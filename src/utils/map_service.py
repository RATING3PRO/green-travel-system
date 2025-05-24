import aiohttp
from src.config.settings import settings

class MapService:
    def __init__(self):
        self.api_key = settings.AMAP_WEB_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def geocode(self, address: str) -> dict:
        """地理编码服务"""
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "address": address,
                "output": "JSON"
            }
            async with session.get(f"{self.base_url}/geocode/geo", params=params) as response:
                return await response.json()
    
    async def calculate_route(self, origin: str, destination: str) -> dict:
        """路径规划服务"""
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "origin": origin,
                "destination": destination,
                "output": "JSON",
                "extensions": "all"
            }
            async with session.get(f"{self.base_url}/direction/walking", params=params) as response:
                return await response.json()
    
    async def search_around(self, location: str, keywords: str, radius: int = 1000) -> dict:
        """周边搜索服务"""
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.api_key,
                "location": location,
                "keywords": keywords,
                "radius": radius,
                "output": "JSON"
            }
            async with session.get(f"{self.base_url}/place/around", params=params) as response:
                return await response.json()

map_service = MapService() 