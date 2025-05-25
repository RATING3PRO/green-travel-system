from pydantic import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # 应用设置
    APP_NAME: str = "城市绿色出行优化系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # API密钥
    SECRET_KEY: str = "your-secret-key-here"  # 用于JWT token
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AMAP_API_KEY: str = ""  # 高德地图Web API密钥
    AMAP_WEB_KEY: str = ""  # 高德地图Web服务密钥
    
    # 外部服务API密钥
    WEATHER_API_KEY: Optional[str] = None
    MAPS_API_KEY: Optional[str] = None
    
    # 服务器设置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 高德地图配置
    AMAP_GEOCODE_URL: str = "https://restapi.amap.com/v3/geocode/geo"
    AMAP_ROUTE_URL: str = "https://restapi.amap.com/v3/direction/driving"
    
    # 百度地图API配置
    BAIDU_MAP_AK: str = os.getenv("BAIDU_MAP_AK", "")
    
    class Config:
        env_file = ".env"

settings = Settings() 