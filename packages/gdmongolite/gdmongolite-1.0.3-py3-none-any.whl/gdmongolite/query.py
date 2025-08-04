"""Advanced query builder and cursor for gdmongolite"""

from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime
import asyncio

class QueryBuilder:
    """Build MongoDB queries from Python-style filters"""
    
    @staticmethod
    def build_filter(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python-style filters to MongoDB query"""
        query = {}
        
        for key, value in filters.items():
            if '__' in key:
                field, operator = key.rsplit('__', 1)
                
                # Handle nested field access
                if '.' in field:
                    field_parts = field.split('.')
                    field = '.'.join(field_parts)
                
                # Convert operators
                mongo_op = QueryBuilder._convert_operator(operator, value)
                if mongo_op:
                    if field in query:
                        if isinstance(query[field], dict):
                            query[field].update(mongo_op)
                        else:
                            query[field] = {**{query[field]: query[field]}, **mongo_op}
                    else:
                        query[field] = mongo_op
                else:
                    query[key] = value
            else:
                query[key] = value
        
        return query
    
    @staticmethod
    def _convert_operator(operator: str, value: Any) -> Optional[Dict[str, Any]]:
        """Convert Python operators to MongoDB operators"""
        operators = {
            # Comparison
            'eq': lambda v: v,  # Direct assignment
            'ne': lambda v: {'$ne': v},
            'gt': lambda v: {'$gt': v},
            'gte': lambda v: {'$gte': v},
            'lt': lambda v: {'$lt': v},
            'lte': lambda v: {'$lte': v},
            'in': lambda v: {'$in': v if isinstance(v, (list, tuple)) else [v]},
            'nin': lambda v: {'$nin': v if isinstance(v, (list, tuple)) else [v]},
            
            # String operations
            'contains': lambda v: {'$regex': str(v), '$options': 'i'},
            'icontains': lambda v: {'$regex': str(v), '$options': 'i'},
            'startswith': lambda v: {'$regex': f'^{str(v)}', '$options': 'i'},
            'endswith': lambda v: {'$regex': f'{str(v)}$', '$options': 'i'},
            'regex': lambda v: {'$regex': v},
            'iregex': lambda v: {'$regex': v, '$options': 'i'},
            
            # Existence
            'exists': lambda v: {'$exists': bool(v)},
            'isnull': lambda v: {'$exists': not bool(v)},
            
            # Array operations
            'size': lambda v: {'$size': v},
            'all': lambda v: {'$all': v if isinstance(v, (list, tuple)) else [v]},
            'elemMatch': lambda v: {'$elemMatch': v},
            
            # Type checking
            'type': lambda v: {'$type': v},
        }
        
        if operator in operators:
            result = operators[operator](value)
            return result if isinstance(result, dict) else {'$eq': result}
        
        return None

class Cursor:
    """Advanced cursor with chainable operations"""
    
    def __init__(self, schema_class: Type, filters: Dict[str, Any]):
        self.schema_class = schema_class
        self.filters = filters
        self.query = QueryBuilder.build_filter(filters)
        
        # Cursor options
        self._limit = None
        self._skip = None
        self._sort = None
        self._projection = None
        self._batch_size = 1000
        
        # Execution tracking
        self._executed = False
        self._results = None
    
    def limit(self, count: int) -> 'Cursor':
        """Limit the number of results"""
        self._limit = count
        return self
    
    def skip(self, count: int) -> 'Cursor':
        """Skip a number of results"""
        self._skip = count
        return self
    
    def sort(self, *args, **kwargs) -> 'Cursor':
        """Sort results
        
        Examples:
            .sort('name')  # Ascending
            .sort('-name')  # Descending
            .sort('name', 'age')  # Multiple fields
            .sort(name=1, age=-1)  # MongoDB style
        """
        if args and kwargs:
            raise ValueError("Cannot use both positional and keyword arguments for sort")
        
        if kwargs:
            # MongoDB style: sort(name=1, age=-1)
            self._sort = list(kwargs.items())
        else:
            # Django style: sort('name', '-age')
            sort_list = []
            for field in args:
                if field.startswith('-'):
                    sort_list.append((field[1:], -1))
                else:
                    sort_list.append((field, 1))
            self._sort = sort_list
        
        return self
    
    def project(self, *fields, **kwargs) -> 'Cursor':
        """Project specific fields
        
        Examples:
            .project('name', 'email')  # Include only these fields
            .project(name=1, email=1)  # MongoDB style
            .project(password=0)  # Exclude password
        """
        if fields and kwargs:
            raise ValueError("Cannot use both positional and keyword arguments for projection")
        
        if kwargs:
            self._projection = kwargs
        else:
            self._projection = {field: 1 for field in fields}
        
        return self
    
    def batch_size(self, size: int) -> 'Cursor':
        """Set batch size for cursor iteration"""
        self._batch_size = size
        return self
    
    def _get_cursor(self, force_mode=None):
        """Get the MongoDB cursor"""
        collection = self.schema_class._get_collection(force_mode)
        cursor = collection.find(self.query)
        
        if self._projection:
            cursor = cursor.projection(self._projection)
        if self._sort:
            cursor = cursor.sort(self._sort)
        if self._skip:
            cursor = cursor.skip(self._skip)
        if self._limit:
            cursor = cursor.limit(self._limit)
        if self._batch_size:
            cursor = cursor.batch_size(self._batch_size)
        
        return cursor
    
    async def to_list(self, length: Optional[int] = None) -> List[Dict]:
        """Convert cursor to list (async)"""
        cursor = self._get_cursor("async")
        
        if length:
            return await cursor.to_list(length)
        else:
            return await cursor.to_list(None)
    
    def to_list_sync(self, length: Optional[int] = None) -> List[Dict]:
        """Convert cursor to list (sync)"""
        cursor = self._get_cursor("sync")
        
        results = []
        count = 0
        for doc in cursor:
            if length and count >= length:
                break
            results.append(doc)
            count += 1
        
        return results
    
    async def first(self) -> Optional[Dict]:
        """Get first document (async)"""
        cursor = self._get_cursor("async").limit(1)
        docs = await cursor.to_list(1)
        return docs[0] if docs else None
    
    def first_sync(self) -> Optional[Dict]:
        """Get first document (sync)"""
        cursor = self._get_cursor("sync").limit(1)
        try:
            return next(cursor)
        except StopIteration:
            return None
    
    async def count(self) -> int:
        """Count documents matching the query (async)"""
        collection = self.schema_class._get_collection("async")
        return await collection.count_documents(self.query)
    
    def count_sync(self) -> int:
        """Count documents matching the query (sync)"""
        collection = self.schema_class._get_collection("sync")
        return collection.count_documents(self.query)
    
    async def exists(self) -> bool:
        """Check if any documents match the query (async)"""
        return await self.count() > 0
    
    def exists_sync(self) -> bool:
        """Check if any documents match the query (sync)"""
        return self.count_sync() > 0
    
    async def distinct(self, field: str) -> List[Any]:
        """Get distinct values for a field (async)"""
        collection = self.schema_class._get_collection("async")
        return await collection.distinct(field, self.query)
    
    def distinct_sync(self, field: str) -> List[Any]:
        """Get distinct values for a field (sync)"""
        collection = self.schema_class._get_collection("sync")
        return collection.distinct(field, self.query)
    
    # Iterator support for async
    def __aiter__(self):
        """Async iterator support"""
        self._async_cursor = self._get_cursor("async")
        return self
    
    async def __anext__(self):
        """Async iterator next"""
        try:
            return await self._async_cursor.__anext__()
        except StopAsyncIteration:
            raise StopAsyncIteration
    
    # Iterator support for sync
    def __iter__(self):
        """Sync iterator support"""
        return self._get_cursor("sync")
    
    def __repr__(self):
        return f"Cursor({self.schema_class.__name__}, query={self.query})"

class AggregationPipeline:
    """MongoDB aggregation pipeline builder"""
    
    def __init__(self, schema_class: Type):
        self.schema_class = schema_class
        self.pipeline = []
    
    def match(self, **filters) -> 'AggregationPipeline':
        """Add $match stage"""
        query = QueryBuilder.build_filter(filters)
        self.pipeline.append({'$match': query})
        return self
    
    def group(self, _id: Any, **fields) -> 'AggregationPipeline':
        """Add $group stage"""
        group_stage = {'_id': _id}
        group_stage.update(fields)
        self.pipeline.append({'$group': group_stage})
        return self
    
    def sort(self, **fields) -> 'AggregationPipeline':
        """Add $sort stage"""
        self.pipeline.append({'$sort': fields})
        return self
    
    def limit(self, count: int) -> 'AggregationPipeline':
        """Add $limit stage"""
        self.pipeline.append({'$limit': count})
        return self
    
    def skip(self, count: int) -> 'AggregationPipeline':
        """Add $skip stage"""
        self.pipeline.append({'$skip': count})
        return self
    
    def project(self, **fields) -> 'AggregationPipeline':
        """Add $project stage"""
        self.pipeline.append({'$project': fields})
        return self
    
    def unwind(self, field: str, preserve_null_and_empty: bool = False) -> 'AggregationPipeline':
        """Add $unwind stage"""
        unwind_stage = {'path': f'${field}'}
        if preserve_null_and_empty:
            unwind_stage['preserveNullAndEmptyArrays'] = True
        self.pipeline.append({'$unwind': unwind_stage})
        return self
    
    def lookup(self, from_collection: str, local_field: str, foreign_field: str, as_field: str) -> 'AggregationPipeline':
        """Add $lookup stage"""
        self.pipeline.append({
            '$lookup': {
                'from': from_collection,
                'localField': local_field,
                'foreignField': foreign_field,
                'as': as_field
            }
        })
        return self
    
    def add_stage(self, stage: Dict[str, Any]) -> 'AggregationPipeline':
        """Add custom stage"""
        self.pipeline.append(stage)
        return self
    
    async def execute(self) -> List[Dict]:
        """Execute aggregation pipeline (async)"""
        collection = self.schema_class._get_collection("async")
        cursor = collection.aggregate(self.pipeline)
        return await cursor.to_list(None)
    
    def execute_sync(self) -> List[Dict]:
        """Execute aggregation pipeline (sync)"""
        collection = self.schema_class._get_collection("sync")
        return list(collection.aggregate(self.pipeline))
    
    def __repr__(self):
        return f"AggregationPipeline({self.schema_class.__name__}, stages={len(self.pipeline)})"