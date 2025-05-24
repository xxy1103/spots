document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    checkUserSession();
    
    // 设置搜索功能
    setupSearch();
    
    // 错误页面特效
    setupErrorEffects();
    
    // 自动跳转功能（可选）
    setupAutoRedirect();
    
    // 错误报告功能
    setupErrorReporting();
});

// 检查用户会话
function checkUserSession() {
    const usernameSpan = document.getElementById('username');
    fetch('/api/check-session')
        .then(response => {
            if (!response.ok) {
                // 如果未授权 (401) 或其他错误，重定向到登录页
                if (response.status === 401) {
                    window.location.href = '/login'; // 跳转到登录页面的路由
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return null; // 防止进一步处理
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                if (usernameSpan) {
                    usernameSpan.textContent = data.user.username || '用户';
                    // 设置用户名链接到用户的日记页面
                    if (data.user.user_id) {
                        usernameSpan.href = `/diary/user/${data.user.user_id}`;
                    }
                }
                // 用户信息获取成功后，获取推荐景点
                if (typeof loadTabContent === 'function') {
                    loadTabContent('recommended');
                }
            } else if (data) {
                // 即使成功响应，也可能业务逻辑失败
                console.error('会话检查失败:', data.message);
                window.location.href = '/login';
            }
            // 如果 response.ok 为 false 且非 401，则不会执行到这里
        })
        .catch(error => {
            console.error('检查会话时出错:', error);
            if (usernameSpan) usernameSpan.textContent = '错误';
            // 可选：也在此处重定向到登录页
            window.location.href = '/login';
        });
}

// 设置搜索功能
function setupSearch() {
    const searchForm = document.querySelector('.search-bar');
    const searchInput = document.querySelector('.search-input input');
    const searchTypeSelect = document.querySelector('.search-bar select');
    const searchButton = document.querySelector('.search-button');
    
    if (!searchButton) return;
    
    searchButton.addEventListener('click', function() {
        const searchType = searchTypeSelect.value;
        const searchQuery = searchInput.value.trim();
        
        if (searchQuery) {
            if (searchType === 'spot') {
                window.location.href = `/spots/search?keyword=${encodeURIComponent(searchQuery)}`;
            } else if (searchType === 'diary') {
                window.location.href = `/diary/search?keyword=${encodeURIComponent(searchQuery)}`;
            }
        }
    });
    
    // 回车键也可以搜索
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
}

// 错误页面特效
function setupErrorEffects() {
    // 添加错误类型特定的类名
    const errorContainer = document.querySelector('.error-container');
    const errorMessage = document.querySelector('.error-message').textContent;
    
    if (errorMessage.includes('404') || errorMessage.includes('找不到')) {
        errorContainer.classList.add('error-404');
    } else if (errorMessage.includes('500') || errorMessage.includes('服务器')) {
        errorContainer.classList.add('error-500');
    } else if (errorMessage.includes('403') || errorMessage.includes('权限')) {
        errorContainer.classList.add('error-403');
    }
    
    // 添加随机浮动效果
    createFloatingElements();
    
    // 添加鼠标跟踪效果
    setupMouseTracker();
}

// 创建浮动元素
function createFloatingElements() {
    const container = document.querySelector('.main-content');
    
    for (let i = 0; i < 5; i++) {
        const element = document.createElement('div');
        element.className = 'floating-element';
        element.style.position = 'absolute';
        element.style.width = Math.random() * 20 + 10 + 'px';
        element.style.height = element.style.width;
        element.style.borderRadius = '50%';
        element.style.background = `rgba(0, 82, 217, ${Math.random() * 0.1 + 0.05})`;
        element.style.left = Math.random() * 100 + '%';
        element.style.top = Math.random() * 100 + '%';
        element.style.animation = `float ${Math.random() * 0.75 + 0.75}s ease-in-out infinite`;
        element.style.animationDelay = Math.random() * 0.5 + 's';
        element.style.zIndex = '-1';
        
        container.appendChild(element);
    }
}

// 鼠标跟踪效果
function setupMouseTracker() {
    const errorIcon = document.querySelector('.error-icon');
    
    if (!errorIcon) return;
    
    document.addEventListener('mousemove', function(e) {
        const rect = errorIcon.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const deltaX = (e.clientX - centerX) / 50;
        const deltaY = (e.clientY - centerY) / 50;
        
        errorIcon.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
    });
}

// 自动跳转功能
function setupAutoRedirect() {
    // 检查是否需要自动跳转（例如404页面10秒后跳转到首页）
    const errorMessage = document.querySelector('.error-message').textContent;
    
    if (errorMessage.includes('404') || errorMessage.includes('找不到')) {
        let countdown = 10;
        const countdownElement = document.createElement('div');
        countdownElement.className = 'auto-redirect';
        countdownElement.style.marginTop = '1rem';
        countdownElement.style.fontSize = '0.9rem';
        countdownElement.style.color = '#888';
        
        const updateCountdown = () => {
            countdownElement.innerHTML = `<i class="fas fa-clock"></i> ${countdown} 秒后自动返回首页 <a href="#" onclick="cancelAutoRedirect()" style="color: #0052d9;">取消</a>`;
            countdown--;
            
            if (countdown < 0) {
                window.location.href = '/spots';
            }
        };
        
        document.querySelector('.error-container').appendChild(countdownElement);
        
        const redirectInterval = setInterval(updateCountdown, 1000);
        updateCountdown();
        
        // 将取消函数添加到全局作用域
        window.cancelAutoRedirect = function() {
            clearInterval(redirectInterval);
            countdownElement.remove();
        };
    }
}

// 错误报告功能
function setupErrorReporting() {
    // 创建错误报告按钮
    const reportButton = document.createElement('button');
    reportButton.className = 'btn-secondary';
    reportButton.innerHTML = '<i class="fas fa-bug"></i> 报告问题';
    reportButton.style.marginTop = '1rem';
    
    reportButton.addEventListener('click', function() {
        const errorDetails = {
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            message: document.querySelector('.error-message').textContent
        };
        
        // 显示报告对话框
        showReportDialog(errorDetails);
    });
    
    // 将报告按钮添加到操作区域
    const actionsContainer = document.querySelector('.error-actions');
    if (actionsContainer) {
        actionsContainer.appendChild(reportButton);
    }
}

// 显示错误报告对话框
function showReportDialog(errorDetails) {
    // 创建模态对话框
    const modal = document.createElement('div');
    modal.className = 'error-report-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '2000';
    
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '2rem';
    modalContent.style.borderRadius = '12px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '90%';
    modalContent.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
    
    modalContent.innerHTML = `
        <h3 style="margin-bottom: 1rem; color: #0052d9;">报告问题</h3>
        <p style="margin-bottom: 1rem; color: #666;">请描述您遇到的问题，我们会尽快处理。</p>
        <textarea id="report-description" placeholder="请描述问题详情..." style="width: 100%; height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem; resize: vertical;"></textarea>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
            <button onclick="closeReportDialog()" style="padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer;">取消</button>
            <button onclick="submitReport()" style="padding: 8px 16px; background: #0052d9; color: white; border: none; border-radius: 4px; cursor: pointer;">提交</button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeReportDialog();
        }
    });
    
    // 存储错误详情供提交使用
    window.currentErrorDetails = errorDetails;
    
    // 聚焦到文本框
    setTimeout(() => {
        document.getElementById('report-description').focus();
    }, 100);
}

// 关闭报告对话框
window.closeReportDialog = function() {
    const modal = document.querySelector('.error-report-modal');
    if (modal) {
        modal.remove();
    }
};

// 提交错误报告
window.submitReport = function() {
    const description = document.getElementById('report-description').value.trim();
    
    if (!description) {
        alert('请填写问题描述');
        return;
    }
    
    const reportData = {
        ...window.currentErrorDetails,
        description: description
    };
    
    // 这里可以发送到后端API
    console.log('Error report:', reportData);
    
    // 模拟提交
    alert('感谢您的反馈！我们已收到您的问题报告。');
    closeReportDialog();
};

// 页面卸载前清理
window.addEventListener('beforeunload', function() {
    // 清理定时器
    if (window.redirectInterval) {
        clearInterval(window.redirectInterval);
    }
});

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // ESC键关闭模态框
    if (e.key === 'Escape') {
        closeReportDialog();
    }
    
    // Alt + H 返回首页
    if (e.altKey && e.key === 'h') {
        e.preventDefault();
        window.location.href = '/spots';
    }
    
    // Alt + B 返回上一页
    if (e.altKey && e.key === 'b') {
        e.preventDefault();
        window.history.back();
    }
});
