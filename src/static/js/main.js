// 全局变量
let map = null;
let currentUser = null;
let routeLayer = null;
let markers = [];
let currentRoute = null;
let startMarker = null;
let endMarker = null;

// DOM 元素
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const userInfo = document.getElementById('userInfo');
const username = document.getElementById('username');
const notification = document.getElementById('notification');

// API 基础URL
const API_BASE_URL = '/api/v1';

// 地图相关变量
let routePolyline = null;

// 工具函数
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function setAuthToken(token) {
    if (token) {
        localStorage.setItem('token', token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
    }
}

// 初始化地图
function initMap() {
    map = L.map('map-container').setView([39.9042, 116.4074], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

// 显示天气信息
async function displayWeather(lat, lon) {
    try {
        const response = await fetch(`/api/v1/weather?lat=${lat}&lon=${lon}`);
        if (!response.ok) {
            throw new Error('获取天气信息失败');
        }
        
        const weatherData = await response.json();
        
        // 更新天气信息显示
        document.querySelector('#weatherInfo .temp').textContent = weatherData.temperature.toFixed(1);
        document.querySelector('#weatherInfo .feels-like').textContent = weatherData.apparent_temperature.toFixed(1);
        document.querySelector('#weatherInfo .description').textContent = weatherData.weather_description;
        document.querySelector('#weatherInfo .humidity').textContent = weatherData.humidity;
        document.querySelector('#weatherInfo .wind-speed').textContent = weatherData.wind_speed.toFixed(1);
        document.querySelector('#weatherInfo .wind-direction').textContent = weatherData.wind_direction;
        
        // 显示天气信息区域
        document.getElementById('weatherInfo').style.display = 'block';
        
    } catch (error) {
        showNotification('获取天气信息失败: ' + error.message, 'error');
        console.error('天气信息获取错误:', error);
    }
}

// 用户认证相关函数
async function login(username, password) {
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/v1/auth/token', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '登录失败');
        }
        
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        
        // 更新UI显示
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        document.getElementById('userInfo').style.display = 'flex';
        
        // 获取并显示用户信息
        await getUserInfo();
        
        // 关闭登录模态框
        document.getElementById('loginModal').style.display = 'none';
        
        showNotification('登录成功', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '注册失败');
        }
        
        const data = await response.json();
        showNotification(data.message, 'success');
        
        // 关闭注册模态框
        document.getElementById('registerModal').style.display = 'none';
        
        // 自动填充登录表单并显示
        document.querySelector('#loginForm input[name="username"]').value = username;
        document.querySelector('#loginForm input[name="password"]').value = password;
        document.getElementById('loginModal').style.display = 'block';
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function getUserInfo() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('未登录');
        }
        
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('获取用户信息失败');
        }
        
        const data = await response.json();
        document.getElementById('username').textContent = data.username;
    } catch (error) {
        console.error('获取用户信息失败:', error);
    }
}

function logout() {
    localStorage.removeItem('token');
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('registerBtn').style.display = 'block';
    document.getElementById('userInfo').style.display = 'none';
    document.getElementById('username').textContent = '';
    showNotification('已退出登录', 'info');
}

// 显示路线
async function displayRoute(startLocation, endLocation) {
    try {
        clearMap();
        console.log('开始规划路线:', { startLocation, endLocation });
        
        // 获取起点坐标
        console.log('正在获取起点坐标...');
        const startResponse = await fetch(`/api/v1/geocode?address=${encodeURIComponent(startLocation)}`);
        const startData = await startResponse.json();
        console.log('起点坐标响应:', startData);
        
        if (startData.status !== "1") {
            throw new Error(startData.error || "无法找到起点位置");
        }
        
        // 获取终点坐标
        console.log('正在获取终点坐标...');
        const endResponse = await fetch(`/api/v1/geocode?address=${encodeURIComponent(endLocation)}`);
        const endData = await endResponse.json();
        console.log('终点坐标响应:', endData);
        
        if (endData.status !== "1") {
            throw new Error(endData.error || "无法找到终点位置");
        }
        
        // 添加起点和终点标记
        console.log('添加地图标记...');
        const startMarker = L.marker([startData.location.lat, startData.location.lng])
            .bindPopup("起点: " + startLocation)
            .addTo(map);
        const endMarker = L.marker([endData.location.lat, endData.location.lng])
            .bindPopup("终点: " + endLocation)
            .addTo(map);
        markers.push(startMarker, endMarker);
        
        // 获取天气信息
        console.log('正在获取天气信息...');
        await displayWeather(startData.location.lat, startData.location.lng);
        
        // 获取路线规划
        console.log('正在规划路线...');
        const routeResponse = await fetch(
            `/api/v1/route?origin=${startData.location.lat},${startData.location.lng}&destination=${endData.location.lat},${endData.location.lng}&consider_weather=true`
        );
        const routeData = await routeResponse.json();
        console.log('路线规划响应:', routeData);
        
        if (routeData.status === "1") {
            // 绘制路线
            console.log('绘制路线...');
            const coordinates = routeData.route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
            routeLayer = L.polyline(coordinates, {
                color: '#4CAF50',
                weight: 5,
                opacity: 0.8
            }).addTo(map);
            
            // 调整地图视图以显示整个路线
            map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
            
            // 更新路线信息
            document.getElementById('totalDistance').textContent = (routeData.route.distance / 1000).toFixed(1) + '公里';
            document.getElementById('totalTime').textContent = Math.round(routeData.route.duration / 60) + '分钟';
            
            // 显示路线详情部分
            document.querySelector('.route-details').style.display = 'block';
            
            console.log('路线规划完成');
        } else if (routeData.warning) {
            console.log('收到天气警告:', routeData.warning);
            showNotification(routeData.warning, 'warning');
            // 显示天气提示
            if (routeData.weather) {
                await displayWeather(startData.location.lat, startData.location.lng);
            }
        } else {
            throw new Error(routeData.error || "无法规划路线");
        }
        
    } catch (error) {
        console.error('路线规划错误:', error);
        showNotification(error.message, 'error');
    }
}

// 清除地图上的所有标记和路线
function clearMap() {
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

// 显示交通状况
async function displayTraffic() {
    try {
        console.log('开始获取交通状况...');
        const response = await fetch('/api/v1/traffic');
        const data = await response.json();
        console.log('交通状况响应:', data);
        
        if (data.status === "1") {
            const traffic = data.traffic;
            
            // 更新拥堵指数和状态
            document.querySelector('.congestion-index .value').textContent = traffic.congestion_index.toFixed(3);
            document.querySelector('.congestion-index .status').textContent = `（${traffic.status}）`;
            
            // 更新周同比变化
            const weeklyChange = document.querySelector('.weekly-change .value');
            weeklyChange.textContent = `${traffic.weekly_change > 0 ? '+' : ''}${traffic.weekly_change.toFixed(2)}%`;
            weeklyChange.style.color = traffic.weekly_change > 0 ? '#f44336' : '#4CAF50';
            
            // 更新排名
            document.querySelector('.traffic-stats .stat-item:nth-child(1) .value').textContent = 
                `${traffic.rank.current}/${traffic.rank.total}`;
            
            // 更新平均速度
            document.querySelector('.traffic-stats .stat-item:nth-child(2) .value').textContent = 
                traffic.average_speed.toFixed(2);
            
            // 更新拥堵里程
            document.querySelector('.traffic-stats .stat-item:nth-child(3) .value').textContent = 
                traffic.congested_length.toFixed(2);
            
            // 更新月度最高拥堵指数
            const monthlyHighest = document.querySelector('.traffic-stats .stat-item:nth-child(4)');
            monthlyHighest.querySelector('.value').textContent = traffic.monthly_highest.index.toFixed(3);
            monthlyHighest.querySelector('.date').textContent = 
                `${traffic.monthly_highest.date} ${traffic.monthly_highest.day}`;
            
            console.log('交通状况显示完成');
        } else {
            console.error('获取交通状况失败:', data.error);
            showNotification(data.error || '获取交通状况失败', 'error');
        }
    } catch (error) {
        console.error('显示交通状况错误:', error);
        showNotification('获取交通状况失败: ' + error.message, 'error');
    }
}

// 初始化函数
async function init() {
    // 绑定路线规划按钮事件
    document.getElementById('planRouteBtn').addEventListener('click', handleRoutePlanning);
    
    // 获取并显示天气信息
    await displayWeather(39.9042, 116.4074); // 默认显示北京市中心的天气
    
    // 获取并显示交通状况
    await displayTraffic();
}

// 处理路线规划
async function handleRoutePlanning() {
    const startLocation = document.getElementById('startLocation').value;
    const endLocation = document.getElementById('endLocation').value;
    
    if (!startLocation || !endLocation) {
        showNotification('请输入起点和终点位置', 'warning');
        return;
    }
    
    try {
        // 清除之前的路线
        clearRoute();
        
        // 获取起点坐标
        const startCoords = await geocodeLocation(startLocation);
        if (!startCoords) {
            showNotification('无法找到起点位置', 'error');
            return;
        }
        
        // 获取终点坐标
        const endCoords = await geocodeLocation(endLocation);
        if (!endCoords) {
            showNotification('无法找到终点位置', 'error');
            return;
        }
        
        // 添加起点和终点标记
        addRouteMarkers(startCoords, endCoords);
        
        // 规划路线
        await planRoute(startCoords, endCoords);
        
        // 调整地图视野以显示完整路线
        fitMapToRoute();
        
    } catch (error) {
        console.error('路线规划错误:', error);
        showNotification('路线规划失败: ' + error.message, 'error');
    }
}

// 地理编码：将地址转换为坐标
async function geocodeLocation(address) {
    try {
        const response = await fetch(`/api/v1/geocode?address=${encodeURIComponent(address)}`);
        if (!response.ok) {
            throw new Error('地理编码请求失败');
        }
        const data = await response.json();
        if (data.status === "1" && data.location) {
            return {
                lat: data.location.latitude,
                lng: data.location.longitude
            };
        }
        throw new Error(data.error || '地理编码失败');
    } catch (error) {
        console.error('地理编码错误:', error);
        throw error;
    }
}

// 添加路线起点和终点标记
function addRouteMarkers(startCoords, endCoords) {
    // 清除现有标记
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    
    // 添加新标记
    startMarker = L.marker([startCoords.lat, startCoords.lng])
        .bindPopup('起点')
        .addTo(map);
    
    endMarker = L.marker([endCoords.lat, endCoords.lng])
        .bindPopup('终点')
        .addTo(map);
}

// 规划路线
async function planRoute(startCoords, endCoords) {
    try {
        const response = await fetch('/api/v1/route', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_location: startCoords,
                end_location: endCoords
            })
        });
        
        if (!response.ok) {
            throw new Error('路线规划请求失败');
        }
        
        const data = await response.json();
        if (data.status === "1" && data.route) {
            // 绘制路线
            currentRoute = L.polyline(data.route.coordinates, {
                color: '#4CAF50',
                weight: 5,
                opacity: 0.8
            }).addTo(map);
            
            // 更新路线信息
            updateRouteInfo(data.route);
            
            // 显示路线详情
            document.querySelector('.route-details').style.display = 'block';
        } else {
            throw new Error(data.error || '路线规划失败');
        }
    } catch (error) {
        console.error('规划路线错误:', error);
        throw error;
    }
}

// 更新路线信息
function updateRouteInfo(route) {
    document.getElementById('totalDistance').textContent = 
        route.distance < 1000 ? 
        `${route.distance}米` : 
        `${(route.distance/1000).toFixed(1)}公里`;
    
    document.getElementById('totalTime').textContent = 
        route.duration < 60 ? 
        `${route.duration}分钟` : 
        `${Math.floor(route.duration/60)}小时${route.duration%60}分钟`;
    
    // 更新路段信息
    const routeSegments = document.getElementById('routeSegments');
    routeSegments.innerHTML = route.steps.map(step => `
        <div class="route-step">
            <i class="fas ${getStepIcon(step.mode)}"></i>
            <span>${step.instruction}</span>
            <small>${step.distance}米 | ${step.duration}分钟</small>
        </div>
    `).join('');
}

// 获取路段图标
function getStepIcon(mode) {
    const icons = {
        'walk': 'fa-walking',
        'bus': 'fa-bus',
        'subway': 'fa-subway',
        'bike': 'fa-bicycle',
        'car': 'fa-car',
        'default': 'fa-arrow-right'
    };
    return icons[mode] || icons.default;
}

// 调整地图视野以显示完整路线
function fitMapToRoute() {
    if (currentRoute) {
        const bounds = currentRoute.getBounds();
        map.fitBounds(bounds, {
            padding: [50, 50]
        });
    }
}

// 清除路线
function clearRoute() {
    if (currentRoute) {
        map.removeLayer(currentRoute);
        currentRoute = null;
    }
    if (startMarker) {
        map.removeLayer(startMarker);
        startMarker = null;
    }
    if (endMarker) {
        map.removeLayer(endMarker);
        endMarker = null;
    }
    document.querySelector('.route-details').style.display = 'none';
}

// 事件监听器
document.addEventListener('DOMContentLoaded', () => {
    // 初始化地图
    initMap();

    // 检查是否已登录
    const token = localStorage.getItem('token');
    if (token) {
        setAuthToken(token);
        getUserInfo();
    }

    // 登录表单提交
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = e.target.username.value;
        const password = e.target.password.value;
        await login(username, password);
    });

    // 注册表单提交
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = e.target.username.value;
        const email = e.target.email.value;
        const password = e.target.password.value;
        await register(username, email, password);
    });

    // 路线规划按钮点击
    document.getElementById('planRouteBtn').addEventListener('click', async () => {
        const startLocation = document.getElementById('startLocation').value;
        const endLocation = document.getElementById('endLocation').value;
        
        if (!startLocation || !endLocation) {
            showNotification('请输入起点和终点位置', 'error');
            return;
        }
        
        await displayRoute(startLocation, endLocation);
    });

    // 模态框相关
    loginBtn.addEventListener('click', () => loginModal.style.display = 'block');
    registerBtn.addEventListener('click', () => registerModal.style.display = 'block');
    logoutBtn.addEventListener('click', logout);

    // 关闭模态框
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            loginModal.style.display = 'none';
            registerModal.style.display = 'none';
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) loginModal.style.display = 'none';
        if (e.target === registerModal) registerModal.style.display = 'none';
    });

    // 显示交通状况
    displayTraffic();
    
    // 每5分钟更新一次交通状况
    setInterval(displayTraffic, 5 * 60 * 1000);

    // 页面加载完成后初始化
    init();
}); 