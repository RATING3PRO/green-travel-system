// 初始化事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 发送消息按钮点击事件
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    
    // 输入框回车事件
    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // 路线规划按钮点击事件
    document.getElementById('planRouteBtn').addEventListener('click', planRoute);
});

// 发送消息到AI助手
async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (message) {
        showMessage('用户', message, 'user');
        userInput.value = '';
        
        try {
            const response = await fetch('/api/v1/ai/advice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_input: message
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                showMessage('AI助手', data.response, 'ai');
            } else {
                showMessage('系统', '获取AI回复失败，请稍后重试。', 'system');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('系统', '发生错误，请稍后重试。', 'system');
        }
    }
}

// 显示消息在聊天窗口
function showMessage(sender, message, type) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.innerHTML = `
        <div class="message-header">${sender}</div>
        <div class="message-content">${message}</div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 新增坐标转换函数
function parsePolyline(points) {
    return points.map(p => {
        const [lng, lat] = p.split(',');
        return [parseFloat(lat), parseFloat(lng)];
    });
}

// 获取智能路线建议
async function getSmartRouteSuggestion(start, end, preferences = null) {
    try {
        const response = await fetch('/api/v1/route/smart-suggestion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                start: start,
                end: end,
                preferences: preferences
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            // 显示AI建议
            showAIAdvice(data.suggestion);
            // 显示天气和交通信息
            updateWeatherTrafficInfo(data.weather, data.traffic);
        } else {
            throw new Error(data.message || '获取建议失败');
        }
    } catch (error) {
        showNotification(`获取智能建议失败: ${error.message}`);
    }
}

// 分析路线选项
async function analyzeRouteOptions(routes) {
    try {
        const response = await fetch('/api/v1/route/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ routes: routes })
        });

        const data = await response.json();
        if (data.status === 'success') {
            showRouteAnalysis(data.analysis);
        } else {
            throw new Error(data.message || '分析失败');
        }
    } catch (error) {
        showNotification(`路线分析失败: ${error.message}`);
    }
}

// 显示AI建议
function showAIAdvice(advice) {
    const adviceContainer = document.getElementById('aiAdvice');
    const adviceContent = adviceContainer.querySelector('.ai-advice-content');
    adviceContent.textContent = advice;
    adviceContainer.style.display = 'block';
}

// 显示路线分析
function showRouteAnalysis(analysis) {
    const analysisContainer = document.getElementById('routeAnalysis');
    const analysisContent = analysisContainer.querySelector('.analysis-content');
    analysisContent.textContent = analysis;
    analysisContainer.style.display = 'block';
}

// 更新天气和交通信息显示
function updateWeatherTrafficInfo(weather, traffic) {
    const infoContainer = document.getElementById('weatherTrafficInfo');
    infoContainer.innerHTML = `
        <div class="info-card">
            <div class="weather-info">
                <h4>🌤️ 天气信息</h4>
                <p>温度: ${weather.temperature}℃</p>
                <p>天气: ${weather.description}</p>
            </div>
            <div class="traffic-info">
                <h4>🚗 交通状况</h4>
                <p>拥堵指数: ${traffic.congestion_index}</p>
                <p>平均车速: ${traffic.average_speed}km/h</p>
            </div>
        </div>
    `;
    infoContainer.style.display = 'block';
}

// 更新路线规划函数
async function planRoute() {
    const start = document.getElementById('startLocation').value;
    const end = document.getElementById('endLocation').value;
    
    if (!start || !end) {
        showNotification('请输入起点和终点位置');
        return;
    }

    showLoading(true);
    
    try {
        // 获取坐标
        const startResponse = await fetch(`/api/v1/route/geocode?address=${encodeURIComponent(start)}`);
        const endResponse = await fetch(`/api/v1/route/geocode?address=${encodeURIComponent(end)}`);
        
        if (!startResponse.ok || !endResponse.ok) {
            throw new Error('地址解析失败');
        }
        
        const startData = await startResponse.json();
        const endData = await endResponse.json();
        
        if (startData.status !== 'success' || endData.status !== 'success') {
            throw new Error('地址解析失败');
        }
        
        const startCoords = startData.location;
        const endCoords = endData.location;
        
        // 获取常规路线
        const routeResponse = await fetch('/api/v1/route/plan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                start: `${startCoords.lng},${startCoords.lat}`,
                end: `${endCoords.lng},${endCoords.lat}`
            })
        });

        if (!routeResponse.ok) {
            throw new Error('路线规划失败');
        }

        const routeData = await routeResponse.json();
        
        if (routeData.status !== 'success') {
            throw new Error(routeData.message || '路线规划失败');
        }

        // 清除旧路线
        clearMap();

        // 绘制新路线
        const path = routeData.path || routeData.polyline.map(point => {
            const [lng, lat] = point.split(',').map(Number);
            return [lng, lat];
        });
        drawRoute(path);

        // 添加起终点标记
        addMarker(startCoords.lat, startCoords.lng, start);
        addMarker(endCoords.lat, endCoords.lng, end);

        // 显示路线详情
        updateRouteDetails(routeData);

        // 获取智能建议
        const suggestionResponse = await fetch('/api/v1/route/smart-suggestion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                start: `${startCoords.lng},${startCoords.lat}`,
                end: `${endCoords.lng},${endCoords.lat}`
            })
        });

        if (!suggestionResponse.ok) {
            throw new Error('获取智能建议失败');
        }

        const suggestionData = await suggestionResponse.json();
        
        if (suggestionData.status === 'success') {
            showAIAdvice(suggestionData.suggestion);
            updateWeatherTrafficInfo(suggestionData.weather, suggestionData.traffic);
        }

        // 分析路线选项
        const analysisResponse = await fetch('/api/v1/route/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ routes: [routeData] })
        });

        if (!analysisResponse.ok) {
            throw new Error('路线分析失败');
        }

        const analysisData = await analysisResponse.json();
        
        if (analysisData.status === 'success') {
            showRouteAnalysis(analysisData.analysis);
        }

    } catch (error) {
        console.error('Error:', error);
        showNotification(`路线规划失败: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// 更新路线详情显示
function updateRouteDetails(data) {
    const routeDetails = document.querySelector('.route-details');
    const totalDistance = document.getElementById('totalDistance');
    const totalTime = document.getElementById('totalTime');
    const routeSegments = document.getElementById('routeSegments');

    if (data.distance && data.duration) {
        totalDistance.textContent = `${(data.distance / 1000).toFixed(1)}公里`;
        totalTime.textContent = `${Math.ceil(data.duration / 60)}分钟`;
        
        if (data.steps) {
            routeSegments.innerHTML = data.steps.map((step, index) => `
                <div class="route-segment">
                    <div class="segment-number">${index + 1}</div>
                    <div class="segment-instruction">${step.instruction}</div>
                    <div class="segment-distance">${(step.distance / 1000).toFixed(1)}km</div>
                </div>
            `).join('');
        }
        
        routeDetails.style.display = 'block';
    }
}

// 显示加载动画
function showLoading(show) {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

// 显示通知
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
} 