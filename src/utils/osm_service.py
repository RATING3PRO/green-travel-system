import aiohttp
from typing import Dict, Any
import asyncio

class OSMService:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.osrm_url = "https://router.project-osrm.org"
        self.headers = {
            "User-Agent": "GreenTravelApp/1.0"  # OpenStreetMap要求提供User-Agent
        }
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10秒超时
        self.base_url = "https://nominatim.openstreetmap.org/search"
    
    async def geocode(self, address: str) -> Dict[str, Any]:
        """将地址转换为坐标"""
        try:
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "accept-language": "zh-CN"
            }
            
            headers = {
                "User-Agent": "GreenTransportApp/1.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            location = data[0]
                            return {
                                "status": "1",
                                "location": {
                                    "latitude": float(location["lat"]),
                                    "longitude": float(location["lon"]),
                                    "address": location.get("display_name", "")
                                }
                            }
                        return {"status": "0", "error": "未找到该地址"}
                    return {"status": "0", "error": f"地理编码请求失败: {response.status}"}
        except Exception as e:
            print(f"地理编码错误: {str(e)}")
            return {"status": "0", "error": f"地理编码失败: {str(e)}"}
    
    async def calculate_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """路径规划服务"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # OSRM需要经度在前，纬度在后
                coords = f"{origin.split(',')[1]},{origin.split(',')[0]};{destination.split(',')[1]},{destination.split(',')[0]}"
                url = f"{self.osrm_url}/route/v1/foot/{coords}"
                params = {
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == "Ok":
                            route = data["routes"][0]
                            return {
                                "status": "1",
                                "route": {
                                    "distance": route["distance"],
                                    "duration": route["duration"],
                                    "geometry": route["geometry"]
                                }
                            }
                        return {"status": "0", "error": "无法规划路线"}
                    else:
                        return {"status": "0", "error": f"路径规划服务错误 (HTTP {response.status})"}
        except asyncio.TimeoutError:
            return {"status": "0", "error": "请求超时，请稍后重试"}
        except Exception as e:
            return {"status": "0", "error": f"路径规划请求失败: {str(e)}"}
    
    async def search_around(self, location: str, keywords: str, radius: int = 1000) -> Dict[str, Any]:
        """周边搜索服务"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                lat, lon = location.split(",")
                params = {
                    "format": "json",
                    "lat": lat,
                    "lon": lon,
                    "q": keywords,
                    "limit": 10,
                    "radius": radius,
                    "countrycodes": "cn"
                }
                
                # 添加延迟以遵守Nominatim使用政策
                await asyncio.sleep(1)
                
                async with session.get(
                    f"{self.nominatim_url}/search",
                    params=params,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "1",
                            "pois": [{
                                "name": item["display_name"],
                                "location": f"{item['lat']},{item['lon']}",
                                "distance": item.get("distance", "未知")
                            } for item in data]
                        }
                    else:
                        return {"status": "0", "error": f"周边搜索服务错误 (HTTP {response.status})"}
        except asyncio.TimeoutError:
            return {"status": "0", "error": "请求超时，请稍后重试"}
        except Exception as e:
            return {"status": "0", "error": f"周边搜索请求失败: {str(e)}"}

osm_service = OSMService() 