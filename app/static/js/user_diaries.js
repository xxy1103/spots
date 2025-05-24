// user_diaries.js - 用户日记页面专用JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 初始化页面
    initializePage();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 添加交互动画
    addInteractiveAnimations();
});

// 初始化页面
function initializePage() {
    // 检查用户会话
    checkUserSession();
    
    // 初始化统计数据动画
    animateStats();
    
    // 初始化图片懒加载
    initLazyLoading();
}

// 检查用户会话
function checkUserSession() {
    fetch('/api/check-session')
        .then(response => {
            if (!response.ok) {
                throw new Error('未登录');
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                // 如果会话无效，重定向到登录页
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('检查会话时出错:', error);
            // 可选择重定向到登录页
            // window.location.href = '/login';
        });
}

// 绑定事件监听器
function bindEventListeners() {
    // 搜索功能
    const searchButton = document.querySelector('.search-button');
    const searchInput = document.querySelector('.search-input input');
    const searchSelect = document.querySelector('.search-bar select');
    
    if (searchButton) {
        searchButton.addEventListener('click', handleSearch);
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // 登出按钮
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }
    
    // 日记项点击事件
    const diaryItems = document.querySelectorAll('.diary-item');
    diaryItems.forEach(item => {
        item.addEventListener('click', handleDiaryItemClick);
    });
    
    // 图片预览点击事件
    const previewImages = document.querySelectorAll('.preview-image img');
    previewImages.forEach(img => {
        img.addEventListener('click', handleImagePreview);
    });
    
    // 统计项点击事件
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('click', handleStatItemClick);
    });
}

// 处理搜索
function handleSearch() {
    const keyword = document.querySelector('.search-input input').value.trim();
    const searchType = document.querySelector('.search-bar select').value;
    
    if (!keyword) {
        showToast('请输入搜索关键词');
        return;
    }
    
    // 根据搜索类型跳转
    if (searchType === 'diary') {
        window.location.href = `/diary/search?keyword=${encodeURIComponent(keyword)}`;
    } else {
        window.location.href = `/spots/search?keyword=${encodeURIComponent(keyword)}`;
    }
}

// 处理登出
function handleLogout() {
    if (confirm('确定要登出吗？')) {
        fetch('/api/logout', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                showToast('登出成功');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1000);
            } else {
                throw new Error('登出失败');
            }
        })
        .catch(error => {
            console.error('登出时出错:', error);
            showToast('登出失败，请重试');
        });
    }
}

// 处理日记项点击
function handleDiaryItemClick(event) {
    // 如果点击的是链接，不要阻止默认行为
    if (event.target.tagName === 'A' || event.target.closest('a')) {
        return;
    }
    
    // 如果点击的是图片，不要跳转到日记详情
    if (event.target.tagName === 'IMG' || event.target.closest('.preview-image')) {
        return;
    }
    
    const diaryId = event.currentTarget.dataset.diaryId;
    if (diaryId) {
        window.location.href = `/diary/${diaryId}`;
    }
}

// 处理图片预览
function handleImagePreview(event) {
    event.stopPropagation(); // 阻止事件冒泡
    
    const imgSrc = event.target.src;
    if (imgSrc) {
        openImageModal(imgSrc);
    }
}

// 打开图片模态框
function openImageModal(imageSrc) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="image-modal-backdrop">
            <div class="image-modal-content">
                <button class="image-modal-close">&times;</button>
                <img src="${imageSrc}" alt="图片预览">
            </div>
        </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .image-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        }
        
        .image-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }
        
        .image-modal-content {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .image-modal-close {
            position: absolute;
            top: 10px;
            right: 15px;
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            font-size: 24px;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .image-modal img {
            max-width: 100%;
            max-height: 100%;
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // 绑定关闭事件
    const closeBtn = modal.querySelector('.image-modal-close');
    const backdrop = modal.querySelector('.image-modal-backdrop');
    
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
        document.head.removeChild(style);
    });
    
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
            document.body.removeChild(modal);
            document.head.removeChild(style);
        }
    });
    
    // ESC键关闭
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            document.body.removeChild(modal);
            document.head.removeChild(style);
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
}

// 处理统计项点击
function handleStatItemClick(event) {
    const statItem = event.currentTarget;
    const statLabel = statItem.querySelector('.stat-label').textContent;
    
    // 添加点击动画
    statItem.style.transform = 'scale(0.95)';
    setTimeout(() => {
        statItem.style.transform = '';
    }, 150);
    
    // 根据统计类型执行相应操作
    if (statLabel.includes('日记')) {
        // 滚动到日记列表
        const diariesSection = document.querySelector('.diaries-section');
        if (diariesSection) {
            diariesSection.scrollIntoView({ behavior: 'smooth' });
        }
    } else if (statLabel.includes('评价')) {
        // 可以跳转到用户评价页面（如果有的话）
        showToast('评价功能正在开发中...');
    }
}

// 添加交互动画
function addInteractiveAnimations() {
    // 为日记项添加序列动画
    const diaryItems = document.querySelectorAll('.diary-item');
    diaryItems.forEach((item, index) => {
        item.style.animationDelay = `${0.1 * index}s`;
        item.classList.add('diary-item-animate');
    });
    
    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        .diary-item-animate {
            opacity: 0;
            transform: translateX(-30px);
            animation: slideInRight 0.6s ease-out forwards;
        }
        
        @keyframes slideInRight {
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// 统计数据动画
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        if (isNaN(finalValue)) return;
        
        let currentValue = 0;
        const increment = Math.ceil(finalValue / 30); // 30帧动画
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            stat.textContent = currentValue;
        }, 50);
    });
}

// 初始化懒加载
function initLazyLoading() {
    const images = document.querySelectorAll('.preview-image img');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.style.transition = 'opacity 0.3s ease'; // Ensure transition is set

                    // Check if image is already loaded (e.g., from cache) and is a valid image
                    if (img.complete && typeof img.naturalWidth !== "undefined" && img.naturalWidth !== 0) {
                        img.style.opacity = '1'; // Show immediately
                    } else {
                        img.style.opacity = '0'; // Ensure it's hidden before loading
                        img.onload = () => {
                            img.style.opacity = '1'; // Fade in when loaded
                        };
                        img.onerror = () => {
                            // Handle image load errors, e.g., show a placeholder or log
                            // For now, let's try to make it visible to see if it's a broken image
                            img.style.opacity = '1'; 
                            console.error('Image failed to load:', img.src);
                        };
                    }
                    
                    observer.unobserve(img); // Unobserve after processing
                }
            });
        }, { threshold: 0.01 }); // Using a small threshold
        
        images.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver: just show all images
        images.forEach(img => {
            img.style.opacity = '1';
        });
    }
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // 样式
    const style = {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3',
        color: 'white',
        padding: '12px 24px',
        borderRadius: '25px',
        zIndex: '10000',
        fontSize: '14px',
        fontWeight: '500',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
        animation: 'slideUp 0.3s ease'
    };
    
    Object.assign(toast.style, style);
    
    // 添加动画样式
    if (!document.querySelector('#toast-styles')) {
        const toastStyle = document.createElement('style');
        toastStyle.id = 'toast-styles';
        toastStyle.textContent = `
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
            
            @keyframes slideDown {
                from {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(-50%) translateY(20px);
                }
            }
        `;
        document.head.appendChild(toastStyle);
    }
    
    document.body.appendChild(toast);
    
    // 3秒后消失
    setTimeout(() => {
        toast.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    // 清理定时器、事件监听器等
    const modals = document.querySelectorAll('.image-modal');
    modals.forEach(modal => {
        if (document.body.contains(modal)) {
            document.body.removeChild(modal);
        }
    });
});
