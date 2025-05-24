import  
from src.utils.weather_service import weather_service

async def test_weather():
    # 测试北京市的天气（使用北京的经纬度）
    result = await weather_service.get_weather(39.9042, 116.4074)
    print(result)

# 运行测试
asyncio.run(test_weather())