from typing import Dict, List, Any
import aiohttp
import random
from datetime import datetime

class RoutePlanner:
    def __init__(self):
        self.osrm_url = "https://router.project-osrm.org/route/v1"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.transit_modes = ["walking", "cycling", "bus", "subway"]
    
    async def get_transit_stops(self, lat: float, lon: float, radius: int = 1000) -> List[Dict]:
        """获取指定位置周边的公交和地铁站"""
        query = f"""
        [out:json];
        (
          node["highway"="bus_stop"](around:{radius},{lat},{lon});
          node["railway"="station"](around:{radius},{lat},{lon});
        );
        out body;
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.overpass_url, params={"data": query}) as response:
                data = await response.json()
                return [{
                    "id": element["id"],
                    "type": "bus_stop" if element.get("tags", {}).get("highway") == "bus_stop" else "subway",
                    "name": element.get("tags", {}).get("name", "未命名站点"),
                    "location": {
                        "lat": element["lat"],
                        "lon": element["lon"]
                    }
                } for element in data.get("elements", [])]

    async def get_bike_stations(self, lat: float, lon: float, radius: int = 1000) -> List[Dict]:
        """获取共享单车站点"""
        query = f"""
        [out:json];
        (
          node["amenity"="bicycle_rental"](around:{radius},{lat},{lon});
        );
        out body;
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.overpass_url, params={"data": query}) as response:
                data = await response.json()
                return [{
                    "id": element["id"],
                    "name": element.get("tags", {}).get("name", "共享单车站点"),
                    "operator": element.get("tags", {}).get("operator", "未知运营商"),
                    "location": {
                        "lat": element["lat"],
                        "lon": element["lon"]
                    }
                } for element in data.get("elements", [])]

    async def calculate_multi_modal_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        preferences: Dict = None
    ) -> Dict[str, Any]:
        """计算多模式路线"""
        if preferences is None:
            preferences = {
                "max_walking_distance": 2000,  # 最大步行距离（米）
                "preferred_modes": ["walking", "bus", "subway"]  # 偏好的交通方式
            }

        # 获取周边公交站点
        nearby_transit = await self.get_transit_stops(start_lat, start_lon, 1000)
        
        # 获取周边共享单车站点
        nearby_bikes = await self.get_bike_stations(start_lat, start_lon, 1000)

        # 根据偏好选择路线
        routes = []
        total_distance = 0
        total_duration = 0
        
        # 模拟路段生成（实际项目中应该根据真实数据计算）
        for mode in preferences["preferred_modes"]:
            if mode == "walking":
                segment = {
                    "mode": "walking",
                    "distance": random.uniform(500, 1500),
                    "duration": random.uniform(10, 30),
                    "start_point": {"lat": start_lat, "lon": start_lon},
                    "end_point": {"lat": start_lat + 0.01, "lon": start_lon + 0.01}
                }
            elif mode == "bus":
                if nearby_transit:
                    segment = {
                        "mode": "bus",
                        "distance": random.uniform(2000, 5000),
                        "duration": random.uniform(15, 45),
                        "start_station": nearby_transit[0],
                        "end_station": {
                            "name": "目标公交站",
                            "location": {"lat": end_lat - 0.01, "lon": end_lon - 0.01}
                        }
                    }
            elif mode == "subway":
                if nearby_transit:
                    segment = {
                        "mode": "subway",
                        "distance": random.uniform(5000, 15000),
                        "duration": random.uniform(20, 60),
                        "start_station": nearby_transit[0],
                        "end_station": {
                            "name": "目标地铁站",
                            "location": {"lat": end_lat - 0.005, "lon": end_lon - 0.005}
                        }
                    }
            
            if "segment" in locals():
                routes.append(segment)
                total_distance += segment["distance"]
                total_duration += segment["duration"]
                del segment

        return {
            "status": "1",
            "route": {
                "distance": total_distance,
                "duration": total_duration,
                "segments": routes,
                "nearby_transit": nearby_transit,
                "nearby_bikes": nearby_bikes
            }
        }

route_planner = RoutePlanner() 