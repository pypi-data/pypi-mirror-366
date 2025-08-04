"""Custom exceptions for gdmongolite"""

class GDMongoError(Exception):
    """Base exception for all gdmongolite errors"""
    pass

class ValidationError(GDMongoError):
    """Raised when data validation fails"""
    pass

class ConnectionError(GDMongoError):
    """Raised when database connection fails"""
    pass

class MigrationError(GDMongoError):
    """Raised when migration operations fail"""
    pass

class QueryError(GDMongoError):
    """Raised when query operations fail"""
    pass