from app.core.db.db_connection import connect, disconnect
from contextlib import asynccontextmanager
from app.routes.user.user_route import router as user_router
from app.routes.auth.auth import router as auth_router
from app.routes.product.product import router as product_router

from app.core.error.error import setup_error_handlers
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await disconnect()

class MyLifespan:
    def __init__(self, app):
        self.app = app
    async def __aenter__(self):
        await connect()
    async def __aexit__(self, *args):
        await disconnect()

app = FastAPI(lifespan=lifespan)

#Error Handling (Global)
setup_error_handlers(app)

# Router Registration
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(product_router)

@app.get("/")
async def root():
    return {"message": "Working"}