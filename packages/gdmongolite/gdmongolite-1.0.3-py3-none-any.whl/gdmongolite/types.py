"""Enhanced types for gdmongolite with better validation"""

from datetime import datetime
from typing import Annotated, Any
from pydantic import EmailStr, Field
try:
    from bson import ObjectId as BSONObjectId
except ImportError:
    from pymongo.objectid import ObjectId as BSONObjectId

# Email type with validation
Email = EmailStr

# Positive integer with validation
Positive = Annotated[int, Field(gt=0, description="Must be a positive integer")]

# MongoDB ObjectId type
class ObjectId(str):
    """MongoDB ObjectId that validates and converts automatically"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, BSONObjectId):
            return str(v)
        if isinstance(v, str):
            try:
                BSONObjectId(v)
                return v
            except:
                raise ValueError("Invalid ObjectId format")
        raise ValueError("ObjectId must be a string or ObjectId")

# DateTime with automatic parsing
DateTime = Annotated[datetime, Field(description="ISO datetime string or datetime object")]

# Common field types for easy use
class FieldTypes:
    """Pre-configured field types for common use cases"""
    
    # String fields
    Name = Annotated[str, Field(min_length=1, max_length=100)]
    Username = Annotated[str, Field(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')]
    Password = Annotated[str, Field(min_length=8, max_length=128)]
    
    # Numeric fields
    Age = Annotated[int, Field(ge=0, le=150)]
    Price = Annotated[float, Field(ge=0)]
    Rating = Annotated[float, Field(ge=0, le=5)]
    
    # Text fields
    Title = Annotated[str, Field(min_length=1, max_length=200)]
    Description = Annotated[str, Field(max_length=1000)]
    Content = Annotated[str, Field(max_length=10000)]
    
    # URL and identifiers
    URL = Annotated[str, Field(pattern=r'^https?://')]
    Phone = Annotated[str, Field(pattern=r'^\+?[\d\s\-\(\)]+$')]

# Export commonly used types
__all__ = [
    "Email", "Positive", "ObjectId", "DateTime", "FieldTypes"
]