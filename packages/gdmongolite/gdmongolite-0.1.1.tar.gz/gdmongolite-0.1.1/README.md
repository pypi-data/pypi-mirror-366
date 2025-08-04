# gdmongolite Documentation
gdmongolite is a zero-boilerplate, schema-first, multi-driver MongoDB toolkit that unifies sync and async drivers, Pydantic validation, migrations, telemetry hooks, and a CLI into one package.

## Table of Contents
1. Installation
2. Configuration
3. Defining Schemas
4. Connecting to MongoDB
5. CRUD Operations
6. Migrations
7. Interactive Shell
8. Model Generation
9. Telemetry Hooks
10. CLI Reference
11. Testing
12. Project Layout
13. Best Practices
14. FAQ

## 1. Installation
Install from PyPI:
```bash
pip install gdmongolite
```
For development tools:
```bash
pip install gdmongolite[dev]
```

## 2. Configuration
Create a `.env` file in your project root:
```
MONGO_URI="mongodb://localhost:27017"
MONGO_DB="myapp"
MONGO_MAX_POOL=50
```
gdmongolite reads these automatically via environment variables. You can also override via environment variables.

## 3. Defining Schemas
All schemas inherit from `Schema`. Collection names are inferred:
```python
# src/gdmongolite/schema/__init__.py
from gdmongolite import DB, Schema, Email, Positive

db = DB()  # Uses .env

class User(Schema):
    name: str
    email: Email          # Validates format
    age: Positive       # Must be >0
    tags: list[str] = []  # Default empty list
```
Now you can use `db.User` for operations.

## 4. Connecting to MongoDB
Instantiate the singleton `DB` facade:
```python
from gdmongolite import DB

db = DB()
```

## 5. CRUD Operations
| Operation      | Async                                        |
|----------------|----------------------------------------------|
| Insert one     | `await db.User.insert(data)`                 |
| Find many      | `await db.User.find(**filters).to_list()`    |
Returned value is a MongoDB cursor for `find` operations.

## 6. Migrations
Generate migration scripts when schemas change:
```bash
gdmongolite migrate
```
- Creates timestamped scripts under `migrations/`

## 7. Interactive Shell
Launch REPL with `db` preloaded:
```bash
gdmongolite shell
```
Inside the shell:
```python
await db.User.insert({"name":"Bob", "email":"bob@x.com", "age":25})
users = await db.User.find().to_list()
```

## 8. Model Generation
Scaffold schemas from existing collections:
```bash
gdmongolite gen-model --collection products --out src/models/product.py
```
- Samples documents
- Infers field names and types

## 9. Telemetry Hooks
Register hooks on query events:
```python
from gdmongolite.core import DBSingleton

@DBSingleton.on("pre_query")
def before(collection, filt, opts):
    print(f"About to query {collection}: {filt}")

@DBSingleton.on("post_query")
def after(collection, result):
    print(f"{collection} query completed.")
```

## 10. CLI Reference
```bash
gdmongolite --help
# Commands:
# migrate     Generate and apply migration scripts
# shell       Launch interactive REPL
# gen-model   Scaffold a schema from an existing collection
# test        Run test suite
```

## 11. Testing
```bash
pip install gdmongolite[dev]
pytest --maxfail=1 --disable-warnings -q
```

## 12. Project Layout
```
gdmongolite/
├── src/gdmongolite/
│   ├── __init__.py
│   ├── core.py
│   ├── schema/
│   │   └── __init__.py
│   ├── query.py
│   ├── migrate/
│   │   └── __init__.py
│   ├── telemetry.py
│   ├── cli.py
│   └── models/ # Generated models
├── migrations/      # Auto-generated scripts
├── tests/
├── README.md
├── LICENSE
├── pyproject.toml
└── .env
```

## 13. Best Practices
- Keep schemas small and focused
- Version your migrations and commit them
- Use telemetry hooks to capture performance metrics

## 14. FAQ
**Q: How do I handle large result sets?**
A: Use cursors with `to_list()`.
**Q: Can I use gdmongolite with FastAPI?**
A: Absolutely—instantiate `db` at startup and import your schemas into your routers.

**gdmongolite** empowers you with a single, coherent API for all MongoDB needs—schema definition, validation, querying, migrations, telemetry, and CLI tooling—ensuring you never touch low-level driver code again.

## Author
**Ganesh Datta Padamata**
Email: ganeshdattapadamata@gmail.com
PyPI: ganeshdatta999
