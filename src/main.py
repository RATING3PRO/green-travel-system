from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import uvicorn
from src.api import routes, users
from src.models.database import create_tables
from src.utils.auth import get_db
from src.config.settings import settings
from src.utils.osm_service import osm_service
from src.utils.route_planner import route_planner
from src.utils.weather_service import weather_service
from src.utils.traffic_service import traffic_service
from src.utils.route_service import route_service
from src.models.schemas import Location, RouteRequest
from src.api.auth import router as auth_router
import os

app = FastAPI(
    title="城市绿色出行优化系统",
    description="AI赋能的城市绿色出行优化系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册认证路由
app.include_router(auth_router)

# 静态文件服务
static_path = os.path.join(os.path.dirname(__file__), "static")
templates_path = os.path.join(os.path.dirname(__file__), "frontend", "templates")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 模板配置
templates = Jinja2Templates(directory=templates_path)

# 注册路由
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"]
)

app.include_router(
    routes.router,
    prefix="/api/v1/routes",
    tags=["routes"]
)

@app.on_event("startup")
async def startup_event():
    """启动时执行的事件"""
    # 创建数据库表
    create_tables()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """渲染主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/v1/geocode")
async def geocode(address: str):
    """地理编码服务"""
    try:
        result = await osm_service.geocode(address)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/weather")
async def get_weather_info(lat: float, lon: float):
    """获取指定位置的天气信息"""
    try:
        result = await weather_service.get_weather(lat, lon)
        if result["status"] == "1":
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/route")
async def get_route(
    origin: str,
    destination: str,
    consider_weather: bool = True,
    max_walking_distance: int = 2000,
    preferred_modes: str = "walking,bus,subway"
):
    """综合路线规划服务"""
    try:
        # 解析起点和终点坐标
        origin_lat, origin_lon = map(float, origin.split(","))
        dest_lat, dest_lon = map(float, destination.split(","))
        
        # 获取天气信息
        if consider_weather:
            weather_info = await weather_service.get_weather(origin_lat, origin_lon)
            if weather_info["status"] == "0":
                raise HTTPException(status_code=500, detail="无法获取天气信息")
            
            # 如果天气不适合户外活动，返回提示
            if not weather_info["weather"]["is_suitable_for_outdoor"]:
                return {
                    "status": "0",
                    "warning": "当前天气不适合户外活动",
                    "weather": weather_info["weather"]
                }
        
        # 设置路线偏好
        preferences = {
            "max_walking_distance": max_walking_distance,
            "preferred_modes": preferred_modes.split(",")
        }
        
        # 计算路线
        route_result = await route_planner.calculate_multi_modal_route(
            origin_lat,
            origin_lon,
            dest_lat,
            dest_lon,
            preferences
        )
        
        if route_result["status"] == "1":
            return route_result
        else:
            raise HTTPException(status_code=500, detail="路线规划失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transit/nearby")
async def get_nearby_transit(lat: float, lon: float, radius: int = 1000):
    """获取周边公交和地铁站"""
    try:
        result = await route_planner.get_transit_stops(lat, lon, radius)
        return {"status": "1", "stops": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/bikes/nearby")
async def get_nearby_bikes(lat: float, lon: float, radius: int = 1000):
    """获取周边共享单车站点"""
    try:
        result = await route_planner.get_bike_stations(lat, lon, radius)
        return {"status": "1", "stations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/traffic")
async def get_traffic_info():
    """获取实时交通状况"""
    try:
        result = await traffic_service.get_traffic_status()
        if result["status"] == "1":
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/route")
async def plan_route(route_request: RouteRequest):
    """规划路线"""
    result = await route_service.plan_route(
        route_request.start_location,
        route_request.end_location
    )
    if result["status"] == "0":
        raise HTTPException(status_code=500, detail=result["error"])
    return result

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 