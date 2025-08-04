# gdmongolite - The World's Most Powerful and Easiest MongoDB Toolkit

**Zero-boilerplate, schema-first MongoDB operations with automatic sync/async detection, advanced queries, real-time features, comprehensive security, intelligent caching, full monitoring, FastAPI integration, and production-ready deployment tools.**

[![PyPI version](https://badge.fury.io/py/gdmongolite.svg)](https://badge.fury.io/py/gdmongolite)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install gdmongolite
```

## Quick Start (30 seconds to productivity!)

```python
from gdmongolite import DB, Schema, Email, FieldTypes

# 1. Define your data model
class User(Schema):
    name: FieldTypes.Name
    email: Email
    age: FieldTypes.Age
    role: str = "user"

# 2. Connect and register
db = DB()  # Auto-connects to MongoDB
db.register_schema(User)

# 3. Use it! (Works in both sync and async)
async def main():
    # Insert with automatic validation
    user = await db.User.insert({
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    })
    
    # Query with advanced filtering
    users = await db.User.find(age__gte=18, role="user").to_list()
    
    # Update documents
    await db.User.update({"role": "user"}, {"$set": {"role": "member"}})
    
    # Aggregations made simple
    stats = await db.User.aggregate().group("$role", count={"$sum": 1}).execute()
```

## Complete Feature Guide

### 1. Schema Definition and Validation

```python
from gdmongolite import DB, Schema, Email, FieldTypes
from typing import List, Optional
from datetime import datetime

class User(Schema):
    # Built-in field types with validation
    name: FieldTypes.Name              # 1-100 chars
    email: Email                       # Email validation
    age: FieldTypes.Age               # 0-150 range
    username: FieldTypes.Username     # 3-30 chars, alphanumeric
    
    # Optional fields with defaults
    role: str = "user"
    is_active: bool = True
    tags: List[str] = []
    created_at: datetime = datetime.now()
    
    # Custom validation
    bio: Optional[FieldTypes.Description] = None  # Max 1000 chars

class Product(Schema):
    name: FieldTypes.Title
    price: FieldTypes.Price           # Non-negative float
    rating: FieldTypes.Rating         # 0-5 range
    category: str
    in_stock: bool = True

class Order(Schema):
    user_id: str
    product_ids: List[str]
    total: FieldTypes.Price
    status: str = "pending"
    order_date: datetime = datetime.now()
```

### 2. Database Connection and Setup

```python
# Basic connection (uses environment variables or defaults)
db = DB()

# Custom connection
db = DB(
    uri="mongodb://localhost:27017",
    database="myapp"
)

# Production connection with all options
db = DB(
    uri="mongodb+srv://user:pass@cluster.mongodb.net/",
    database="production"
)

# Register your schemas
db.register_schema(User)
db.register_schema(Product)
db.register_schema(Order)
```

### 3. CRUD Operations (Create, Read, Update, Delete)

#### Create (Insert)
```python
# Single document
user = await db.User.insert({
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "age": 28,
    "role": "admin"
})

# Multiple documents
users = await db.User.insert([
    {"name": "Bob", "email": "bob@example.com", "age": 25},
    {"name": "Carol", "email": "carol@example.com", "age": 30}
])

# Using schema objects
user_obj = User(name="David", email="david@example.com", age=35)
result = await db.User.insert(user_obj)
```

#### Read (Find/Query)
```python
# Find all
all_users = await db.User.find().to_list()

# Find with filters
adults = await db.User.find(age__gte=18).to_list()
admins = await db.User.find(role="admin").to_list()

# Complex queries
active_adults = await db.User.find(
    age__gte=18,
    is_active=True,
    role__in=["user", "admin"]
).to_list()

# Find one
user = await db.User.find(email="alice@example.com").first()

# Pagination
page1 = await db.User.find().skip(0).limit(10).to_list()
page2 = await db.User.find().skip(10).limit(10).to_list()

# Sorting
newest = await db.User.find().sort("-created_at").to_list()
oldest = await db.User.find().sort("created_at").to_list()

# Count
total_users = await db.User.find().count()
adult_count = await db.User.find(age__gte=18).count()
```

#### Update
```python
# Update many documents
result = await db.User.update(
    {"role": "user"},                    # Filter
    {"$set": {"role": "member"}}         # Update
)

# Update with operators
await db.User.update(
    {"_id": user_id},
    {
        "$set": {"last_login": datetime.now()},
        "$inc": {"login_count": 1},
        "$push": {"tags": "active"}
    }
)

# Upsert (insert if not exists)
await db.User.update(
    {"email": "new@example.com"},
    {"$set": {"name": "New User", "age": 25}},
    upsert=True
)
```

#### Delete
```python
# Delete documents
result = await db.User.delete(role="inactive")
result = await db.User.delete(age__lt=13)  # Remove underage users

# Delete by ID
await db.User.delete(_id=user_id)
```

### 4. Advanced Queries and Aggregations

```python
# Complex aggregation pipeline
pipeline_result = await (
    db.Order.aggregate()
    .match(status="completed")
    .lookup("users", "user_id", "_id", "user_info")
    .unwind("user_info")
    .group(
        "$user_info.role",
        total_orders={"$sum": 1},
        total_revenue={"$sum": "$total"},
        avg_order={"$avg": "$total"}
    )
    .sort(total_revenue=-1)
    .execute()
)

# Statistical analysis
user_stats = await (
    db.User.aggregate()
    .group(
        None,
        total_users={"$sum": 1},
        avg_age={"$avg": "$age"},
        min_age={"$min": "$age"},
        max_age={"$max": "$age"}
    )
    .execute()
)

# Date-based grouping
monthly_signups = await (
    db.User.aggregate()
    .group(
        {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
        count={"$sum": 1}
    )
    .sort(_id=1)
    .execute()
)
```

### 5. Data Import/Export

```python
from gdmongolite import DataImporter, DataExporter

# Export data
exporter = DataExporter(db)

# Export to JSON
await exporter.export_to_json(db.User, "users.json")
await exporter.export_to_json(
    db.User.find(role="admin"), 
    "admin_users.json"
)

# Export to CSV
await exporter.export_to_csv(db.User, "users.csv")

# Import data
importer = DataImporter(db)

# Import from JSON
await importer.import_from_json("users.json", User)

# Import from CSV with mapping
await importer.import_from_csv(
    "users.csv", 
    User,
    field_mapping={
        "full_name": "name",
        "email_address": "email",
        "user_age": "age"
    }
)

# Batch import with validation
await importer.batch_import(
    data_source="large_dataset.json",
    schema=User,
    batch_size=1000,
    validate=True
)
```

### 6. FastAPI Integration (Auto-Generated REST APIs)

```python
from gdmongolite import create_fastapi_app
from fastapi import FastAPI

# Create full REST API automatically
app = create_fastapi_app(
    db,
    schemas=[User, Product, Order],
    title="My Powerful API",
    version="1.0.0",
    enable_docs=True
)

# Automatically generates these endpoints:
# GET    /users/              - List users (with pagination, filtering, sorting)
# POST   /users/              - Create user
# GET    /users/{id}          - Get user by ID
# PUT    /users/{id}          - Update user
# DELETE /users/{id}          - Delete user
# POST   /users/search        - Advanced search
# GET    /users/count         - Count users
# Same for Product and Order...

# Add custom endpoints
@app.get("/analytics/dashboard")
async def analytics():
    return {
        "total_users": await db.User.find().count(),
        "total_orders": await db.Order.find().count(),
        "revenue": await db.Order.aggregate().group(
            None, total={"$sum": "$total"}
        ).execute()
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 7. Real-time Features and WebSockets

```python
from gdmongolite import WebSocketManager
from fastapi import WebSocket

# Real-time data updates
@app.websocket("/ws/users")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Watch for changes in User collection
    async def on_user_change(change):
        await websocket.send_json({
            "type": "user_update",
            "operation": change["operationType"],
            "data": change.get("fullDocument", {})
        })
    
    # Subscribe to changes
    await db.User.watch_changes(on_user_change)

# Live queries that update automatically
live_query = db.User.live_query(is_active=True)
await live_query.subscribe(websocket)
```

### 8. Security and Authentication

```python
from gdmongolite import SecurityMiddleware, PasswordManager

# Setup security
security = SecurityMiddleware(db)

# Password hashing
password_manager = PasswordManager()
hashed = password_manager.hash_password("user_password")
is_valid = password_manager.verify_password("user_password", hashed)

# JWT tokens
from gdmongolite import JWTManager
jwt_manager = JWTManager(secret_key="your-secret-key")

@app.post("/login")
async def login(email: str, password: str):
    user = await db.User.find(email=email).first()
    if user and password_manager.verify_password(password, user["password"]):
        token = jwt_manager.create_token({"user_id": str(user["_id"])})
        return {"access_token": token}
    raise HTTPException(401, "Invalid credentials")

# Protected endpoints
@app.get("/protected")
async def protected_route(current_user=Depends(jwt_manager.get_current_user)):
    return {"message": f"Hello {current_user['email']}"}
```

### 9. Caching for Performance

```python
from gdmongolite import add_caching_to_db

# Enable caching
cached_db = add_caching_to_db(db)

# Cached queries (automatic)
users = await cached_db.User.find(role="admin").to_list()  # Cached
users = await cached_db.User.find(role="admin").to_list()  # From cache

# Manual caching
@cached_db.cached(ttl=300)  # Cache for 5 minutes
async def expensive_operation():
    return await db.Order.aggregate().complex_pipeline().execute()

# Cache statistics
cache_stats = cached_db.get_cache_stats()
print(f"Hit rate: {cache_stats['hit_rate']}")
```

### 10. Monitoring and Performance

```python
from gdmongolite import add_monitoring_to_db

# Enable monitoring
monitored_db = add_monitoring_to_db(db)

# Get performance metrics
stats = monitored_db.get_performance_stats()
print(f"Average query time: {stats['avg_query_time']}ms")
print(f"Slow queries: {len(stats['slow_queries'])}")

# Health check
health = monitored_db.health_check()
print(f"Database status: {health['status']}")
print(f"Connection pool: {health['connection_pool']}")

# Built-in monitoring dashboard
@app.get("/monitoring/dashboard")
async def monitoring_dashboard():
    return monitored_db.get_full_stats()
```

### 11. Sync Usage (Non-async)

```python
# All operations work in sync mode too
db = DB()
db.register_schema(User)

# Sync operations (automatically detected)
user = db.User.insert_sync({
    "name": "Sync User",
    "email": "sync@example.com",
    "age": 25
})

users = db.User.find(age__gte=18).to_list_sync()
db.User.update_sync({"role": "user"}, {"$set": {"updated": True}})
```

### 12. Environment Configuration

```python
# .env file
MONGO_URI=mongodb://localhost:27017
MONGO_DB=myapp
MONGO_MAX_POOL=50
MONGO_MIN_POOL=5
MONGO_TIMEOUT_MS=30000

# Advanced configuration
GDMONGO_CACHE_TTL=3600
GDMONGO_ENABLE_MONITORING=true
GDMONGO_LOG_SLOW_QUERIES=true
GDMONGO_SLOW_QUERY_THRESHOLD=500
```

### 13. Production Deployment

```python
# Production-ready setup
from gdmongolite import production_setup

db = production_setup(
    uri="mongodb+srv://user:pass@cluster.mongodb.net/",
    database="production"
)

# With all features enabled
app = create_fastapi_app(
    db,
    schemas=[User, Product, Order],
    enable_monitoring=True,
    enable_caching=True,
    enable_security=True,
    cors_origins=["https://myapp.com"]
)

# Docker deployment
# FROM python:3.11-slim
# COPY . /app
# WORKDIR /app
# RUN pip install gdmongolite
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Why Choose gdmongolite?

### vs PyMongo
- ❌ PyMongo: Manual everything, no validation, verbose syntax
- ✅ gdmongolite: Automatic validation, simple syntax, zero boilerplate

### vs MongoEngine  
- ❌ MongoEngine: Django-style (heavy), sync-only, limited features
- ✅ gdmongolite: Lightweight, sync+async, comprehensive features

### vs Motor
- ❌ Motor: Async-only, no validation, manual serialization
- ✅ gdmongolite: Universal, automatic validation, smart serialization

### vs Beanie
- ❌ Beanie: Async-only, complex setup, limited tooling
- ✅ gdmongolite: Universal, zero setup, rich tooling

## Complete Example: E-commerce API

```python
from gdmongolite import DB, Schema, Email, FieldTypes, create_fastapi_app
from datetime import datetime
from typing import List

# Define schemas
class User(Schema):
    name: FieldTypes.Name
    email: Email
    password_hash: str
    role: str = "customer"

class Product(Schema):
    name: FieldTypes.Title
    price: FieldTypes.Price
    category: str
    stock: int = 0

class Order(Schema):
    user_id: str
    items: List[dict]
    total: FieldTypes.Price
    status: str = "pending"
    created_at: datetime = datetime.now()

# Setup database
db = DB()
for schema in [User, Product, Order]:
    db.register_schema(schema)

# Create API
app = create_fastapi_app(db, [User, Product, Order])

# Custom business logic
@app.post("/orders/")
async def create_order(order_data: dict):
    # Validate stock
    for item in order_data["items"]:
        product = await db.Product.find(_id=item["product_id"]).first()
        if product["stock"] < item["quantity"]:
            raise HTTPException(400, "Insufficient stock")
    
    # Create order
    order = await db.Order.insert(order_data)
    
    # Update stock
    for item in order_data["items"]:
        await db.Product.update(
            {"_id": item["product_id"]},
            {"$inc": {"stock": -item["quantity"]}}
        )
    
    return order

@app.get("/analytics")
async def analytics():
    return {
        "total_users": await db.User.find().count(),
        "total_orders": await db.Order.find().count(),
        "revenue": await db.Order.aggregate().group(
            None, total={"$sum": "$total"}
        ).execute(),
        "top_products": await db.Product.find().sort("-rating").limit(5).to_list()
    }

# Run: uvicorn main:app --reload
```

## Support and Documentation

- **GitHub**: https://github.com/ganeshdatta999/gdmongolite
- **Documentation**: https://gdmongolite.readthedocs.io
- **PyPI**: https://pypi.org/project/gdmongolite/
- **Issues**: https://github.com/ganeshdatta999/gdmongolite/issues

## License

MIT License - see [LICENSE](LICENSE) file.

## Author

**Ganesh Datta Padamata**
- Email: ganeshdattapadamata@gmail.com
- GitHub: [@ganeshdatta23](https://github.com/ganeshdatta23)


---

**🚀 Transform your MongoDB development experience with gdmongolite!**