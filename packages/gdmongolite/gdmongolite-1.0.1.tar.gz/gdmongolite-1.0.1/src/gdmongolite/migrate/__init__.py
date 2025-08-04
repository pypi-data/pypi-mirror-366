"""Migration system for gdmongolite"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..exceptions import MigrationError

class Migration:
    """Represents a single migration"""
    
    def __init__(self, name: str, version: str, description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.operations = []
        self.applied = False
        self.applied_at = None
    
    def add_index(self, collection: str, fields: Dict[str, int], **options):
        """Add index creation operation"""
        self.operations.append({
            'type': 'create_index',
            'collection': collection,
            'fields': fields,
            'options': options
        })
        return self
    
    def drop_index(self, collection: str, index_name: str):
        """Add index drop operation"""
        self.operations.append({
            'type': 'drop_index',
            'collection': collection,
            'index_name': index_name
        })
        return self
    
    def add_field(self, collection: str, field: str, default_value: Any = None):
        """Add field to all documents in collection"""
        self.operations.append({
            'type': 'add_field',
            'collection': collection,
            'field': field,
            'default_value': default_value
        })
        return self
    
    def remove_field(self, collection: str, field: str):
        """Remove field from all documents in collection"""
        self.operations.append({
            'type': 'remove_field',
            'collection': collection,
            'field': field
        })
        return self
    
    def rename_field(self, collection: str, old_name: str, new_name: str):
        """Rename field in all documents"""
        self.operations.append({
            'type': 'rename_field',
            'collection': collection,
            'old_name': old_name,
            'new_name': new_name
        })
        return self
    
    def rename_collection(self, old_name: str, new_name: str):
        """Rename collection"""
        self.operations.append({
            'type': 'rename_collection',
            'old_name': old_name,
            'new_name': new_name
        })
        return self
    
    def custom_operation(self, operation: Dict[str, Any]):
        """Add custom migration operation"""
        self.operations.append(operation)
        return self
    
    def to_dict(self):
        """Convert migration to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'operations': self.operations,
            'applied': self.applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create migration from dictionary"""
        migration = cls(data['name'], data['version'], data.get('description', ''))
        migration.operations = data.get('operations', [])
        migration.applied = data.get('applied', False)
        if data.get('applied_at'):
            migration.applied_at = datetime.fromisoformat(data['applied_at'])
        return migration

class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db, migrations_dir: str = "migrations"):
        self.db = db
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Migration tracking collection
        self.migration_collection = "gdmongo_migrations"
    
    async def create_migration(self, name: str, description: str = "") -> Migration:
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{timestamp}_{name}"
        
        migration = Migration(name, version, description)
        
        # Save migration file
        migration_file = self.migrations_dir / f"{version}.json"
        with open(migration_file, 'w') as f:
            json.dump(migration.to_dict(), f, indent=2)
        
        return migration
    
    def load_migrations(self) -> List[Migration]:
        """Load all migration files"""
        migrations = []
        
        for migration_file in sorted(self.migrations_dir.glob("*.json")):
            try:
                with open(migration_file, 'r') as f:
                    data = json.load(f)
                migration = Migration.from_dict(data)
                migrations.append(migration)
            except Exception as e:
                raise MigrationError(f"Failed to load migration {migration_file}: {e}")
        
        return migrations
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            db = self.db._get_db("async")
            collection = db[self.migration_collection]
            
            cursor = collection.find({}, {"version": 1})
            docs = await cursor.to_list(None)
            return [doc["version"] for doc in docs]
        except Exception:
            return []
    
    def get_applied_migrations_sync(self) -> List[str]:
        """Get list of applied migration versions (sync)"""
        try:
            db = self.db._get_db("sync")
            collection = db[self.migration_collection]
            
            docs = list(collection.find({}, {"version": 1}))
            return [doc["version"] for doc in docs]
        except Exception:
            return []
    
    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        try:
            db = self.db._get_db("async")
            
            for operation in migration.operations:
                await self._execute_operation(db, operation)
            
            # Mark as applied
            collection = db[self.migration_collection]
            await collection.insert_one({
                "version": migration.version,
                "name": migration.name,
                "description": migration.description,
                "applied_at": datetime.now(),
                "operations_count": len(migration.operations)
            })
            
            migration.applied = True
            migration.applied_at = datetime.now()
            
            return True
        
        except Exception as e:
            raise MigrationError(f"Failed to apply migration {migration.version}: {e}")
    
    def apply_migration_sync(self, migration: Migration) -> bool:
        """Apply a single migration (sync)"""
        try:
            db = self.db._get_db("sync")
            
            for operation in migration.operations:
                self._execute_operation_sync(db, operation)
            
            # Mark as applied
            collection = db[self.migration_collection]
            collection.insert_one({
                "version": migration.version,
                "name": migration.name,
                "description": migration.description,
                "applied_at": datetime.now(),
                "operations_count": len(migration.operations)
            })
            
            migration.applied = True
            migration.applied_at = datetime.now()
            
            return True
        
        except Exception as e:
            raise MigrationError(f"Failed to apply migration {migration.version}: {e}")
    
    async def _execute_operation(self, db, operation: Dict[str, Any]):
        """Execute a single migration operation (async)"""
        op_type = operation['type']
        
        if op_type == 'create_index':
            collection = db[operation['collection']]
            await collection.create_index(
                list(operation['fields'].items()),
                **operation.get('options', {})
            )
        
        elif op_type == 'drop_index':
            collection = db[operation['collection']]
            await collection.drop_index(operation['index_name'])
        
        elif op_type == 'add_field':
            collection = db[operation['collection']]
            await collection.update_many(
                {operation['field']: {'$exists': False}},
                {'$set': {operation['field']: operation.get('default_value')}}
            )
        
        elif op_type == 'remove_field':
            collection = db[operation['collection']]
            await collection.update_many(
                {},
                {'$unset': {operation['field']: ""}}
            )
        
        elif op_type == 'rename_field':
            collection = db[operation['collection']]
            await collection.update_many(
                {},
                {'$rename': {operation['old_name']: operation['new_name']}}
            )
        
        elif op_type == 'rename_collection':
            await db[operation['old_name']].rename(operation['new_name'])
        
        else:
            raise MigrationError(f"Unknown operation type: {op_type}")
    
    def _execute_operation_sync(self, db, operation: Dict[str, Any]):
        """Execute a single migration operation (sync)"""
        op_type = operation['type']
        
        if op_type == 'create_index':
            collection = db[operation['collection']]
            collection.create_index(
                list(operation['fields'].items()),
                **operation.get('options', {})
            )
        
        elif op_type == 'drop_index':
            collection = db[operation['collection']]
            collection.drop_index(operation['index_name'])
        
        elif op_type == 'add_field':
            collection = db[operation['collection']]
            collection.update_many(
                {operation['field']: {'$exists': False}},
                {'$set': {operation['field']: operation.get('default_value')}}
            )
        
        elif op_type == 'remove_field':
            collection = db[operation['collection']]
            collection.update_many(
                {},
                {'$unset': {operation['field']: ""}}
            )
        
        elif op_type == 'rename_field':
            collection = db[operation['collection']]
            collection.update_many(
                {},
                {'$rename': {operation['old_name']: operation['new_name']}}
            )
        
        elif op_type == 'rename_collection':
            db[operation['old_name']].rename(operation['new_name'])
        
        else:
            raise MigrationError(f"Unknown operation type: {op_type}")
    
    async def migrate_all(self) -> Dict[str, Any]:
        """Apply all pending migrations"""
        migrations = self.load_migrations()
        applied_versions = await self.get_applied_migrations()
        
        pending_migrations = [
            m for m in migrations 
            if m.version not in applied_versions
        ]
        
        results = {
            'total_migrations': len(migrations),
            'applied_count': len(applied_versions),
            'pending_count': len(pending_migrations),
            'newly_applied': [],
            'errors': []
        }
        
        for migration in pending_migrations:
            try:
                await self.apply_migration(migration)
                results['newly_applied'].append(migration.version)
            except Exception as e:
                results['errors'].append({
                    'migration': migration.version,
                    'error': str(e)
                })
        
        return results
    
    def migrate_all_sync(self) -> Dict[str, Any]:
        """Apply all pending migrations (sync)"""
        migrations = self.load_migrations()
        applied_versions = self.get_applied_migrations_sync()
        
        pending_migrations = [
            m for m in migrations 
            if m.version not in applied_versions
        ]
        
        results = {
            'total_migrations': len(migrations),
            'applied_count': len(applied_versions),
            'pending_count': len(pending_migrations),
            'newly_applied': [],
            'errors': []
        }
        
        for migration in pending_migrations:
            try:
                self.apply_migration_sync(migration)
                results['newly_applied'].append(migration.version)
            except Exception as e:
                results['errors'].append({
                    'migration': migration.version,
                    'error': str(e)
                })
        
        return results
    
    async def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration (basic implementation)"""
        # This is a basic implementation - full rollback would need reverse operations
        try:
            db = self.db._get_db("async")
            collection = db[self.migration_collection]
            
            result = await collection.delete_one({"version": version})
            return result.deleted_count > 0
        
        except Exception as e:
            raise MigrationError(f"Failed to rollback migration {version}: {e}")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status"""
        migrations = self.load_migrations()
        applied_versions = self.get_applied_migrations_sync()
        
        return {
            'total_migrations': len(migrations),
            'applied_migrations': len(applied_versions),
            'pending_migrations': len(migrations) - len(applied_versions),
            'migrations': [
                {
                    'version': m.version,
                    'name': m.name,
                    'description': m.description,
                    'applied': m.version in applied_versions,
                    'operations_count': len(m.operations)
                }
                for m in migrations
            ]
        }