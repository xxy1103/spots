// diary_add.js - 日记添加页面专用JavaScript

// 全局变量：跟踪表单提交状态
let isFormSubmitting = false;

document.addEventListener('DOMContentLoaded', () => {
    // 初始化页面
    initializePage();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 添加表单验证
    setupFormValidation();
    
    // 初始化评分系统
    initializeRating();
});

// 初始化页面
function initializePage() {
    // 检查用户会话，确保用户已登录
    checkUserSession();
    
    // 初始化拖放功能
    initializeDragAndDrop();
}

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

// 绑定事件监听器
function bindEventListeners() {
    // 搜索功能
    const searchButton = document.querySelector('.search-button');
    const searchInput = document.querySelector('.search-input input');
    const searchSelect = document.querySelector('.search-bar select');
    
    if (searchButton && searchInput && searchSelect) {
        searchButton.addEventListener('click', handleSearch);
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
    
    // 文件上传按钮点击
    const imageUploadButton = document.getElementById('imageUploadButton');
    const videoUploadButton = document.getElementById('videoUploadButton');
    const imagesInput = document.getElementById('images');
    const videosInput = document.getElementById('videos');
    
    if (imageUploadButton && imagesInput) {
        imageUploadButton.addEventListener('click', () => imagesInput.click());
    }
    
    if (videoUploadButton && videosInput) {
        videoUploadButton.addEventListener('click', () => videosInput.click());
    }
    
    // 监听文件选择变化
    if (imagesInput) {
        imagesInput.addEventListener('change', function(event) {
            previewImages(event);
        });
    }
    
    if (videosInput) {
        videosInput.addEventListener('change', function(event) {
            previewVideos(event);
        });
    }
    
    // 表单取消按钮
    const cancelButton = document.querySelector('.cancel-button');
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            if (confirm('确定要放弃编写日记吗？已编写的内容将不会保存。')) {
                window.history.back();
            }
        });
    }
}

// 处理搜索
function handleSearch() {
    const searchInput = document.querySelector('.search-input input');
    const searchSelect = document.querySelector('.search-bar select');
    
    if (!searchInput || !searchSelect) return;
    
    const keyword = searchInput.value.trim();
    if (!keyword) {
        // 空关键词提示
        searchInput.style.borderColor = 'red';
        searchInput.style.animation = 'shake 0.5s';
        setTimeout(() => {
            searchInput.style.borderColor = '#CCCCCC';
            searchInput.style.animation = '';
        }, 500);
        return;
    }
    
    const searchType = searchSelect.value;
    
    // 如果搜索类型是日记，直接跳转到日记搜索页面
    if (searchType === 'diary') {
        window.location.href = `/diary/search?keyword=${encodeURIComponent(keyword)}`;
        return;
    }
    
    // 其他搜索类型使用景点搜索API
    const apiUrl = new URL('/api/search-spots', window.location.origin);
    apiUrl.searchParams.append('keyword', keyword);
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && Array.isArray(data.spots)) {
                window.location.href = `/spots/search?keyword=${encodeURIComponent(keyword)}`;
            } else {
                showToast('搜索服务暂不可用，请稍后重试');
            }
        })
        .catch(error => {
            console.error('搜索时出错:', error);
            showToast('搜索服务暂不可用，请稍后重试');
        });
}

// 处理登出
function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        fetch('/api/logout', { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    showToast('已成功退出登录', 'success');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1000);
                } else {
                    throw new Error('退出失败');
                }
            })
            .catch(error => {
                console.error('登出时出错:', error);
                showToast('退出失败，请重试', 'error');
            });
    }
}

// 表单验证
function setupFormValidation() {
    const form = document.querySelector('.diary-add-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 移除所有错误提示
        const errorMessages = form.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());
        
        const formGroups = form.querySelectorAll('.form-group');
        formGroups.forEach(group => group.classList.remove('error'));
        
        // 验证景点选择
        const spotId = document.getElementById('spot_id').value;
        if (!spotId) {
            showFieldError('spot_id', '请选择一个景点');
            return;
        }
        
        // 验证标题
        const title = document.getElementById('title').value.trim();
        if (!title) {
            showFieldError('title', '请输入日记标题');
            return;
        }
        
        // 验证内容
        const content = document.getElementById('content').value.trim();
        if (!content) {
            showFieldError('content', '请输入日记内容');
            return;
        } else if (content.length < 50) {
            showFieldError('content', '日记内容至少需要50个字符');
            return;
        }
        
        // 验证评分
        const spotMarking = parseFloat(document.getElementById('spot_marking').value);
        if (isNaN(spotMarking) || spotMarking <= 0) {
            // 如果没有评分，设置为默认值
            document.getElementById('spot_marking').value = 3;
            const ratingValue = document.querySelector('.rating-value');
            if (ratingValue) {
                ratingValue.textContent = '3分';
            }
            highlightStars(3);
        }
          // 验证通过，提交表单
        isFormSubmitting = true; // 设置提交标志
        showToast('提交中...', 'info');
        form.submit();
    });
    
    // 显示字段错误
    function showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            formGroup.classList.add('error');
            
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.textContent = message;
            
            formGroup.appendChild(errorMessage);
            
            // 滚动到错误字段
            field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        showToast(message, 'error');
    }
}

// 初始化评分系统
function initializeRating() {
    const stars = document.querySelectorAll('.stars-container i');
    const ratingInput = document.getElementById('spot_marking');
    const ratingValue = document.querySelector('.rating-value');
    
    if (!stars.length || !ratingInput || !ratingValue) return;
    
    // 设置默认值为0
    ratingInput.value = 0;
    
    stars.forEach(star => {
        // 鼠标悬停效果
        star.addEventListener('mouseover', function() {
            const rating = this.getAttribute('data-rating');
            highlightStars(rating);
        });
        
        // 鼠标离开效果
        star.addEventListener('mouseout', function() {
            const currentRating = ratingInput.value;
            highlightStars(currentRating);
        });
        
        // 点击选择评分
        star.addEventListener('click', function() {
            const rating = this.getAttribute('data-rating');
            ratingInput.value = rating;
            ratingValue.textContent = rating + '分';
            highlightStars(rating);
              // 添加点击动画效果
            this.style.transform = 'scale(1.3)';
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        });
    });
}

// 高亮星星函数
function highlightStars(rating) {
    const stars = document.querySelectorAll('.stars-container i');
    
    stars.forEach(star => {
        const starRating = star.getAttribute('data-rating');
        if (starRating <= rating) {
            star.className = 'fas fa-star'; // 实心星星
        } else {
            star.className = 'far fa-star'; // 空心星星
        }
    });
}

// 初始化拖放功能
function initializeDragAndDrop() {
    const imagePreviewArea = document.getElementById('imagePreview');
    const videoPreviewArea = document.getElementById('videoPreview');
    
    if (!imagePreviewArea || !videoPreviewArea) return;
    
    // 为图片区域添加拖放事件
    setupDropZone(imagePreviewArea, 'images', previewImageFile);
    
    // 为视频区域添加拖放事件
    setupDropZone(videoPreviewArea, 'videos', previewVideoFile);
    
    function setupDropZone(dropZone, fileType, previewFunction) {
        // 防止浏览器默认拖放行为
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // 高亮拖放区域
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('highlight-drop');
            }, false);
        });
        
        // 取消高亮
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('highlight-drop');
            }, false);
        });
        
        // 处理拖放文件
        dropZone.addEventListener('drop', event => {
            const dt = event.dataTransfer;
            const files = dt.files;
            
            // 筛选文件类型
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (fileType === 'images' && file.type.startsWith('image/')) {
                    previewFunction(file, dropZone);
                } else if (fileType === 'videos' && file.type.startsWith('video/')) {
                    previewFunction(file, dropZone);
                }
            }
        }, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }
}

// 预览选择的图片
function previewImages(event) {
    const imagePreview = document.getElementById('imagePreview');
    if (!imagePreview) return;
    
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) continue;
        
        previewImageFile(file, imagePreview);
    }
}

// 预览单张图片
function previewImageFile(file, container) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item';
        
        const img = document.createElement('img');
        img.src = e.target.result;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'remove-preview';
        removeButton.innerHTML = '×';
        removeButton.onclick = function(e) {
            e.stopPropagation();  // 防止冒泡
            container.removeChild(previewItem);
        };
          previewItem.appendChild(img);
        previewItem.appendChild(removeButton);
        container.appendChild(previewItem);
        
        // 添加动画效果
        previewItem.style.opacity = '0';
        previewItem.style.transform = 'scale(0.8)';
        setTimeout(() => {
            previewItem.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            previewItem.style.opacity = '1';
            previewItem.style.transform = 'scale(1)';
        }, 10);
    };
    reader.readAsDataURL(file);
}

// 预览选择的视频
function previewVideos(event) {
    const videoPreview = document.getElementById('videoPreview');
    if (!videoPreview) return;
    
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file || !file.type.startsWith('video/')) continue;
        
        previewVideoFile(file, videoPreview);
    }
}

// 预览单个视频
function previewVideoFile(file, container) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item video-preview';
        
        const video = document.createElement('video');
        video.src = e.target.result;
        video.controls = true;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'remove-preview';
        removeButton.innerHTML = '×';
        removeButton.onclick = function(e) {
            e.stopPropagation();  // 防止冒泡
            container.removeChild(previewItem);
        };
        
        previewItem.appendChild(video);
        previewItem.appendChild(removeButton);
        container.appendChild(previewItem);
          // 添加动画效果
        previewItem.style.opacity = '0';
        previewItem.style.transform = 'scale(0.8)';
        setTimeout(() => {
            previewItem.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            previewItem.style.opacity = '1';
            previewItem.style.transform = 'scale(1)';
        }, 10);
    };
    reader.readAsDataURL(file);
}

// 显示提示消息
function showToast(message, type = 'info') {
    // 移除已有的toast
    const existingToasts = document.querySelectorAll('.toast-message');
    existingToasts.forEach(toast => {
        if (document.body.contains(toast)) {
            document.body.removeChild(toast);
        }
    });
    
    const toast = document.createElement('div');
    toast.className = `toast-message toast-${type}`;
    
    // 根据类型设置图标
    let icon = '';
    switch(type) {
        case 'success': icon = '✅'; break;
        case 'error': icon = '❌'; break;
        case 'warning': icon = '⚠️'; break;
        case 'info': 
        default: icon = 'ℹ️'; break;
    }
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-text">${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // 样式
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: 
            type === 'success' ? '#4caf50' : 
            type === 'error' ? '#f44336' : 
            type === 'warning' ? '#ff9800' : 
            '#2196f3',
        color: 'white',
        padding: '12px 24px',
        borderRadius: '30px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: '10000',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        opacity: '0',
        transition: 'opacity 0.3s, transform 0.3s'
    });
    
    // 动画
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 10);
      // 1.5秒后消失
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translate(-50%, 20px)';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 150);
    }, 1500);
}

// 页面卸载时确认
window.addEventListener('beforeunload', function(e) {
    // 如果正在提交表单，不显示警告
    if (isFormSubmitting) {
        return;
    }
    
    const title = document.getElementById('title');
    const content = document.getElementById('content');
    
    // 只有当用户已经输入内容时才提示确认
    if ((title && title.value.trim()) || (content && content.value.trim())) {
        const message = '您的日记未保存，确定要离开此页面吗？';
        e.returnValue = message;
        return message;
    }
});
