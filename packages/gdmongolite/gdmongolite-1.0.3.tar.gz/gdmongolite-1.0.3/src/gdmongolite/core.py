"""Core gdmongolite implementation - The world's easiest MongoDB toolkit"""

import os
import asyncio
import inspect
from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime
from contextlib import asynccontextmanager

import motor.motor_asyncio
import pymongo
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError as PydanticValidationError
try:
    from bson import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId

from .exceptions import GDMongoError, ValidationError, ConnectionError, QueryError
from .query import QueryBuilder, Cursor

# Load environment variables
load_dotenv()

class QueryResponse:
    """Standardized response for all database operations"""
    
    def __init__(self, success: bool = True, data: Any = None, count: int = 0, 
                 message: str = "", error: str = None, duration: float = 0):
        self.success = success
        self.data = data
        self.count = count
        self.message = message
        self.error = error
        self.duration = duration
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "count": self.count,
            "message": self.message,
            "error": self.error,
            "duration": self.duration
        }
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "ERROR"
        return f"QueryResponse({status} {self.message}, count={self.count})"

class DB:
    """The main DB facade - automatically detects sync/async context"""
    
    _instances = {}
    _default_config = {
        "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "database": os.getenv("MONGO_DB", "gdmongo"),
        "max_pool_size": int(os.getenv("MONGO_MAX_POOL", "50")),
        "min_pool_size": int(os.getenv("MONGO_MIN_POOL", "5")),
        "timeout_ms": int(os.getenv("MONGO_TIMEOUT_MS", "30000"))
    }
    
    def __init__(self, uri: str = None, database: str = None, mode: str = "auto"):
        """Initialize DB connection
        
        Args:
            uri: MongoDB connection string (defaults to MONGO_URI env var)
            database: Database name (defaults to MONGO_DB env var)
            mode: 'auto', 'sync', or 'async' (auto-detects by default)
        """
        self.uri = uri or self._default_config["uri"]
        self.database_name = database or self._default_config["database"]
        self.mode = mode
        
        # Connection objects
        self._async_client = None
        self._sync_client = None
        self._async_db = None
        self._sync_db = None
        
        # Schema registry
        self._schemas: Dict[str, Type['Schema']] = {}
    
    def _init_async(self):
        """Initialize async MongoDB connection"""
        try:
            self._async_client = motor.motor_asyncio.AsyncIOMotorClient(
                self.uri,
                maxPoolSize=self._default_config["max_pool_size"],
                minPoolSize=self._default_config["min_pool_size"],
                serverSelectionTimeoutMS=self._default_config["timeout_ms"]
            )
            self._async_db = self._async_client[self.database_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB (async): {e}")
    
    def _init_sync(self):
        """Initialize sync MongoDB connection"""
        try:
            self._sync_client = pymongo.MongoClient(
                self.uri,
                maxPoolSize=self._default_config["max_pool_size"],
                minPoolSize=self._default_config["min_pool_size"],
                serverSelectionTimeoutMS=self._default_config["timeout_ms"]
            )
            self._sync_db = self._sync_client[self.database_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB (sync): {e}")
    
    def _detect_context(self):
        """Auto-detect if we're in async or sync context"""
        if self.mode != "auto":
            return self.mode
        
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            return "async"
        except RuntimeError:
            return "sync"
    
    def _get_db(self, force_mode=None):
        """Get the appropriate database connection"""
        mode = force_mode or self._detect_context()
        
        if mode == "async":
            if self._async_db is None:
                self._init_async()
            return self._async_db
        else:
            if self._sync_db is None:
                self._init_sync()
            return self._sync_db
    
    def __getattr__(self, name: str):
        """Dynamic access to schemas: db.User -> User schema class"""
        if name in self._schemas:
            return self._schemas[name]
        
        # Return collection for direct access
        db = self._get_db()
        return db[name.lower()]
    
    def register_schema(self, schema_class: Type['Schema']):
        """Register a schema class with the DB"""
        self._schemas[schema_class.__name__] = schema_class
        schema_class._db = self
    
    async def close(self):
        """Close async connections"""
        if self._async_client is not None:
            self._async_client.close()
    
    def close_sync(self):
        """Close sync connections"""
        if self._sync_client is not None:
            self._sync_client.close()

class Schema(BaseModel):
    """Base schema class with automatic CRUD operations"""
    
    _db: Optional[DB] = None
    _collection_name: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # Auto-generate collection name from class name
        if hasattr(cls, '__name__') and cls.__name__:
            cls._collection_name = cls._to_snake_case(cls.__name__)
        else:
            cls._collection_name = 'documents'
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case"""
        if not name:
            return 'documents'
        
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()
    
    @classmethod
    def _get_collection(cls, force_mode=None):
        """Get the MongoDB collection for this schema"""
        if not cls._db:
            raise GDMongoError(f"Schema {cls.__name__} not registered with a DB instance")
        
        db = cls._db._get_db(force_mode)
        return db[cls._collection_name]
    
    @classmethod
    def _create_response(cls, success=True, data=None, count=0, message="", error=None, duration=0):
        """Create standardized response"""
        return QueryResponse(success, data, count, message, error, duration)
    
    # ASYNC CRUD OPERATIONS
    @classmethod
    async def insert(cls, data: Union[Dict, List[Dict], 'Schema', List['Schema']]) -> QueryResponse:
        """Insert one or many documents"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("async")
            
            # Handle different input types
            if isinstance(data, (list, tuple)):
                # Multiple documents
                docs = []
                for item in data:
                    if isinstance(item, cls):
                        docs.append(item.dict())
                    elif isinstance(item, dict):
                        # Validate with Pydantic
                        validated = cls(**item)
                        docs.append(validated.dict())
                    else:
                        raise ValidationError(f"Invalid data type: {type(item)}")
                
                result = await collection.insert_many(docs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return cls._create_response(
                    success=True,
                    data=result.inserted_ids,
                    count=len(result.inserted_ids),
                    message=f"Inserted {len(result.inserted_ids)} documents",
                    duration=duration
                )
            else:
                # Single document
                if isinstance(data, cls):
                    doc = data.dict()
                elif isinstance(data, dict):
                    validated = cls(**data)
                    doc = validated.dict()
                else:
                    raise ValidationError(f"Invalid data type: {type(data)}")
                
                result = await collection.insert_one(doc)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return cls._create_response(
                    success=True,
                    data=result.inserted_id,
                    count=1,
                    message="Document inserted successfully",
                    duration=duration
                )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Insert operation failed",
                duration=duration
            )
    
    @classmethod
    def find(cls, **filters) -> 'Cursor':
        """Find documents with advanced filtering"""
        return Cursor(cls, filters)
    
    @classmethod
    async def update(cls, filter_dict: Dict, update_dict: Dict, upsert: bool = False) -> QueryResponse:
        """Update documents"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("async")
            
            # Ensure update operators
            if not any(key.startswith('$') for key in update_dict.keys()):
                update_dict = {'$set': update_dict}
            
            result = await collection.update_many(filter_dict, update_dict, upsert=upsert)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return cls._create_response(
                success=True,
                data={
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": result.upserted_id
                },
                count=result.modified_count,
                message=f"Updated {result.modified_count} documents",
                duration=duration
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Update operation failed",
                duration=duration
            )
    
    @classmethod
    async def delete(cls, **filters) -> QueryResponse:
        """Delete documents"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("async")
            query = QueryBuilder.build_filter(filters)
            
            result = await collection.delete_many(query)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return cls._create_response(
                success=True,
                data={"deleted_count": result.deleted_count},
                count=result.deleted_count,
                message=f"Deleted {result.deleted_count} documents",
                duration=duration
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Delete operation failed",
                duration=duration
            )
    
    # SYNC CRUD OPERATIONS
    @classmethod
    def insert_sync(cls, data: Union[Dict, List[Dict], 'Schema', List['Schema']]) -> QueryResponse:
        """Sync version of insert"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("sync")
            
            if isinstance(data, (list, tuple)):
                docs = []
                for item in data:
                    if isinstance(item, cls):
                        docs.append(item.dict())
                    elif isinstance(item, dict):
                        validated = cls(**item)
                        docs.append(validated.dict())
                    else:
                        raise ValidationError(f"Invalid data type: {type(item)}")
                
                result = collection.insert_many(docs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return cls._create_response(
                    success=True,
                    data=result.inserted_ids,
                    count=len(result.inserted_ids),
                    message=f"Inserted {len(result.inserted_ids)} documents",
                    duration=duration
                )
            else:
                if isinstance(data, cls):
                    doc = data.dict()
                elif isinstance(data, dict):
                    validated = cls(**data)
                    doc = validated.dict()
                else:
                    raise ValidationError(f"Invalid data type: {type(data)}")
                
                result = collection.insert_one(doc)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                return cls._create_response(
                    success=True,
                    data=result.inserted_id,
                    count=1,
                    message="Document inserted successfully",
                    duration=duration
                )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Insert operation failed",
                duration=duration
            )
    
    @classmethod
    def update_sync(cls, filter_dict: Dict, update_dict: Dict, upsert: bool = False) -> QueryResponse:
        """Sync version of update"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("sync")
            
            if not any(key.startswith('$') for key in update_dict.keys()):
                update_dict = {'$set': update_dict}
            
            result = collection.update_many(filter_dict, update_dict, upsert=upsert)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return cls._create_response(
                success=True,
                data={
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": getattr(result, 'upserted_id', None)
                },
                count=result.modified_count,
                message=f"Updated {result.modified_count} documents",
                duration=duration
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Update operation failed",
                duration=duration
            )
    
    @classmethod
    def delete_sync(cls, **filters) -> QueryResponse:
        """Sync version of delete"""
        start_time = datetime.now()
        
        try:
            collection = cls._get_collection("sync")
            query = QueryBuilder.build_filter(filters)
            
            result = collection.delete_many(query)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return cls._create_response(
                success=True,
                data={"deleted_count": result.deleted_count},
                count=result.deleted_count,
                message=f"Deleted {result.deleted_count} documents",
                duration=duration
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return cls._create_response(
                success=False,
                error=str(e),
                message="Delete operation failed",
                duration=duration
            )