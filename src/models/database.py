from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from ..config.settings import settings

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    preferences = relationship("UserPreference", back_populates="user")
    travel_history = relationship("TravelHistory", back_populates="user")
    route_history = relationship("RouteHistory", back_populates="user")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    max_walking_distance = Column(Float, default=1.0)
    preferred_transport_modes = Column(String)  # JSON字符串存储
    avoid_traffic = Column(Boolean, default=True)
    consider_weather = Column(Boolean, default=True)
    carbon_conscious = Column(Boolean, default=True)
    user = relationship("User", back_populates="preferences")

class TravelHistory(Base):
    __tablename__ = "travel_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_location = Column(String)  # JSON字符串存储
    end_location = Column(String)  # JSON字符串存储
    transport_mode = Column(String)
    distance = Column(Float)
    duration = Column(Integer)  # 分钟
    carbon_emission = Column(Float)
    weather_condition = Column(String)
    traffic_condition = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="travel_history")

class TrafficData(Base):
    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)  # JSON字符串存储
    timestamp = Column(DateTime, default=datetime.now)
    congestion_level = Column(Float)
    average_speed = Column(Float)
    incident_type = Column(String, nullable=True)
    data_source = Column(String)

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)  # JSON字符串存储
    timestamp = Column(DateTime, default=datetime.now)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    condition = Column(String)
    is_raining = Column(Boolean)

class TransportationService(Base):
    __tablename__ = "transportation_services"

    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String)  # bus, subway, shared_bike
    location = Column(String)  # JSON字符串存储
    status = Column(String)
    capacity = Column(String)
    next_arrival = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.now)

class RouteHistory(Base):
    __tablename__ = "route_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_location = Column(String)
    end_location = Column(String)
    distance = Column(Integer)  # 单位：米
    duration = Column(Integer)  # 单位：秒
    created_at = Column(DateTime, default=datetime.utcnow)
    weather_condition = Column(String)
    traffic_condition = Column(String)
    
    # 关联到用户
    user = relationship("User", back_populates="route_history")

# 创建数据库表
def create_tables():
    """创建所有数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
    except Exception as e:
        print(f"创建数据库表时出错: {str(e)}")
        raise

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 