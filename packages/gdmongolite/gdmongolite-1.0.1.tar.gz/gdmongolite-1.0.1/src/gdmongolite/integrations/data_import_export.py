"""Data import/export functionality for gdmongolite"""

import json
import csv
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, Type, IO
from pathlib import Path
from datetime import datetime
import asyncio

from ..core import DB, Schema, QueryResponse
from ..exceptions import GDMongoError
from ..utils import serialize_for_mongo, format_file_size


class DataImporter:
    """Import data from various formats into MongoDB"""
    
    def __init__(self, db: DB):
        self.db = db
        self.supported_formats = ['json', 'csv', 'yaml', 'yml', 'xml', 'bson']
    
    async def import_from_file(
        self, 
        file_path: Union[str, Path], 
        schema: Type[Schema],
        format: str = None,
        batch_size: int = 1000,
        validate: bool = True,
        upsert: bool = False,
        upsert_key: str = None
    ) -> QueryResponse:
        """Import data from file"""
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise GDMongoError(f"File not found: {file_path}")
        
        # Auto-detect format from extension
        if not format:
            format = file_path.suffix.lower().lstrip('.')
        
        if format not in self.supported_formats:
            raise GDMongoError(f"Unsupported format: {format}")
        
        print(f"📥 Importing from {file_path} ({format.upper()})...")
        start_time = datetime.now()
        
        try:
            # Read and parse data
            if format == 'json':
                data = await self._read_json(file_path)
            elif format == 'csv':
                data = await self._read_csv(file_path)
            elif format in ['yaml', 'yml']:
                data = await self._read_yaml(file_path)
            elif format == 'xml':
                data = await self._read_xml(file_path)
            else:
                raise GDMongoError(f"Format {format} not implemented yet")
            
            # Validate data if requested
            if validate:
                data = await self._validate_data(data, schema)
            
            # Import in batches
            total_imported = 0
            errors = []
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                try:
                    if upsert and upsert_key:
                        # Upsert each document individually
                        for doc in batch:
                            if upsert_key in doc:
                                await schema.update(
                                    {upsert_key: doc[upsert_key]},
                                    doc,
                                    upsert=True
                                )
                                total_imported += 1
                    else:
                        # Regular batch insert
                        response = await schema.insert(batch)
                        if response.success:
                            total_imported += response.count
                        else:
                            errors.append(f"Batch {i//batch_size + 1}: {response.error}")
                
                except Exception as e:
                    errors.append(f"Batch {i//batch_size + 1}: {str(e)}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return QueryResponse(
                success=len(errors) == 0,
                data={"imported": total_imported, "errors": errors},
                count=total_imported,
                message=f"Imported {total_imported} documents in {duration:.2f}s",
                duration=duration * 1000
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return QueryResponse(
                success=False,
                error=str(e),
                message="Import failed",
                duration=duration * 1000
            )
    
    async def _read_json(self, file_path: Path) -> List[Dict]:
        """Read JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both single object and array
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise GDMongoError("JSON must contain object or array")
    
    async def _read_csv(self, file_path: Path) -> List[Dict]:
        """Read CSV file"""
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string values to appropriate types
                converted_row = {}
                for key, value in row.items():
                    converted_row[key] = self._convert_csv_value(value)
                data.append(converted_row)
        
        return data
    
    def _convert_csv_value(self, value: str) -> Any:
        """Convert CSV string value to appropriate Python type"""
        if value == '':
            return None
        
        # Try boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try integer
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try JSON (for arrays/objects)
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Return as string
        return value
    
    async def _read_yaml(self, file_path: Path) -> List[Dict]:
        """Read YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise GDMongoError("YAML must contain object or array")
    
    async def _read_xml(self, file_path: Path) -> List[Dict]:
        """Read XML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        def xml_to_dict(element):
            result = {}
            
            # Add attributes
            if element.attrib:
                result.update(element.attrib)
            
            # Add text content
            if element.text and element.text.strip():
                if len(element) == 0:  # No children
                    return element.text.strip()
                else:
                    result['_text'] = element.text.strip()
            
            # Add children
            for child in element:
                child_data = xml_to_dict(child)
                
                if child.tag in result:
                    # Convert to list if multiple children with same tag
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        # If root has multiple children with same tag, return as list
        children_tags = [child.tag for child in root]
        if len(set(children_tags)) == 1 and len(children_tags) > 1:
            return [xml_to_dict(child) for child in root]
        else:
            return [xml_to_dict(root)]
    
    async def _validate_data(self, data: List[Dict], schema: Type[Schema]) -> List[Dict]:
        """Validate data against schema"""
        validated_data = []
        
        for i, item in enumerate(data):
            try:
                validated_item = schema(**item)
                validated_data.append(validated_item.dict())
            except Exception as e:
                raise GDMongoError(f"Validation error at item {i}: {str(e)}")
        
        return validated_data
    
    async def import_from_url(
        self, 
        url: str, 
        schema: Type[Schema],
        format: str = 'json',
        **kwargs
    ) -> QueryResponse:
        """Import data from URL"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise GDMongoError(f"HTTP {response.status}: {await response.text()}")
                    
                    if format == 'json':
                        data = await response.json()
                    else:
                        text = await response.text()
                        # Save to temp file and process
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
                            f.write(text)
                            temp_path = f.name
                        
                        result = await self.import_from_file(temp_path, schema, format, **kwargs)
                        Path(temp_path).unlink()  # Clean up
                        return result
            
            # Handle JSON data directly
            if isinstance(data, dict):
                data = [data]
            
            return await schema.insert(data)
        
        except Exception as e:
            return QueryResponse(
                success=False,
                error=str(e),
                message="URL import failed"
            )


class DataExporter:
    """Export data from MongoDB to various formats"""
    
    def __init__(self, db: DB):
        self.db = db
        self.supported_formats = ['json', 'csv', 'yaml', 'yml', 'xml']
    
    async def export_to_file(
        self,
        schema: Type[Schema],
        file_path: Union[str, Path],
        format: str = None,
        query: Dict = None,
        limit: int = None,
        sort: Dict = None,
        projection: Dict = None
    ) -> QueryResponse:
        """Export data to file"""
        
        file_path = Path(file_path)
        
        # Auto-detect format from extension
        if not format:
            format = file_path.suffix.lower().lstrip('.')
        
        if format not in self.supported_formats:
            raise GDMongoError(f"Unsupported format: {format}")
        
        print(f"📤 Exporting to {file_path} ({format.upper()})...")
        start_time = datetime.now()
        
        try:
            # Query data
            cursor = schema.find(**(query or {}))
            
            if projection:
                cursor = cursor.project(**projection)
            
            if sort:
                cursor = cursor.sort(**sort)
            
            if limit:
                cursor = cursor.limit(limit)
            
            data = await cursor.to_list()
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export based on format
            if format == 'json':
                await self._write_json(file_path, data)
            elif format == 'csv':
                await self._write_csv(file_path, data)
            elif format in ['yaml', 'yml']:
                await self._write_yaml(file_path, data)
            elif format == 'xml':
                await self._write_xml(file_path, data)
            
            duration = (datetime.now() - start_time).total_seconds()
            file_size = file_path.stat().st_size
            
            return QueryResponse(
                success=True,
                data={"file_path": str(file_path), "file_size": file_size},
                count=len(data),
                message=f"Exported {len(data)} documents ({format_file_size(file_size)}) in {duration:.2f}s",
                duration=duration * 1000
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return QueryResponse(
                success=False,
                error=str(e),
                message="Export failed",
                duration=duration * 1000
            )
    
    async def _write_json(self, file_path: Path, data: List[Dict]):
        """Write data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    async def _write_csv(self, file_path: Path, data: List[Dict]):
        """Write data to CSV file"""
        if not data:
            return
        
        # Get all unique field names
        fieldnames = set()
        for item in data:
            fieldnames.update(self._flatten_dict(item).keys())
        
        fieldnames = sorted(fieldnames)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                flattened = self._flatten_dict(item)
                # Convert complex types to strings
                for key, value in flattened.items():
                    if isinstance(value, (dict, list)):
                        flattened[key] = json.dumps(value, default=str)
                    elif value is None:
                        flattened[key] = ''
                    else:
                        flattened[key] = str(value)
                
                writer.writerow(flattened)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary for CSV export"""
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                # Handle list of objects
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    async def _write_yaml(self, file_path: Path, data: List[Dict]):
        """Write data to YAML file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    async def _write_xml(self, file_path: Path, data: List[Dict]):
        """Write data to XML file"""
        root = ET.Element("data")
        
        for i, item in enumerate(data):
            item_element = ET.SubElement(root, "item", {"id": str(i)})
            self._dict_to_xml(item, item_element)
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def _dict_to_xml(self, data: Dict, parent: ET.Element):
        """Convert dictionary to XML elements"""
        for key, value in data.items():
            # Clean key name for XML
            clean_key = str(key).replace(' ', '_').replace('.', '_')
            
            if isinstance(value, dict):
                child = ET.SubElement(parent, clean_key)
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    child = ET.SubElement(parent, clean_key, {"index": str(i)})
                    if isinstance(item, dict):
                        self._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, clean_key)
                child.text = str(value) if value is not None else ""
    
    async def export_schema_to_file(
        self,
        schema: Type[Schema],
        file_path: Union[str, Path],
        include_data: bool = True,
        include_indexes: bool = True
    ) -> QueryResponse:
        """Export schema definition and optionally data"""
        
        file_path = Path(file_path)
        
        try:
            schema_info = {
                "schema_name": schema.__name__,
                "collection_name": schema._collection_name,
                "fields": {},
                "created_at": datetime.now().isoformat()
            }
            
            # Add field information
            for field_name, field_info in schema.__fields__.items():
                schema_info["fields"][field_name] = {
                    "type": str(field_info.type_),
                    "required": field_info.required,
                    "default": str(field_info.default) if field_info.default is not None else None
                }
            
            # Add index information if requested
            if include_indexes:
                # This would require accessing MongoDB to get actual indexes
                schema_info["indexes"] = []
            
            # Add sample data if requested
            if include_data:
                cursor = schema.find().limit(10)
                sample_data = await cursor.to_list()
                schema_info["sample_data"] = sample_data
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema_info, f, indent=2, default=str, ensure_ascii=False)
            
            return QueryResponse(
                success=True,
                data={"file_path": str(file_path)},
                count=1,
                message=f"Schema exported to {file_path}"
            )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                error=str(e),
                message="Schema export failed"
            )


class DataMigrator:
    """Migrate data between different databases or collections"""
    
    def __init__(self, source_db: DB, target_db: DB = None):
        self.source_db = source_db
        self.target_db = target_db or source_db
    
    async def migrate_collection(
        self,
        source_schema: Type[Schema],
        target_schema: Type[Schema] = None,
        transform_func: callable = None,
        batch_size: int = 1000
    ) -> QueryResponse:
        """Migrate data from one collection to another"""
        
        target_schema = target_schema or source_schema
        
        try:
            # Get all data from source
            cursor = source_schema.find()
            total_count = await cursor.count()
            
            migrated_count = 0
            errors = []
            
            # Process in batches
            async for batch in self._batch_cursor(cursor, batch_size):
                try:
                    # Transform data if function provided
                    if transform_func:
                        batch = [transform_func(doc) for doc in batch]
                    
                    # Insert into target
                    response = await target_schema.insert(batch)
                    if response.success:
                        migrated_count += response.count
                    else:
                        errors.append(response.error)
                
                except Exception as e:
                    errors.append(str(e))
            
            return QueryResponse(
                success=len(errors) == 0,
                data={"migrated": migrated_count, "total": total_count, "errors": errors},
                count=migrated_count,
                message=f"Migrated {migrated_count}/{total_count} documents"
            )
        
        except Exception as e:
            return QueryResponse(
                success=False,
                error=str(e),
                message="Migration failed"
            )
    
    async def _batch_cursor(self, cursor, batch_size: int):
        """Yield cursor results in batches"""
        batch = []
        
        async for doc in cursor:
            batch.append(doc)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch