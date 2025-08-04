"""Example schemas for gdmongolite - The world's easiest MongoDB toolkit"""

from gdmongolite import DB, Schema, Email, Positive, FieldTypes

# Create database instance
db = DB()

class User(Schema):
    """User model with comprehensive validation"""
    name: FieldTypes.Name
    email: Email
    age: FieldTypes.Age
    username: FieldTypes.Username
    tags: list[str] = []
    is_active: bool = True
    
    class Config:
        # Custom collection name (optional)
        collection_name = "users"
        
        # Add indexes
        indexes = [
            {"email": 1},  # Unique email index
            {"username": 1},  # Unique username index
            {"tags": 1},  # Multi-key index on tags
            {"name": "text", "email": "text"}  # Text search index
        ]

class Product(Schema):
    """Product model for e-commerce"""
    name: FieldTypes.Title
    description: FieldTypes.Description
    price: FieldTypes.Price
    rating: FieldTypes.Rating = 0.0
    category: str
    tags: list[str] = []
    in_stock: bool = True
    
    class Config:
        indexes = [
            {"category": 1, "price": 1},  # Compound index
            {"name": "text", "description": "text"},  # Text search
            {"rating": -1}  # Descending rating
        ]

class Order(Schema):
    """Order model with relationships"""
    user_id: str  # Reference to User
    products: list[dict]  # List of product items
    total_amount: FieldTypes.Price
    status: str = "pending"
    created_at: FieldTypes.DateTime = None
    
    class Config:
        indexes = [
            {"user_id": 1},
            {"status": 1},
            {"created_at": -1}
        ]

# Register all schemas with the database
db.register_schema(User)
db.register_schema(Product) 
db.register_schema(Order)

# Now you can use:
# await db.User.insert({"name": "John", "email": "john@example.com", "age": 30})
# users = await db.User.find(age__gte=18).to_list()
# await db.Product.update({"category": "electronics"}, {"$inc": {"rating": 0.1}})

# Export for easy importing
__all__ = ["db", "User", "Product", "Order"]