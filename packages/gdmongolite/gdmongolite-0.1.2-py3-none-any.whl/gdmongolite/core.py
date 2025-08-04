import os
import motor.motor_asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, PositiveInt

load_dotenv()

class DBSingleton:
    _instance = None
    _hooks = {
        "pre_query": [],
        "post_query": [],
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBSingleton, cls).__new__(cls)
            cls._instance.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
            cls._instance.db = cls._instance.client[os.getenv("MONGO_DB")]
            cls._instance._schemas = {}
        return cls._instance

    def __getattr__(self, name):
        if name in self._instance._schemas:
            return self._instance._schemas[name]
        return self._instance.db[name]

    @classmethod
    def on(cls, event):
        def decorator(func):
            if event in cls._hooks:
                cls._hooks[event].append(func)
            return func
        return decorator

db = DBSingleton()

class Schema(BaseModel):
    _collection = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        collection_name = cls.__name__.lower()
        cls._collection = db.db[collection_name]
        db._schemas[cls.__name__] = cls

    @classmethod
    async def insert(cls, data):
        return await cls._collection.insert_one(data)

    @classmethod
    def find(cls, **kwargs):
        query = {}
        for key, value in kwargs.items():
            if '__' in key:
                field, op = key.split('__')
                query[field] = {f'${op}': value}
            else:
                query[key] = value
        
        for hook in db._hooks["pre_query"]:
            hook(cls.__name__.lower(), query, {})

        result = cls._collection.find(query)

        for hook in db._hooks["post_query"]:
            hook(cls.__name__.lower(), result)

        return result

Email = EmailStr
Positive = PositiveInt

def DB():
    return db
