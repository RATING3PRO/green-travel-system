from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..models.schemas import RouteRequest, Route, UserPreference
from ..utils.route_optimizer import RouteOptimizer
from ..utils.weather_service import WeatherService
from ..utils.traffic_service import TrafficService
from datetime import datetime

router = APIRouter()
route_optimizer = RouteOptimizer()
weather_service = WeatherService()
traffic_service = TrafficService()

@router.post("/recommend", response_model=List[Dict[str, Any]])
async def recommend_routes(
    start_location: str,
    end_location: str,
    departure_time: datetime = None,
    consider_weather: bool = True,
    consider_traffic: bool = True
):
    """
    推荐路线
    """
    try:
        routes = route_optimizer.get_route_recommendations(
            start_location=start_location,
            end_location=end_location,
            departure_time=departure_time,
            consider_weather=consider_weather,
            consider_traffic=consider_traffic
        )
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_route_history():
    """
    获取历史路线
    """
    # 模拟历史数据
    return [
        {
            "id": 1,
            "date": "2024-03-23",
            "start_location": "北京西站",
            "end_location": "天安门",
            "total_distance": 5.2,
            "total_duration": 25,
            "total_carbon_emission": 0.8
        },
        {
            "id": 2,
            "date": "2024-03-22",
            "start_location": "王府井",
            "end_location": "北京南站",
            "total_distance": 7.5,
            "total_duration": 40,
            "total_carbon_emission": 1.2
        }
    ]

@router.get("/carbon-savings")
async def calculate_carbon_savings(route_id: str):
    """
    计算特定路线的碳排放节省量
    """
    try:
        savings = await route_optimizer.calculate_carbon_savings(route_id)
        return {
            "route_id": route_id,
            "carbon_savings": savings,
            "unit": "kg_co2"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"碳排放计算失败: {str(e)}"
        )

@router.post("/user-preferences")
async def update_user_preferences(preferences: UserPreference):
    """
    更新用户出行偏好
    """
    try:
        # 保存用户偏好
        # TODO: 实现数据库存储
        return preferences
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新用户偏好失败: {str(e)}"
        ) 