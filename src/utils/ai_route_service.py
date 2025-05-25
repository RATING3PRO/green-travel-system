from typing import Dict, Any, List
import aiohttp
from src.utils.ai_service import ai_service
from src.utils.weather_service import weather_service
from src.utils.traffic_service import traffic_service

class AIRouteService:
    async def get_route_suggestion(self, start: str, end: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """基于天气、交通和用户偏好提供智能路线建议"""
        # 获取实时天气和交通数据
        weather_data = await weather_service.get_weather_data()
        traffic_data = await traffic_service.get_traffic_data()
        
        # 构建提示词
        prompt = f"""基于以下信息为用户推荐最佳出行方案：
        - 出发地：{start}
        - 目的地：{end}
        - 天气状况：温度{weather_data['temperature']}℃，{weather_data['description']}
        - 交通状况：拥堵指数{traffic_data['congestion_index']}，平均车速{traffic_data['average_speed']}km/h
        """
        
        if user_preferences:
            prompt += f"\n用户偏好：{str(user_preferences)}"
            
        # 调用AI服务获取建议
        response = await ai_service.get_travel_advice(prompt)
        
        return {
            "status": "success",
            "suggestion": response,
            "weather": weather_data,
            "traffic": traffic_data
        }
    
    async def analyze_route_options(self, routes: List[Dict]) -> Dict[str, Any]:
        """分析多条路线并提供智能建议"""
        routes_info = []
        for route in routes:
            routes_info.append({
                "距离": f"{int(route['distance'])/1000}公里",
                "预计时间": f"{int(route['duration'])/60}分钟",
                "路段数": len(route['steps'])
            })
            
        prompt = f"""分析以下路线方案并推荐最佳选择：
        {str(routes_info)}
        
        请考虑：
        1. 路程时间与距离的平衡
        2. 路段复杂度（转弯、红绿灯等）
        3. 当前天气和交通状况的影响
        """
        
        analysis = await ai_service.get_travel_advice(prompt)
        
        return {
            "status": "success",
            "analysis": analysis,
            "routes": routes_info
        }

ai_route_service = AIRouteService() 