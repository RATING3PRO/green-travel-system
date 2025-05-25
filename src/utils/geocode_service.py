import aiohttp
from src.config.settings import settings

class GeocodeService:
    def __init__(self):
        self.base_url = "https://api.map.baidu.com/geocoding/v3"
        self.ak = settings.BAIDU_MAP_AK  # 从配置中获取API密钥

    async def geocode(self, address: str) -> dict:
        """将地址转换为经纬度坐标"""
        params = {
            "address": address,
            "output": "json",
            "ak": self.ak
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as resp:
                    data = await resp.json()
                    
                    if data["status"] == 0 and "result" in data:
                        location = data["result"]["location"]
                        return {
                            "status": "success",
                            "location": {
                                "lng": location["lng"],
                                "lat": location["lat"]
                            }
                        }
                    return {
                        "status": "error",
                        "message": data.get("message", "地址解析失败")
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

geocode_service = GeocodeService() 