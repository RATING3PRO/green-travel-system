# AI赋能的城市绿色出行优化系统

## Update at 25/05/25
已将地图API更换为百度
内置的百度地图API已经停用，请自行更改

## 项目简介
本项目是一个基于人工智能的城市绿色出行优化系统，旨在通过AI技术分析城市出行数据，为用户提供个性化的绿色出行方案，同时为城市管理者提供决策支持。

## 主要功能
- 智能出行路线推荐
- 实时交通流量分析
- 碳排放计算
- 个性化用户画像
- 交通拥堵预测
- 数据可视化展示

## 技术架构
- 后端：Python FastAPI
- AI模型：TensorFlow, Scikit-learn
- 数据存储：MongoDB, SQLAlchemy
- 地理信息：GeoPandas, OSMnx
- 前端：Dash, Plotly
- API文档：Swagger/OpenAPI

## 快速开始

### 环境要求
- Python 3.8+
- MongoDB
- 相关Python包（见requirements.txt）

### 安装步骤
1. 克隆项目
```bash
git clone [项目地址]
cd green-travel-ai
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
复制`.env.example`为`.env`并填写相关配置

5. 运行项目
```bash
uvicorn src.main:app --reload
```

## 项目结构
```
src/
├── api/          # API接口
├── models/       # AI模型
├── utils/        # 工具函数
├── frontend/     # 前端界面
├── data/         # 数据处理
└── config/       # 配置文件
tests/            # 测试文件
docs/             # 文档
```

## 开发团队
无

## 联系我
xiesmail2000@gmail.com
