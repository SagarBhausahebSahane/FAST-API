from slowapi import Limiter
from app.utils.rate_limit_handler.rate_limit_handler import get_rate_limit_key
from app.core.config.config import settings
limiter = Limiter(key_func=get_rate_limit_key,storage_uri=settings.REDIS_URL,default_limits=["2/hour"],strategy="fixed-window")