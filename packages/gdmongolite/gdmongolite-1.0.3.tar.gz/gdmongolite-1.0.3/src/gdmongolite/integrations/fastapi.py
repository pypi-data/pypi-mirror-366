"""FastAPI integration for gdmongolite - World's easiest MongoDB + FastAPI combo"""

from typing import Dict, List, Any, Optional, Type, Union
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core import DB, Schema, QueryResponse
from ..exceptions import GDMongoError


class FastAPIIntegration:
    """Seamless FastAPI integration for gdmongolite schemas"""
    
    def __init__(self, db: DB, app: FastAPI = None):
        self.db = db
        self.app = app or FastAPI(title="gdmongolite API", version="1.0.0")
        self._setup_middleware()
        self._setup_error_handlers()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        @self.app.exception_handler(GDMongoError)
        async def gdmongo_error_handler(request, exc):
            return JSONResponse(
                status_code=400,
                content={"error": str(exc), "type": "GDMongoError"}
            )
        
        @self.app.exception_handler(Exception)
        async def general_error_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": str(exc)}
            )
    
    def add_crud_routes(self, schema: Type[Schema], prefix: str = None):
        """Auto-generate CRUD routes for a schema"""
        if not prefix:
            prefix = f"/{schema._collection_name}"
        
        # Response models
        class ItemResponse(BaseModel):
            success: bool = True
            data: Any = None
            count: int = 0
            message: str = ""
        
        class ListResponse(BaseModel):
            success: bool = True
            data: List[Dict] = []
            count: int = 0
            total: int = 0
            page: int = 1
            per_page: int = 10
        
        # CREATE - POST /items
        @self.app.post(f"{prefix}/", response_model=ItemResponse)
        async def create_item(item: Union[schema, Dict] = Body(...)):
            """Create a new item"""
            try:
                if isinstance(item, dict):
                    response = await schema.insert(item)
                else:
                    response = await schema.insert(item.dict())
                
                return ItemResponse(
                    success=response.success,
                    data=str(response.data),
                    count=response.count,
                    message=response.message
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # CREATE MANY - POST /items/bulk
        @self.app.post(f"{prefix}/bulk", response_model=ItemResponse)
        async def create_items(items: List[Union[schema, Dict]] = Body(...)):
            """Create multiple items"""
            try:
                data = [item.dict() if hasattr(item, 'dict') else item for item in items]
                response = await schema.insert(data)
                
                return ItemResponse(
                    success=response.success,
                    data=[str(id) for id in response.data],
                    count=response.count,
                    message=response.message
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # READ ALL - GET /items
        @self.app.get(f"{prefix}/", response_model=ListResponse)
        async def get_items(
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100),
            sort: str = Query(None),
            **filters
        ):
            """Get items with pagination and filtering"""
            try:
                # Remove pagination params from filters
                filters.pop('page', None)
                filters.pop('per_page', None)
                filters.pop('sort', None)
                
                cursor = schema.find(**filters)
                
                # Apply sorting
                if sort:
                    if sort.startswith('-'):
                        cursor = cursor.sort(**{sort[1:]: -1})
                    else:
                        cursor = cursor.sort(**{sort: 1})
                
                # Get total count
                total = await cursor.count()
                
                # Apply pagination
                skip = (page - 1) * per_page
                items = await cursor.skip(skip).limit(per_page).to_list()
                
                return ListResponse(
                    success=True,
                    data=items,
                    count=len(items),
                    total=total,
                    page=page,
                    per_page=per_page
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # READ ONE - GET /items/{id}
        @self.app.get(f"{prefix}/{{item_id}}", response_model=ItemResponse)
        async def get_item(item_id: str = Path(...)):
            """Get a single item by ID"""
            try:
                from bson import ObjectId
                cursor = schema.find(_id=ObjectId(item_id))
                item = await cursor.first()
                
                if not item:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                return ItemResponse(
                    success=True,
                    data=item,
                    count=1,
                    message="Item found"
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # UPDATE - PUT /items/{id}
        @self.app.put(f"{prefix}/{{item_id}}", response_model=ItemResponse)
        async def update_item(
            item_id: str = Path(...),
            update_data: Dict = Body(...)
        ):
            """Update an item by ID"""
            try:
                from bson import ObjectId
                response = await schema.update(
                    {"_id": ObjectId(item_id)},
                    update_data
                )
                
                if response.count == 0:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                return ItemResponse(
                    success=response.success,
                    data=response.data,
                    count=response.count,
                    message=response.message
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # DELETE - DELETE /items/{id}
        @self.app.delete(f"{prefix}/{{item_id}}", response_model=ItemResponse)
        async def delete_item(item_id: str = Path(...)):
            """Delete an item by ID"""
            try:
                from bson import ObjectId
                response = await schema.delete(_id=ObjectId(item_id))
                
                if response.count == 0:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                return ItemResponse(
                    success=response.success,
                    data=response.data,
                    count=response.count,
                    message=response.message
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # SEARCH - POST /items/search
        @self.app.post(f"{prefix}/search", response_model=ListResponse)
        async def search_items(
            query: Dict = Body(...),
            page: int = Body(1),
            per_page: int = Body(10),
            sort: Dict = Body(None)
        ):
            """Advanced search with complex queries"""
            try:
                cursor = schema.find(**query)
                
                if sort:
                    cursor = cursor.sort(**sort)
                
                total = await cursor.count()
                skip = (page - 1) * per_page
                items = await cursor.skip(skip).limit(per_page).to_list()
                
                return ListResponse(
                    success=True,
                    data=items,
                    count=len(items),
                    total=total,
                    page=page,
                    per_page=per_page
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
    
    def add_health_check(self):
        """Add health check endpoint"""
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                # Test database connection
                db_instance = self.db._get_db("async")
                await db_instance.command("ping")
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": "connected",
                    "schemas": list(self.db._schemas.keys())
                }
            except Exception as e:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
    
    def add_schema_info(self):
        """Add schema information endpoint"""
        @self.app.get("/schemas")
        async def get_schemas():
            """Get information about all registered schemas"""
            schemas_info = {}
            
            for name, schema_class in self.db._schemas.items():
                schemas_info[name] = {
                    "collection_name": schema_class._collection_name,
                    "fields": list(schema_class.__fields__.keys()),
                    "field_types": {
                        field: str(field_info.type_)
                        for field, field_info in schema_class.__fields__.items()
                    }
                }
            
            return {
                "schemas": schemas_info,
                "total_schemas": len(schemas_info)
            }
    
    def add_stats_endpoint(self):
        """Add database statistics endpoint"""
        @self.app.get("/stats")
        async def get_stats():
            """Get database and collection statistics"""
            try:
                db_instance = self.db._get_db("async")
                stats = {}
                
                # Database stats
                db_stats = await db_instance.command("dbStats")
                stats["database"] = {
                    "collections": db_stats.get("collections", 0),
                    "objects": db_stats.get("objects", 0),
                    "dataSize": db_stats.get("dataSize", 0),
                    "storageSize": db_stats.get("storageSize", 0)
                }
                
                # Collection stats
                stats["collections"] = {}
                for name, schema_class in self.db._schemas.items():
                    try:
                        coll_stats = await db_instance.command("collStats", schema_class._collection_name)
                        stats["collections"][schema_class._collection_name] = {
                            "count": coll_stats.get("count", 0),
                            "size": coll_stats.get("size", 0),
                            "avgObjSize": coll_stats.get("avgObjSize", 0),
                            "indexes": coll_stats.get("nindexes", 0)
                        }
                    except:
                        stats["collections"][schema_class._collection_name] = {"count": 0}
                
                return stats
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


def create_fastapi_app(db: DB, schemas: List[Type[Schema]] = None, **kwargs) -> FastAPI:
    """Create a FastAPI app with auto-generated CRUD routes"""
    
    app_config = {
        "title": "gdmongolite API",
        "description": "Auto-generated API using gdmongolite - The World's Easiest MongoDB Toolkit",
        "version": "1.0.0",
        **kwargs
    }
    
    app = FastAPI(**app_config)
    integration = FastAPIIntegration(db, app)
    
    # Add utility endpoints
    integration.add_health_check()
    integration.add_schema_info()
    integration.add_stats_endpoint()
    
    # Add CRUD routes for schemas
    if schemas:
        for schema in schemas:
            integration.add_crud_routes(schema)
    else:
        # Add routes for all registered schemas
        for schema in db._schemas.values():
            integration.add_crud_routes(schema)
    
    return app


class FastAPIRouter:
    """Advanced router for custom endpoints"""
    
    def __init__(self, db: DB):
        self.db = db
    
    def create_custom_endpoint(self, schema: Type[Schema], endpoint_name: str, query_func):
        """Create custom endpoint with complex query logic"""
        def endpoint():
            async def custom_endpoint(**kwargs):
                try:
                    result = await query_func(schema, **kwargs)
                    return {"success": True, "data": result}
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
            return custom_endpoint
        
        return endpoint()
    
    def create_aggregation_endpoint(self, schema: Type[Schema], pipeline: List[Dict]):
        """Create endpoint for aggregation pipeline"""
        async def aggregation_endpoint():
            try:
                from ..query import AggregationPipeline
                agg = AggregationPipeline(schema)
                
                for stage in pipeline:
                    agg.add_stage(stage)
                
                result = await agg.execute()
                return {"success": True, "data": result, "count": len(result)}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        return aggregation_endpoint


# Utility decorators for FastAPI routes
def with_db_session(db: DB):
    """Dependency to inject database session"""
    async def get_db_session():
        return db
    return Depends(get_db_session)


def with_pagination():
    """Dependency for pagination parameters"""
    def get_pagination(
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(10, ge=1, le=100, description="Items per page")
    ):
        return {"page": page, "per_page": per_page, "skip": (page - 1) * per_page}
    
    return Depends(get_pagination)


def with_sorting():
    """Dependency for sorting parameters"""
    def get_sorting(
        sort_by: str = Query(None, description="Field to sort by"),
        sort_order: int = Query(1, description="Sort order: 1 for asc, -1 for desc")
    ):
        if sort_by:
            return {sort_by: sort_order}
        return None
    
    return Depends(get_sorting)