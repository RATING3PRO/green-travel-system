from typing import Dict, Any, List
import aiohttp
from ..models.schemas import Location
import polyline
import random
from src.config.settings import settings

class RouteService:
    def __init__(self):
        self.base_url = "https://restapi.amap.com/v3/direction/driving"
    
    async def plan_route(self, origin: str, destination: str) -> Dict[str, Any]:
        params = {
            "key": settings.AMAP_API_KEY,
            "origin": origin,
            "destination": destination,
            "strategy": 2,  # 2=速度优先
            "extensions": "all"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)
                    return {"status": "error", "message": "API请求失败"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _parse_response(self, data: Dict) -> Dict:
        if data["status"] != "1":
            return {"status": "error", "message": data.get("info", "未知错误")}
        
        route = data["route"]["paths"][0]
        return {
            "status": "success",
            "distance": route["distance"],
            "duration": route["duration"],
            "steps": [
                {
                    "instruction": step["instruction"],
                    "distance": step["distance"],
                    "polyline": step["polyline"].split(";")
                } for step in route["steps"]
            ],
            "polyline": route["polyline"].split(";")
        }

    def _extract_coordinates(self, coords: List[List[float]]) -> List[List[float]]:
        """提取并转换坐标点"""
        return [[coord[1], coord[0]] for coord in coords]  # 转换为[lat, lng]格式
    
    def _process_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理路线步骤信息"""
        processed_steps = []
        for step in steps:
            processed_steps.append({
                "instruction": step["maneuver"]["type"],
                "distance": round(step["distance"]),
                "duration": round(step["duration"] / 60),
                "mode": self._get_travel_mode(step)
            })
        return processed_steps
    
    def _get_travel_mode(self, step: Dict[str, Any]) -> str:
        """根据步骤信息确定出行方式"""
        # 这里可以根据实际情况判断出行方式
        return "car"  # 默认使用小汽车模式

route_service = RouteService() 