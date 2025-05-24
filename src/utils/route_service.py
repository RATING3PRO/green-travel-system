from typing import Dict, Any, List
import aiohttp
from ..models.schemas import Location
import polyline
import random

class RouteService:
    def __init__(self):
        self.base_url = "https://router.project-osrm.org/route/v1"
        self.profile = "driving"  # 可选：driving, walking, cycling
        
    async def plan_route(self, start: Location, end: Location) -> Dict[str, Any]:
        """规划路线"""
        try:
            coordinates = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
            url = f"{self.base_url}/{self.profile}/{coordinates}"
            params = {
                "overview": "full",
                "geometries": "geojson",
                "steps": "true",
                "annotations": "true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["code"] == "Ok" and len(data["routes"]) > 0:
                            route = data["routes"][0]
                            return {
                                "status": "1",
                                "route": {
                                    "distance": round(route["distance"]),  # 米
                                    "duration": round(route["duration"] / 60),  # 分钟
                                    "coordinates": self._extract_coordinates(route["geometry"]["coordinates"]),
                                    "steps": self._process_steps(route["legs"][0]["steps"])
                                }
                            }
                    return {"status": "0", "error": "无法获取路线信息"}
        except Exception as e:
            print(f"路线规划错误: {str(e)}")
            return {"status": "0", "error": f"路线规划失败: {str(e)}"}
    
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