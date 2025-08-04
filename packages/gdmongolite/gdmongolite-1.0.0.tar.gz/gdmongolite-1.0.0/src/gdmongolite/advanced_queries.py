"""Advanced query operations for gdmongolite - Joins, Aggregations, and Complex Queries"""

from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime
import asyncio

from .core import Schema
from .exceptions import QueryError


class JoinBuilder:
    """Build MongoDB joins (lookups) with simple syntax"""
    
    def __init__(self, schema: Type[Schema]):
        self.schema = schema
        self.joins = []
        self.pipeline = []
    
    def join(
        self, 
        foreign_schema: Type[Schema], 
        local_field: str, 
        foreign_field: str = "_id",
        as_field: str = None,
        join_type: str = "left"
    ) -> 'JoinBuilder':
        """
        Join with another collection
        
        Args:
            foreign_schema: Schema to join with
            local_field: Field in current collection
            foreign_field: Field in foreign collection (default: _id)
            as_field: Name for joined data (default: foreign collection name)
            join_type: Type of join - left, inner (default: left)
        """
        if not as_field:
            as_field = foreign_schema._collection_name
        
        join_info = {
            "from": foreign_schema._collection_name,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": as_field,
            "type": join_type
        }
        
        self.joins.append(join_info)
        
        # Add lookup stage
        self.pipeline.append({
            "$lookup": {
                "from": join_info["from"],
                "localField": join_info["localField"],
                "foreignField": join_info["foreignField"],
                "as": join_info["as"]
            }
        })
        
        # For inner join, filter out documents without matches
        if join_type == "inner":
            self.pipeline.append({
                "$match": {join_info["as"]: {"$ne": []}}
            })
        
        return self
    
    def join_one(
        self,
        foreign_schema: Type[Schema],
        local_field: str,
        foreign_field: str = "_id",
        as_field: str = None
    ) -> 'JoinBuilder':
        """
        Join with another collection and get single document
        """
        self.join(foreign_schema, local_field, foreign_field, as_field)
        
        # Unwind to get single document instead of array
        as_field = as_field or foreign_schema._collection_name
        self.pipeline.append({
            "$unwind": {
                "path": f"${as_field}",
                "preserveNullAndEmptyArrays": True
            }
        })
        
        return self
    
    def where(self, **filters) -> 'JoinBuilder':
        """Add where conditions"""
        from .query import QueryBuilder
        query = QueryBuilder.build_filter(filters)
        
        self.pipeline.append({"$match": query})
        return self
    
    def select(self, *fields, **field_mappings) -> 'JoinBuilder':
        """Select specific fields"""
        projection = {}
        
        # Add positional fields
        for field in fields:
            projection[field] = 1
        
        # Add field mappings
        projection.update(field_mappings)
        
        if projection:
            self.pipeline.append({"$project": projection})
        
        return self
    
    def sort(self, **sort_fields) -> 'JoinBuilder':
        """Sort results"""
        if sort_fields:
            self.pipeline.append({"$sort": sort_fields})
        return self
    
    def limit(self, count: int) -> 'JoinBuilder':
        """Limit results"""
        self.pipeline.append({"$limit": count})
        return self
    
    def skip(self, count: int) -> 'JoinBuilder':
        """Skip results"""
        self.pipeline.append({"$skip": count})
        return self
    
    async def execute(self) -> List[Dict]:
        """Execute the join query"""
        collection = self.schema._get_collection("async")
        cursor = collection.aggregate(self.pipeline)
        return await cursor.to_list(None)
    
    def execute_sync(self) -> List[Dict]:
        """Execute the join query (sync)"""
        collection = self.schema._get_collection("sync")
        return list(collection.aggregate(self.pipeline))


class AggregationBuilder:
    """Advanced aggregation pipeline builder"""
    
    def __init__(self, schema: Type[Schema]):
        self.schema = schema
        self.pipeline = []
    
    def match(self, **filters) -> 'AggregationBuilder':
        """Filter documents"""
        from .query import QueryBuilder
        query = QueryBuilder.build_filter(filters)
        self.pipeline.append({"$match": query})
        return self
    
    def group(self, _id: Any, **operations) -> 'AggregationBuilder':
        """Group documents"""
        group_stage = {"_id": _id}
        group_stage.update(operations)
        self.pipeline.append({"$group": group_stage})
        return self
    
    def sort(self, **sort_fields) -> 'AggregationBuilder':
        """Sort documents"""
        self.pipeline.append({"$sort": sort_fields})
        return self
    
    def limit(self, count: int) -> 'AggregationBuilder':
        """Limit results"""
        self.pipeline.append({"$limit": count})
        return self
    
    def skip(self, count: int) -> 'AggregationBuilder':
        """Skip results"""
        self.pipeline.append({"$skip": count})
        return self
    
    def project(self, **fields) -> 'AggregationBuilder':
        """Project fields"""
        self.pipeline.append({"$project": fields})
        return self
    
    def unwind(self, field: str, preserve_null: bool = False) -> 'AggregationBuilder':
        """Unwind array field"""
        unwind_stage = {"path": f"${field}"}
        if preserve_null:
            unwind_stage["preserveNullAndEmptyArrays"] = True
        
        self.pipeline.append({"$unwind": unwind_stage})
        return self
    
    def lookup(
        self, 
        from_collection: str, 
        local_field: str, 
        foreign_field: str, 
        as_field: str
    ) -> 'AggregationBuilder':
        """Join with another collection"""
        self.pipeline.append({
            "$lookup": {
                "from": from_collection,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": as_field
            }
        })
        return self
    
    def add_fields(self, **fields) -> 'AggregationBuilder':
        """Add computed fields"""
        self.pipeline.append({"$addFields": fields})
        return self
    
    def facet(self, **facets) -> 'AggregationBuilder':
        """Create multiple aggregation facets"""
        self.pipeline.append({"$facet": facets})
        return self
    
    def bucket(
        self, 
        group_by: str, 
        boundaries: List[Any], 
        default: Any = None,
        output: Dict = None
    ) -> 'AggregationBuilder':
        """Bucket documents"""
        bucket_stage = {
            "groupBy": f"${group_by}",
            "boundaries": boundaries
        }
        
        if default is not None:
            bucket_stage["default"] = default
        
        if output:
            bucket_stage["output"] = output
        
        self.pipeline.append({"$bucket": bucket_stage})
        return self
    
    def bucket_auto(
        self,
        group_by: str,
        buckets: int,
        output: Dict = None,
        granularity: str = None
    ) -> 'AggregationBuilder':
        """Auto bucket documents"""
        bucket_stage = {
            "groupBy": f"${group_by}",
            "buckets": buckets
        }
        
        if output:
            bucket_stage["output"] = output
        
        if granularity:
            bucket_stage["granularity"] = granularity
        
        self.pipeline.append({"$bucketAuto": bucket_stage})
        return self
    
    def sample(self, size: int) -> 'AggregationBuilder':
        """Random sample of documents"""
        self.pipeline.append({"$sample": {"size": size}})
        return self
    
    def count(self, field_name: str = "count") -> 'AggregationBuilder':
        """Count documents"""
        self.pipeline.append({"$count": field_name})
        return self
    
    def replace_root(self, new_root: str) -> 'AggregationBuilder':
        """Replace document root"""
        self.pipeline.append({"$replaceRoot": {"newRoot": f"${new_root}"}})
        return self
    
    def out(self, collection: str) -> 'AggregationBuilder':
        """Output to collection"""
        self.pipeline.append({"$out": collection})
        return self
    
    def merge(self, into: str, **options) -> 'AggregationBuilder':
        """Merge into collection"""
        merge_stage = {"into": into}
        merge_stage.update(options)
        self.pipeline.append({"$merge": merge_stage})
        return self
    
    # Statistical operations
    def stats(self, field: str) -> 'AggregationBuilder':
        """Get statistics for a field"""
        return self.group(
            None,
            count={"$sum": 1},
            min={"$min": f"${field}"},
            max={"$max": f"${field}"},
            avg={"$avg": f"${field}"},
            sum={"$sum": f"${field}"},
            stdDev={"$stdDevPop": f"${field}"}
        )
    
    def percentiles(self, field: str, percentiles: List[float]) -> 'AggregationBuilder':
        """Calculate percentiles"""
        return self.group(
            None,
            percentiles={
                "$percentile": {
                    "input": f"${field}",
                    "p": percentiles,
                    "method": "approximate"
                }
            }
        )
    
    def histogram(self, field: str, buckets: int = 10) -> 'AggregationBuilder':
        """Create histogram"""
        return self.bucket_auto(field, buckets, output={"count": {"$sum": 1}})
    
    # Time series operations
    def date_histogram(
        self, 
        date_field: str, 
        interval: str = "day",
        format: str = None
    ) -> 'AggregationBuilder':
        """Group by date intervals"""
        date_formats = {
            "year": "%Y",
            "month": "%Y-%m", 
            "day": "%Y-%m-%d",
            "hour": "%Y-%m-%d %H:00",
            "minute": "%Y-%m-%d %H:%M"
        }
        
        date_format = format or date_formats.get(interval, "%Y-%m-%d")
        
        return self.group(
            {"$dateToString": {"format": date_format, "date": f"${date_field}"}},
            count={"$sum": 1},
            date={"$first": f"${date_field}"}
        ).sort(date=1)
    
    def moving_average(
        self, 
        field: str, 
        window: int,
        sort_field: str = None
    ) -> 'AggregationBuilder':
        """Calculate moving average"""
        if sort_field:
            self.sort(**{sort_field: 1})
        
        return self.add_fields(**{
            f"{field}_moving_avg": {
                "$avg": {
                    "$slice": [
                        {"$map": {
                            "input": {"$range": [0, window]},
                            "as": "i",
                            "in": f"${field}"
                        }},
                        f"-{window}",
                        window
                    ]
                }
            }
        })
    
    # Text search operations
    def text_search(self, query: str, language: str = None) -> 'AggregationBuilder':
        """Full text search"""
        search_stage = {"$text": {"$search": query}}
        if language:
            search_stage["$text"]["$language"] = language
        
        self.pipeline.insert(0, {"$match": search_stage})
        
        # Add text score
        return self.add_fields(textScore={"$meta": "textScore"}).sort(textScore=-1)
    
    def regex_search(self, field: str, pattern: str, options: str = "i") -> 'AggregationBuilder':
        """Regex search"""
        return self.match(**{field: {"$regex": pattern, "$options": options}})
    
    # Geospatial operations
    def geo_near(
        self,
        near: Dict,
        distance_field: str = "distance",
        max_distance: float = None,
        min_distance: float = None,
        spherical: bool = True
    ) -> 'AggregationBuilder':
        """Geospatial near query"""
        geo_near_stage = {
            "near": near,
            "distanceField": distance_field,
            "spherical": spherical
        }
        
        if max_distance:
            geo_near_stage["maxDistance"] = max_distance
        
        if min_distance:
            geo_near_stage["minDistance"] = min_distance
        
        # $geoNear must be first stage
        self.pipeline.insert(0, {"$geoNear": geo_near_stage})
        return self
    
    def geo_within(self, field: str, geometry: Dict) -> 'AggregationBuilder':
        """Find documents within geometry"""
        return self.match(**{
            field: {
                "$geoWithin": {
                    "$geometry": geometry
                }
            }
        })
    
    async def execute(self) -> List[Dict]:
        """Execute aggregation pipeline"""
        collection = self.schema._get_collection("async")
        cursor = collection.aggregate(self.pipeline)
        return await cursor.to_list(None)
    
    def execute_sync(self) -> List[Dict]:
        """Execute aggregation pipeline (sync)"""
        collection = self.schema._get_collection("sync")
        return list(collection.aggregate(self.pipeline))
    
    def explain(self) -> Dict:
        """Get execution plan"""
        collection = self.schema._get_collection("sync")
        return collection.aggregate(self.pipeline, explain=True)


class QueryAnalyzer:
    """Analyze and optimize queries"""
    
    def __init__(self, schema: Type[Schema]):
        self.schema = schema
    
    async def explain_query(self, **filters) -> Dict:
        """Explain query execution"""
        from .query import QueryBuilder
        query = QueryBuilder.build_filter(filters)
        
        collection = self.schema._get_collection("async")
        cursor = collection.find(query)
        
        return await cursor.explain()
    
    async def get_indexes(self) -> List[Dict]:
        """Get collection indexes"""
        collection = self.schema._get_collection("async")
        indexes = []
        
        async for index in collection.list_indexes():
            indexes.append(index)
        
        return indexes
    
    async def suggest_indexes(self, queries: List[Dict]) -> List[Dict]:
        """Suggest indexes for common queries"""
        suggestions = []
        
        for query in queries:
            # Analyze query fields
            fields = self._extract_query_fields(query)
            
            if len(fields) == 1:
                # Single field index
                suggestions.append({
                    "type": "single",
                    "fields": {fields[0]: 1},
                    "query": query
                })
            elif len(fields) > 1:
                # Compound index
                suggestions.append({
                    "type": "compound", 
                    "fields": {field: 1 for field in fields},
                    "query": query
                })
        
        return suggestions
    
    def _extract_query_fields(self, query: Dict) -> List[str]:
        """Extract fields from query"""
        fields = []
        
        for key, value in query.items():
            if key.startswith('$'):
                continue
            
            # Handle nested field names (field__operator)
            field_name = key.split('__')[0]
            if field_name not in fields:
                fields.append(field_name)
        
        return fields
    
    async def profile_queries(self, duration_seconds: int = 60) -> List[Dict]:
        """Profile slow queries"""
        # This would require MongoDB profiling to be enabled
        # For now, return empty list
        return []


# Add methods to Schema class for advanced queries
def add_advanced_query_methods():
    """Add advanced query methods to Schema class"""
    
    @classmethod
    def join(cls, foreign_schema: Type[Schema], local_field: str, foreign_field: str = "_id", as_field: str = None):
        """Start a join query"""
        return JoinBuilder(cls).join(foreign_schema, local_field, foreign_field, as_field)
    
    @classmethod
    def aggregate(cls):
        """Start an aggregation pipeline"""
        return AggregationBuilder(cls)
    
    @classmethod
    def analyze(cls):
        """Get query analyzer"""
        return QueryAnalyzer(cls)
    
    # Add methods to Schema class
    Schema.join = join
    Schema.aggregate = aggregate
    Schema.analyze = analyze


# Initialize advanced query methods
add_advanced_query_methods()


# Utility functions for common aggregations
class CommonAggregations:
    """Common aggregation patterns"""
    
    @staticmethod
    def sales_by_period(
        schema: Type[Schema],
        date_field: str = "created_at",
        amount_field: str = "amount",
        period: str = "day"
    ) -> AggregationBuilder:
        """Sales aggregation by time period"""
        return (schema.aggregate()
                .date_histogram(date_field, period)
                .add_fields(total_sales={"$sum": f"${amount_field}"}))
    
    @staticmethod
    def top_customers(
        schema: Type[Schema],
        customer_field: str = "customer_id",
        amount_field: str = "amount",
        limit: int = 10
    ) -> AggregationBuilder:
        """Top customers by total amount"""
        return (schema.aggregate()
                .group(f"${customer_field}", 
                       total={"$sum": f"${amount_field}"},
                       count={"$sum": 1})
                .sort(total=-1)
                .limit(limit))
    
    @staticmethod
    def category_stats(
        schema: Type[Schema],
        category_field: str = "category",
        value_field: str = "value"
    ) -> AggregationBuilder:
        """Statistics by category"""
        return (schema.aggregate()
                .group(f"${category_field}",
                       count={"$sum": 1},
                       total={"$sum": f"${value_field}"},
                       avg={"$avg": f"${value_field}"},
                       min={"$min": f"${value_field}"},
                       max={"$max": f"${value_field}"}))
    
    @staticmethod
    def user_activity_summary(
        schema: Type[Schema],
        user_field: str = "user_id",
        date_field: str = "created_at"
    ) -> AggregationBuilder:
        """User activity summary"""
        return (schema.aggregate()
                .group(f"${user_field}",
                       total_actions={"$sum": 1},
                       first_action={"$min": f"${date_field}"},
                       last_action={"$max": f"${date_field}"},
                       unique_days={"$addToSet": {
                           "$dateToString": {
                               "format": "%Y-%m-%d",
                               "date": f"${date_field}"
                           }
                       }})
                .add_fields(
                    active_days={"$size": "$unique_days"},
                    days_since_first={"$divide": [
                        {"$subtract": ["$last_action", "$first_action"]},
                        86400000  # milliseconds in a day
                    ]}
                ))


# Export everything
__all__ = [
    "JoinBuilder",
    "AggregationBuilder", 
    "QueryAnalyzer",
    "CommonAggregations",
    "add_advanced_query_methods"
]