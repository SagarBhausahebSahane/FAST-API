from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from app.core.config.config import settings

db = None
client = None

async def connect():
    global client, db
    client = AsyncMongoClient(settings.MONGODB_URL,server_api=ServerApi(version="1", strict=True, deprecation_errors=True))
    db = client[settings.DATABASE_NAME]
    await client.admin.command('ping')
    print("Database connected")

async def disconnect():
    global client
    if client:
        await client.close()
        print("Database disconnected")

async def get_db():
    global db
    if db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return db