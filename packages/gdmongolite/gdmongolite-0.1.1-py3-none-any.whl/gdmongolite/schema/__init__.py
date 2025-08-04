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