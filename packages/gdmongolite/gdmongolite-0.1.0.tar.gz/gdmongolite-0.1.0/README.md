# gdmongolite

gdmongolite: lightweight, auto-maintained all-in-one MongoDB toolkit by Ganeshdatta

## Installation

```bash
pip install gdmongolite
```

## Usage

### 1. Configure Your Environment

Create a `.env` file at your project root with your MongoDB URI and settings:

```
MONGO_URI="mongodb://localhost:27017"
MONGO_DB="myapp"
MONGO_MAX_POOL=50
```

### 2. Defining Your First Schema

Open `src/gdmongolite/schema/__init__.py` and define your schema:

```python
from gdmongolite import DB, Schema, Email, Positive

# Bind to default DB from .env
db = DB()

class User(Schema):
    name: str
    email: Email
    age: Positive
    tags: list[str] = []

# Immediately available on DB instance
assert db.User is User
```

### 3. Running Migrations

Whenever you add, remove, or change fields in your schema, run:

```bash
poetry run gdmongolite migrate
```

### 4. Interactive Shell

Start an interactive shell to inspect and test your models:

```bash
poetry run gdmongolite shell
```

Then, in the REPL:

```python
await db.User.insert({"name":"Alice","email":"a@b.com","age":28})
users = await db.User.find(age__gte=18).to_list()
print(users)
```

### 5. Generating Models from Existing Collections

To scaffold a model from a live collection:

```bash
poetry run gdmongolite gen-model --collection products --out src/models/product.py
```

### 6. Running Tests

Validate core and your extensions:

```bash
poetry run pytest --maxfail=1 --disable-warnings -q
```

### 7. Adding Telemetry Hooks

In your app top-level (e.g., `app.py`):

```python
from gdmongolite.core import DBSingleton

@DBSingleton.on("pre_query")
def log_pre(collection, filt, opts):
    print(f"Querying {collection}: {filt}")

@DBSingleton.on("post_query")
def log_post(collection, result):
    print(f"{collection} query completed.")
```

## Cookbook (Advanced Use Cases)

*   Complex Queries
*   Transactions
*   Sharded Clusters
*   Change Streams

(To be expanded)