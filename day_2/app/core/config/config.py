from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "myapp"
    SECRET_KEY:str = "your-secret-key"    
    REFRESH_SECRET_KEY:str= "your-refresh-key"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 15
    REFRESH_TOKEN_EXPIRE_DAYS:int = 7 
    REDIS_URL:str="redis://localhost:6379"  
    class Config:
        env_file = ".env"

settings = Settings()