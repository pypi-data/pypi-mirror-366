"""Configuration management for gdmongolite"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GDMongoConfig(BaseSettings):
    """Configuration settings for gdmongolite"""
    
    # MongoDB connection settings
    mongo_uri: str = Field(
        default="mongodb://localhost:27017",
        env="MONGO_URI",
        description="MongoDB connection string"
    )
    
    mongo_db: str = Field(
        default="gdmongo",
        env="MONGO_DB", 
        description="Default database name"
    )
    
    mongo_max_pool: int = Field(
        default=50,
        env="MONGO_MAX_POOL",
        description="Maximum connection pool size"
    )
    
    mongo_min_pool: int = Field(
        default=5,
        env="MONGO_MIN_POOL",
        description="Minimum connection pool size"
    )
    
    mongo_timeout_ms: int = Field(
        default=30000,
        env="MONGO_TIMEOUT_MS",
        description="Connection timeout in milliseconds"
    )
    
    # Performance settings
    slow_query_threshold: int = Field(
        default=1000,
        env="GDMONGO_SLOW_QUERY_THRESHOLD",
        description="Slow query threshold in milliseconds"
    )
    
    default_batch_size: int = Field(
        default=1000,
        env="GDMONGO_BATCH_SIZE",
        description="Default cursor batch size"
    )
    
    # Telemetry settings
    telemetry_enabled: bool = Field(
        default=True,
        env="GDMONGO_TELEMETRY_ENABLED",
        description="Enable telemetry and hooks"
    )
    
    performance_monitoring: bool = Field(
        default=True,
        env="GDMONGO_PERFORMANCE_MONITORING",
        description="Enable built-in performance monitoring"
    )
    
    # Migration settings
    migrations_dir: str = Field(
        default="migrations",
        env="GDMONGO_MIGRATIONS_DIR",
        description="Directory for migration files"
    )
    
    auto_migrate: bool = Field(
        default=False,
        env="GDMONGO_AUTO_MIGRATE",
        description="Automatically apply migrations on startup"
    )
    
    # Validation settings
    strict_validation: bool = Field(
        default=True,
        env="GDMONGO_STRICT_VALIDATION",
        description="Enable strict Pydantic validation"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        env="GDMONGO_LOG_LEVEL",
        description="Logging level"
    )
    
    log_queries: bool = Field(
        default=False,
        env="GDMONGO_LOG_QUERIES",
        description="Log all database queries"
    )
    
    # Development settings
    debug_mode: bool = Field(
        default=False,
        env="GDMONGO_DEBUG",
        description="Enable debug mode"
    )
    
    @validator('mongo_uri')
    def validate_mongo_uri(cls, v):
        """Validate MongoDB URI format"""
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError('MongoDB URI must start with mongodb:// or mongodb+srv://')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

# Global configuration instance
config = GDMongoConfig()

def get_config() -> GDMongoConfig:
    """Get the global configuration instance"""
    return config

def update_config(**kwargs) -> GDMongoConfig:
    """Update configuration with new values"""
    global config
    
    # Create new config with updated values
    current_values = config.dict()
    current_values.update(kwargs)
    config = GDMongoConfig(**current_values)
    
    return config

def reset_config():
    """Reset configuration to defaults"""
    global config
    config = GDMongoConfig()

class ConfigManager:
    """Advanced configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or '.env'
        self.config = GDMongoConfig()
    
    def load_from_file(self, file_path: str):
        """Load configuration from a specific file"""
        if os.path.exists(file_path):
            load_dotenv(file_path, override=True)
            self.config = GDMongoConfig()
    
    def save_to_file(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        file_path = file_path or self.config_file
        
        config_lines = []
        for field_name, field_info in self.config.__fields__.items():
            env_name = field_info.field_info.extra.get('env', field_name.upper())
            value = getattr(self.config, field_name)
            
            # Format value appropriately
            if isinstance(value, str):
                config_lines.append(f'{env_name}="{value}"')
            else:
                config_lines.append(f'{env_name}={value}')
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(config_lines))
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get MongoDB connection parameters"""
        return {
            'uri': self.config.mongo_uri,
            'database': self.config.mongo_db,
            'maxPoolSize': self.config.mongo_max_pool,
            'minPoolSize': self.config.mongo_min_pool,
            'serverSelectionTimeoutMS': self.config.mongo_timeout_ms
        }
    
    def get_telemetry_params(self) -> Dict[str, Any]:
        """Get telemetry configuration parameters"""
        return {
            'enabled': self.config.telemetry_enabled,
            'slow_query_threshold': self.config.slow_query_threshold,
            'performance_monitoring': self.config.performance_monitoring
        }
    
    def get_migration_params(self) -> Dict[str, Any]:
        """Get migration configuration parameters"""
        return {
            'migrations_dir': self.config.migrations_dir,
            'auto_migrate': self.config.auto_migrate
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        issues = []
        warnings = []
        
        # Check MongoDB connection
        if 'localhost' in self.config.mongo_uri and not self.config.debug_mode:
            warnings.append("Using localhost MongoDB in production mode")
        
        # Check pool sizes
        if self.config.mongo_min_pool >= self.config.mongo_max_pool:
            issues.append("Minimum pool size must be less than maximum pool size")
        
        # Check timeout
        if self.config.mongo_timeout_ms < 5000:
            warnings.append("Connection timeout is very low (< 5 seconds)")
        
        # Check slow query threshold
        if self.config.slow_query_threshold < 100:
            warnings.append("Slow query threshold is very low (< 100ms)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def print_config(self):
        """Print current configuration in a readable format"""
        print("=== gdmongolite Configuration ===")
        print(f"MongoDB URI: {self.config.mongo_uri}")
        print(f"Database: {self.config.mongo_db}")
        print(f"Pool Size: {self.config.mongo_min_pool}-{self.config.mongo_max_pool}")
        print(f"Timeout: {self.config.mongo_timeout_ms}ms")
        print(f"Telemetry: {'Enabled' if self.config.telemetry_enabled else 'Disabled'}")
        print(f"Performance Monitoring: {'Enabled' if self.config.performance_monitoring else 'Disabled'}")
        print(f"Auto Migration: {'Enabled' if self.config.auto_migrate else 'Disabled'}")
        print(f"Debug Mode: {'Enabled' if self.config.debug_mode else 'Disabled'}")
        print("================================")

# Environment-specific configurations
class DevelopmentConfig(GDMongoConfig):
    """Development environment configuration"""
    debug_mode: bool = True
    log_queries: bool = True
    telemetry_enabled: bool = True
    auto_migrate: bool = True

class ProductionConfig(GDMongoConfig):
    """Production environment configuration"""
    debug_mode: bool = False
    log_queries: bool = False
    strict_validation: bool = True
    auto_migrate: bool = False

class TestingConfig(GDMongoConfig):
    """Testing environment configuration"""
    mongo_db: str = "gdmongo_test"
    debug_mode: bool = True
    telemetry_enabled: bool = False
    auto_migrate: bool = True

def get_config_for_environment(env: str) -> GDMongoConfig:
    """Get configuration for specific environment"""
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = configs.get(env.lower(), GDMongoConfig)
    return config_class()