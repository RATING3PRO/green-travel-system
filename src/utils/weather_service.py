import aiohttp
from typing import Dict, Any
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class WeatherService:
    def __init__(self):
        # 使用固定的天气数据
        self.weather_data = {
            "temperature": 18.4,
            "apparent_temperature": 18.4,
            "weather_description": "晴天",
            "humidity": 49,
            "wind_speed": 3.3,
            "wind_direction": "北风"
        }
    
    async def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """获取指定位置的天气信息"""
        try:
            return {
                "status": "1",
                "weather": self.weather_data
            }
        except Exception as e:
            print(f"获取天气信息时发生错误：{str(e)}")
            return {"status": "0", "error": f"获取天气信息失败: {str(e)}"}

weather_service = WeatherService() 