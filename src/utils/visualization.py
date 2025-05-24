import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta
from ..models.database import TravelHistory, TrafficData, WeatherData
from sqlalchemy.orm import Session

class DataVisualization:
    def __init__(self, db: Session):
        self.db = db
        
    def create_travel_history_dashboard(self, user_id: int) -> Dict[str, Any]:
        """创建用户出行历史仪表板"""
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
            return {"error": "无出行记录"}
            
        # 创建图表
        figures = {
            "transport_mode_distribution": self._create_mode_distribution(history),
            "carbon_emission_trend": self._create_carbon_trend(history),
            "distance_by_weather": self._create_weather_analysis(history),
            "monthly_statistics": self._create_monthly_stats(history)
        }
        
        return figures
        
    def _create_mode_distribution(self, history: pd.DataFrame) -> Dict:
        """创建交通方式分布图"""
        mode_counts = history["transport_mode"].value_counts()
        
        fig = px.pie(
            values=mode_counts.values,
            names=mode_counts.index,
            title="出行方式分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        return fig.to_dict()
        
    def _create_carbon_trend(self, history: pd.DataFrame) -> Dict:
        """创建碳排放趋势图"""
        daily_carbon = history.groupby(
            history["created_at"].dt.date
        )["carbon_emission"].sum().reset_index()
        
        fig = px.line(
            daily_carbon,
            x="created_at",
            y="carbon_emission",
            title="每日碳排放趋势",
            labels={"carbon_emission": "碳排放量 (kg)", "created_at": "日期"}
        )
        
        return fig.to_dict()
        
    def _create_weather_analysis(self, history: pd.DataFrame) -> Dict:
        """创建天气影响分析图"""
        weather_distance = history.groupby(
            ["weather_condition", "transport_mode"]
        )["distance"].mean().reset_index()
        
        fig = px.bar(
            weather_distance,
            x="weather_condition",
            y="distance",
            color="transport_mode",
            title="不同天气条件下的出行距离",
            barmode="group",
            labels={
                "distance": "平均距离 (km)",
                "weather_condition": "天气状况",
                "transport_mode": "出行方式"
            }
        )
        
        return fig.to_dict()
        
    def _create_monthly_stats(self, history: pd.DataFrame) -> Dict:
        """创建月度统计图"""
        monthly_stats = history.groupby(
            history["created_at"].dt.to_period("M")
        ).agg({
            "distance": "sum",
            "carbon_emission": "sum",
            "duration": "mean"
        }).reset_index()
        
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "月度总距离",
                "月度碳排放",
                "平均行程时间",
                "出行方式占比"
            )
        )
        
        # 添加子图
        fig.add_trace(
            go.Bar(
                x=monthly_stats["created_at"].astype(str),
                y=monthly_stats["distance"],
                name="距离"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=monthly_stats["created_at"].astype(str),
                y=monthly_stats["carbon_emission"],
                name="碳排放"
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Line(
                x=monthly_stats["created_at"].astype(str),
                y=monthly_stats["duration"],
                name="时间"
            ),
            row=2, col=1
        )
        
        # 添加月度出行方式占比
        mode_by_month = history.groupby(
            [history["created_at"].dt.to_period("M"), "transport_mode"]
        ).size().unstack(fill_value=0)
        
        fig.add_trace(
            go.Bar(
                x=mode_by_month.index.astype(str),
                y=mode_by_month.iloc[:, 0],
                name=mode_by_month.columns[0]
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="月度统计概览")
        return fig.to_dict()
        
    def create_traffic_heatmap(self, date: datetime) -> Dict:
        """创建交通热力图"""
        # 获取指定日期的交通数据
        traffic_data = pd.DataFrame([
            {
                "latitude": float(d.location.split(",")[0]),
                "longitude": float(d.location.split(",")[1]),
                "congestion_level": d.congestion_level
            }
            for d in self.db.query(TrafficData).filter(
                TrafficData.timestamp.date() == date.date()
            ).all()
        ])
        
        if traffic_data.empty:
            return {"error": "无交通数据"}
            
        fig = px.density_mapbox(
            traffic_data,
            lat="latitude",
            lon="longitude",
            z="congestion_level",
            radius=10,
            center=dict(lat=traffic_data["latitude"].mean(),
                       lon=traffic_data["longitude"].mean()),
            zoom=11,
            mapbox_style="carto-positron",
            title="交通拥堵热力图"
        )
        
        return fig.to_dict()
        
    def create_environmental_impact_report(
        self,
        user_id: int,
        time_period: str = "month"
    ) -> Dict[str, Any]:
        """创建环境影响报告"""
        # 获取历史数据
        if time_period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=365)
            
        history = pd.DataFrame([
            {
                "transport_mode": h.transport_mode,
                "distance": h.distance,
                "carbon_emission": h.carbon_emission,
                "created_at": h.created_at
            }
            for h in self.db.query(TravelHistory).filter(
                TravelHistory.user_id == user_id,
                TravelHistory.created_at >= start_date
            ).all()
        ])
        
        if history.empty:
            return {"error": "无环境影响数据"}
            
        # 创建环境影响图表
        figures = {
            "carbon_savings": self._create_carbon_savings_chart(history),
            "green_travel_ratio": self._create_green_travel_ratio(history),
            "impact_comparison": self._create_impact_comparison(history)
        }
        
        return figures
        
    def _create_carbon_savings_chart(self, history: pd.DataFrame) -> Dict:
        """创建碳排放节省图表"""
        car_emission_factor = 0.2  # kg CO2/km
        
        history["baseline_emission"] = history["distance"] * car_emission_factor
        history["savings"] = history["baseline_emission"] - history["carbon_emission"]
        
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=history["created_at"],
                y=history["baseline_emission"],
                name="基准排放量"
            )
        )
        fig.add_trace(
            go.Bar(
                x=history["created_at"],
                y=history["carbon_emission"],
                name="实际排放量"
            )
        )
        
        fig.update_layout(
            title="碳排放节省情况",
            barmode="group",
            xaxis_title="日期",
            yaxis_title="碳排放量 (kg CO2)"
        )
        
        return fig.to_dict()
        
    def _create_green_travel_ratio(self, history: pd.DataFrame) -> Dict:
        """创建绿色出行比例图表"""
        green_modes = ["walking", "cycling", "shared_bike"]
        history["is_green"] = history["transport_mode"].isin(green_modes)
        
        green_ratio = history["is_green"].value_counts(normalize=True)
        
        fig = px.pie(
            values=green_ratio.values,
            names=["绿色出行", "常规出行"],
            title="绿色出行比例",
            color_discrete_sequence=["#2ecc71", "#e74c3c"]
        )
        
        return fig.to_dict()
        
    def _create_impact_comparison(self, history: pd.DataFrame) -> Dict:
        """创建环境影响对比图表"""
        impact_by_mode = history.groupby("transport_mode").agg({
            "distance": "sum",
            "carbon_emission": "sum"
        }).reset_index()
        
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("总行程距离", "总碳排放量")
        )
        
        fig.add_trace(
            go.Bar(
                x=impact_by_mode["transport_mode"],
                y=impact_by_mode["distance"],
                name="距离"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=impact_by_mode["transport_mode"],
                y=impact_by_mode["carbon_emission"],
                name="碳排放"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="各出行方式环境影响对比",
            showlegend=True
        )
        
        return fig.to_dict() 