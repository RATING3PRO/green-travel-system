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

// 路线规划功能
async function planRoute() {
    const startLocation = document.getElementById('startLocation').value.trim();
    const endLocation = document.getElementById('endLocation').value.trim();
    
    if (!startLocation || !endLocation) {
        showNotification('请输入起点和终点位置');
        return;
    }
    
    try {
        // 清除现有路线
        map.eachLayer((layer) => {
            if (layer instanceof L.Polyline || layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
        
        // 模拟路线坐标（实际应用中应该从后端API获取）
        const route = [
            [39.9042, 116.4074], // 起点（北京市中心）
            [39.9100, 116.4100], // 途经点1
            [39.9150, 116.4150], // 途经点2
            [39.9200, 116.4200]  // 终点
        ];
        
        // 添加起点和终点标记
        addMarker(route[0][0], route[0][1], '起点: ' + startLocation);
        addMarker(route[route.length-1][0], route[route.length-1][1], '终点: ' + endLocation);
        
        // 绘制路线
        drawRoute(route);
        
        // 显示路线详情
        document.querySelector('.route-details').style.display = 'block';
        document.getElementById('totalDistance').textContent = '5.2 公里';
        document.getElementById('totalTime').textContent = '15 分钟';
        
        // 调整地图视图以显示整个路线
        map.fitBounds(route);
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('路线规划失败，请稍后重试');
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