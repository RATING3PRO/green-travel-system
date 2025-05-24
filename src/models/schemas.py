from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TransportMode(str, Enum):
    WALKING = "walking"
    CYCLING = "cycling"
    BUS = "bus"
    SUBWAY = "subway"
    SHARED_BIKE = "shared_bike"

class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class RouteRequest(BaseModel):
    start_location: Location
    end_location: Location
    mode: Optional[str] = "car"  # 出行方式：car, bike, walk
    preferences: Optional[Dict[str, bool]] = {
        "consider_weather": True,
        "consider_traffic": True
    }

class RouteSegment(BaseModel):
    mode: TransportMode
    distance: float  # 公里
    duration: int   # 分钟
    start_location: Location
    end_location: Location
    carbon_emission: float  # 千克CO2
    instructions: List[str]

class Route(BaseModel):
    segments: List[RouteSegment]
    total_distance: float
    total_duration: int
    total_carbon_emission: float
    weather_condition: Optional[str]
    traffic_condition: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class UserPreference(BaseModel):
    user_id: int
    max_walking_distance: float = 1000  # 最大步行距离（米）
    preferred_transport_modes: List[str] = ["walking", "bus", "subway"]
    avoid_traffic: bool = True
    consider_weather: bool = True
    carbon_conscious: bool = True

    class Config:
        orm_mode = True

class RouteBase(BaseModel):
    start_location: str
    end_location: str
    departure_time: Optional[datetime] = None
    consider_weather: bool = True
    consider_traffic: bool = True

class TrafficPrediction(BaseModel):
    location: Location
    timestamp: datetime
    congestion_level: float  # 0-1，1表示严重拥堵
    prediction_confidence: float  # 0-1
    affected_routes: List[str]

class TravelHistoryResponse(BaseModel):
    id: int
    user_id: int
    start_location: str
    end_location: str
    transport_mode: str
    distance: float
    duration: int
    carbon_emission: float
    weather_condition: str
    traffic_condition: str
    created_at: datetime

    class Config:
        orm_mode = True 