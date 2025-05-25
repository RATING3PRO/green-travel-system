from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
from src.utils.route_service import route_service
from src.utils.ai_route_service import ai_route_service
from src.utils.weather_service import weather_service
from src.utils.traffic_service import traffic_service

router = APIRouter(prefix="/api/v1/route", tags=["route"])

class RouteRequest(BaseModel):
    start: str  # 格式：经度,纬度
    end: str    # 格式：经度,纬度
    preferences: Optional[Dict] = None

class RouteAnalysisRequest(BaseModel):
    routes: List[Dict]

@router.post("/plan")
async def plan_route(request: RouteRequest):
    """规划路线"""
    try:
        result = await route_service.plan_route(request.start, request.end)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/smart-suggestion")
async def get_smart_route_suggestion(request: RouteRequest):
    """获取AI智能路线建议"""
    try:
        # 获取天气和交通数据
        weather_data = await weather_service.get_weather_data()
        traffic_data = await traffic_service.get_traffic_data()
        
        # 构建提示词
        prompt = f"""基于以下信息为用户推荐最佳出行方案：
        - 出发地：{request.start}
        - 目的地：{request.end}
        - 天气状况：温度{weather_data['temperature']}℃，{weather_data['description']}
        - 交通状况：拥堵指数{traffic_data['congestion_index']}，平均车速{traffic_data['average_speed']}km/h
        """
        
        if request.preferences:
            prompt += f"\n用户偏好：{str(request.preferences)}"
        
        # 获取AI建议
        suggestion = await ai_route_service.get_route_suggestion(
            request.start,
            request.end,
            request.preferences
        )
        
        return {
            "status": "success",
            "suggestion": suggestion["suggestion"],
            "weather": weather_data,
            "traffic": traffic_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_routes(request: RouteAnalysisRequest):
    """分析多条路线并提供智能建议"""
    try:
        result = await ai_route_service.analyze_route_options(request.routes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geocode")
async def geocode_address(address: str):
    """地理编码服务"""
    try:
        from src.utils.geocode_service import geocode_service
        location = await geocode_service.geocode(address)
        if location:
            return {"status": "success", "location": location}
        raise HTTPException(status_code=400, detail="无法解析该地址")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 