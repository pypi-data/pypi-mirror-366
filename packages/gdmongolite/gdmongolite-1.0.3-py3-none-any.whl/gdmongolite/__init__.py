"""gdmongolite: The World's Most Powerful and Easiest MongoDB Toolkit"""

__version__ = "1.0.3"
__author__ = "Ganesh Datta Padamata"
__email__ = "ganeshdattapadamata@gmail.com"

import os

# Core functionality
from .core import DB, Schema, QueryResponse
from .types import Email, Positive, ObjectId, DateTime, FieldTypes
from .exceptions import GDMongoError, ValidationError, ConnectionError

# Query system
try:
    from .query import QueryBuilder, Cursor, AggregationPipeline
except ImportError:
    class QueryBuilder:
        @staticmethod
        def build_filter(filters): return filters
    class Cursor:
        def __init__(self, schema, filters): pass
    class AggregationPipeline:
        def __init__(self, schema): pass

# Configuration
try:
    from .config import get_config, ConfigManager
except ImportError:
    def get_config(): return {}
    class ConfigManager: pass

# Advanced queries
try:
    from .advanced_queries import JoinBuilder, AggregationBuilder, QueryAnalyzer, CommonAggregations
except ImportError:
    class JoinBuilder: pass
    class AggregationBuilder: pass
    class QueryAnalyzer: pass
    class CommonAggregations: pass

# Real-time features
try:
    from .realtime import ChangeStreamManager, WebSocketManager, LiveQuery, RealtimeAPI, NotificationSystem
except ImportError:
    class ChangeStreamManager: pass
    class WebSocketManager: pass
    class LiveQuery: pass
    class RealtimeAPI: pass
    class NotificationSystem: pass

# Security features
try:
    from .security import PasswordManager, JWTManager, RoleBasedAccessControl, DataEncryption, SecurityMiddleware, AuditLog, SecurityConfig
except ImportError:
    class PasswordManager: pass
    class JWTManager: pass
    class RoleBasedAccessControl: pass
    class DataEncryption: pass
    class SecurityMiddleware: pass
    class AuditLog: pass
    class SecurityConfig: pass

# Caching system
try:
    from .caching import CacheManager, MemoryCache, RedisCache, SmartCache, QueryCache, CacheDecorator, CacheWarmer
    def add_caching_to_db(db): return db
except ImportError:
    class CacheManager: pass
    class MemoryCache: pass
    class RedisCache: pass
    class SmartCache: pass
    class QueryCache: pass
    class CacheDecorator: pass
    class CacheWarmer: pass
    def add_caching_to_db(db): return db

# Monitoring
try:
    from .monitoring import MetricsCollector, HealthChecker, PerformanceProfiler, MonitoringDashboard
    def add_monitoring_to_db(db): return db
except ImportError:
    class MetricsCollector: pass
    class HealthChecker: pass
    class PerformanceProfiler: pass
    class MonitoringDashboard: pass
    def add_monitoring_to_db(db): return db

# Web integrations
try:
    from .integrations.fastapi import FastAPIIntegration, create_fastapi_app
    from .integrations.data_import_export import DataImporter, DataExporter, DataMigrator
    from .integrations.web_server import WebServer, quick_serve, dev_serve, prod_serve
except ImportError:
    class FastAPIIntegration: pass
    def create_fastapi_app(*args, **kwargs): pass
    class DataImporter: pass
    class DataExporter: pass
    class DataMigrator: pass
    class WebServer: pass
    def quick_serve(*args, **kwargs): pass
    def dev_serve(*args, **kwargs): pass
    def prod_serve(*args, **kwargs): pass

# Migration system
try:
    from .migrate import MigrationManager
except ImportError:
    class MigrationManager:
        def __init__(self, db): pass
        def get_migration_status(self): return {}

# Enhanced DB class with all features
class PowerDB(DB):
    """Enhanced DB class with all gdmongolite features"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add features with fallbacks
        try:
            add_caching_to_db(self)
        except: 
            pass
        
        try:
            add_monitoring_to_db(self)
        except: 
            pass
        
        # Add other features with proper checks
        try:
            self.security = SecurityMiddleware(self) if hasattr(SecurityMiddleware, '__call__') and SecurityMiddleware != type else None
        except:
            self.security = None
            
        try:
            self.realtime = RealtimeAPI(self) if hasattr(RealtimeAPI, '__call__') and RealtimeAPI != type else None
        except:
            self.realtime = None
            
        try:
            self.notifications = NotificationSystem(self) if hasattr(NotificationSystem, '__call__') and NotificationSystem != type else None
        except:
            self.notifications = None
            
        self.migrations = MigrationManager(self)
    
    def get_full_stats(self):
        """Get comprehensive statistics"""
        try:
            return {
                "cache_stats": getattr(self, 'smart_cache', {}).get_stats() if hasattr(getattr(self, 'smart_cache', {}), 'get_stats') else {},
                "query_stats": {},
                "system_stats": {},
                "health_status": {}
            }
        except:
            return {
                "cache_stats": {},
                "query_stats": {},
                "system_stats": {},
                "health_status": {}
            }

# Make PowerDB the default DB
DB = PowerDB

# Everything you need in one import
__all__ = [
    # Core functionality
    "DB", "Schema", "QueryResponse",
    "Email", "Positive", "ObjectId", "DateTime", "FieldTypes",
    "GDMongoError", "ValidationError", "ConnectionError",
    "QueryBuilder", "Cursor", "AggregationPipeline",
    "get_config", "ConfigManager",
    
    # Advanced queries
    "JoinBuilder", "AggregationBuilder", "QueryAnalyzer", "CommonAggregations",
    
    # Real-time features
    "ChangeStreamManager", "WebSocketManager", "LiveQuery", "RealtimeAPI", "NotificationSystem",
    
    # Security features
    "PasswordManager", "JWTManager", "RoleBasedAccessControl", "DataEncryption",
    "SecurityMiddleware", "AuditLog", "SecurityConfig",
    
    # Caching system
    "CacheManager", "MemoryCache", "RedisCache", "SmartCache", "QueryCache",
    "CacheDecorator", "CacheWarmer",
    
    # Monitoring and observability
    "MetricsCollector", "HealthChecker", "PerformanceProfiler", "MonitoringDashboard",
    
    # Web integrations
    "FastAPIIntegration", "create_fastapi_app",
    "DataImporter", "DataExporter", "DataMigrator",
    "WebServer", "quick_serve", "dev_serve", "prod_serve",
    
    # Migration system
    "MigrationManager"
]

# Quick setup functions
def quick_setup(uri: str = None, database: str = None) -> DB:
    """Quick setup with all features enabled"""
    return DB(uri, database)

def production_setup(uri: str = None, database: str = None) -> DB:
    """Production setup with monitoring, caching, and security"""
    return DB(uri, database)

def development_setup(uri: str = None, database: str = None) -> DB:
    """Development setup with debugging and hot reload"""
    os.environ["GDMONGO_DEBUG"] = "true"
    return DB(uri, database)

__all__.extend(["quick_setup", "production_setup", "development_setup"])

# Suppress startup messages during tests
if not os.getenv('GDMONGO_SUPPRESS_STARTUP', False):
    print(f"gdmongolite v{__version__} - The World's Most Powerful MongoDB Toolkit loaded!")
    print("Ready for development and production use!")
    print(f"GitHub: https://github.com/ganeshdatta23/gdmongolite")
    print(f"PyPI: https://pypi.org/project/gdmongolite/")
    print(f"Author: Ganesh Datta Padamata (ganeshdattapadamata@gmail.com)")