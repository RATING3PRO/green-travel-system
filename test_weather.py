import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.weather_service import weather_service

async def test_weather():
    # 测试北京市的天气（使用北京的经纬度）
    print("正在获取北京市天气信息...")
    result = await weather_service.get_weather(39.9042, 116.4074)
    print("\n天气信息：")
    if result["status"] == "1":
        weather = result["weather"]
        print(f"温度: {weather['temperature']}°C")
        print(f"体感温度: {weather['feels_like']}°C")
        print(f"天气状况: {weather['description']}")
        print(f"湿度: {weather['humidity']}%")
        print(f"风速: {weather['wind_speed']}m/s")
        print(f"风向: {weather['wind_direction']}")
        print(f"能见度: {weather['visibility']}km")
        print(f"降水量: {weather['precipitation']}mm")
        print(f"是否适合户外活动: {'是' if weather['is_suitable_for_outdoor'] else '否'}")
        print(f"是否下雨: {'是' if weather['is_raining'] else '否'}")
    else:
        print(f"获取天气信息失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_weather()) 