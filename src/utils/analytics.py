import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..models.database import TravelHistory, TrafficData, WeatherData
from sqlalchemy.orm import Session

class TravelAnalytics:
    def __init__(self, db: Session):
        self.db = db
        
    def analyze_user_patterns(self, user_id: int) -> Dict[str, Any]:
        """分析用户出行模式"""
        # 获取用户历史数据
        history = pd.DataFrame([
            {
                "transport_mode": h.transport_mode,
                "distance": h.distance,
                "duration": h.duration,
                "carbon_emission": h.carbon_emission,
                "created_at": h.created_at,
                "weather_condition": h.weather_condition
            }
            for h in self.db.query(TravelHistory).filter(
                TravelHistory.user_id == user_id
            ).all()
        ])
        
        if history.empty:
            return {
                "frequent_mode": None,
                "avg_carbon_emission": 0,
                "total_distance": 0,
                "weather_impact": {}
            }
            
        analysis = {
            "frequent_mode": history["transport_mode"].mode().iloc[0],
            "avg_carbon_emission": history["carbon_emission"].mean(),
            "total_distance": history["distance"].sum(),
            "weather_impact": self._analyze_weather_impact(history)
        }
        
        return analysis
        
    def _analyze_weather_impact(self, history: pd.DataFrame) -> Dict[str, Any]:
        """分析天气对出行方式的影响"""
        weather_impact = history.groupby(["weather_condition", "transport_mode"]).size()
        return weather_impact.to_dict()
        
    def predict_traffic_congestion(
        self,
        location: Dict[str, float],
        time: datetime
    ) -> float:
        """预测交通拥堵程度"""
        # 获取历史交通数据
        historical_data = pd.DataFrame([
            {
                "hour": d.timestamp.hour,
                "day_of_week": d.timestamp.weekday(),
                "congestion_level": d.congestion_level
            }
            for d in self.db.query(TrafficData).filter(
                TrafficData.timestamp >= time - timedelta(days=30)
            ).all()
        ])
        
        if historical_data.empty:
            return 0.5  # 默认中等拥堵程度
            
        # 简单时间序列预测
        target_hour = time.hour
        target_day = time.weekday()
        
        similar_conditions = historical_data[
            (historical_data["hour"] == target_hour) &
            (historical_data["day_of_week"] == target_day)
        ]
        
        if similar_conditions.empty:
            return 0.5
            
        return similar_conditions["congestion_level"].mean()
        
    def cluster_users_by_behavior(self, n_clusters: int = 3) -> Dict[str, List[int]]:
        """根据用户行为进行聚类"""
        # 获取所有用户的行为数据
        user_behaviors = pd.DataFrame([
            {
                "user_id": h.user_id,
                "avg_distance": h.distance,
                "avg_carbon": h.carbon_emission,
                "transport_preference": h.transport_mode
            }
            for h in self.db.query(TravelHistory).all()
        ])
        
        if user_behaviors.empty:
            return {"clusters": []}
            
        # 数据预处理
        scaler = StandardScaler()
        features = scaler.fit_transform(
            user_behaviors[["avg_distance", "avg_carbon"]]
        )
        
        # K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features)
        
        # 整理结果
        result = {}
        for i in range(n_clusters):
            result[f"cluster_{i}"] = user_behaviors[clusters == i]["user_id"].tolist()
            
        return result
        
    def calculate_environmental_impact(
        self,
        user_id: int,
        time_period: str = "month"
    ) -> Dict[str, float]:
        """计算环境影响"""
        # 获取指定时期的出行记录
        if time_period == "month":
            start_date = datetime.now() - timedelta(days=30)
        elif time_period == "year":
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = datetime.now() - timedelta(days=7)
            
        history = self.db.query(TravelHistory).filter(
            TravelHistory.user_id == user_id,
            TravelHistory.created_at >= start_date
        ).all()
        
        # 计算各项指标
        total_carbon = sum(h.carbon_emission for h in history)
        total_distance = sum(h.distance for h in history)
        green_trips = sum(1 for h in history if h.transport_mode in ["walking", "cycling"])
        
        return {
            "total_carbon_emission": total_carbon,
            "total_distance": total_distance,
            "green_trips_count": green_trips,
            "carbon_saved": self._calculate_carbon_savings(history)
        }
        
    def _calculate_carbon_savings(self, history: List[TravelHistory]) -> float:
        """计算碳排放节省量"""
        # 假设所有行程都使用私家车的基准碳排放
        car_emission_factor = 0.2  # kg CO2/km
        
        actual_emissions = sum(h.carbon_emission for h in history)
        baseline_emissions = sum(h.distance * car_emission_factor for h in history)
        
        return baseline_emissions - actual_emissions 