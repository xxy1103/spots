// 图片导航功能
let currentImageIndex = 0;
let imageElements = [];

// 全局定义 openImageModal 和 closeImageModal 函数，以便 HTML 中的 onclick 能够访问
window.openImageModal = function(imgElement, event) {
    console.log('openImageModal called with:', imgElement, event); // 调试日志
    
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    
    console.log('Modal elements found:', modal, modalImg); // 调试日志
    
    if (modal && modalImg) {
        // 获取所有图片元素
        imageElements = Array.from(document.querySelectorAll('.gallery-image'));
        currentImageIndex = imageElements.indexOf(imgElement);
        
        console.log('Image elements:', imageElements.length, 'Current index:', currentImageIndex); // 调试日志
        
        // 设置模态框中的图片源
        modalImg.src = imgElement.src;
        modalImg.dataset.imagePath = imgElement.src; // 保存图片路径用于AIGC
        
        // 显示模态框并添加淡入动画
        modal.style.display = 'block';
        
        // 阻止事件冒泡
        if (event) {
            event.stopPropagation();
        }
        
        // 禁止背景滚动
        document.body.style.overflow = 'hidden';
        
        // 更新导航按钮状态
        updateNavigationButtons();    } else {
        console.error('Modal or modal image not found!'); // 错误日志
    }
};

window.closeImageModal = function() {
    const modal = document.getElementById('imageModal');
    
    if (modal) {
        // 淡出并关闭模态框
        modal.style.display = 'none';
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        // 隐藏加载动画
        hideLoadingSpinner();
    }
};

// 图片导航功能
window.navigateImage = function(direction) {
    if (imageElements.length === 0) return;
    
    const modalImg = document.getElementById('modalImage');
    const prevIndex = currentImageIndex;
    
    currentImageIndex += direction;
    
    // 循环导航
    if (currentImageIndex >= imageElements.length) {
        currentImageIndex = 0;
    } else if (currentImageIndex < 0) {
        currentImageIndex = imageElements.length - 1;
    }
    
    // 添加切换动画
    const animationClass = direction > 0 ? 'slide-right' : 'slide-left';
    modalImg.classList.remove('slide-right', 'slide-left');
    
    // 更新图片
    modalImg.src = imageElements[currentImageIndex].src;
    modalImg.dataset.imagePath = imageElements[currentImageIndex].src;
    modalImg.classList.add(animationClass);
    
    // 移除动画类
    setTimeout(() => {
        modalImg.classList.remove(animationClass);
    }, 300);
    
    // 更新导航按钮状态
    updateNavigationButtons();
};

// 更新导航按钮状态
function updateNavigationButtons() {
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');
    
    if (imageElements.length <= 1) {
        if (prevButton) prevButton.style.display = 'none';
        if (nextButton) nextButton.style.display = 'none';
    } else {
        if (prevButton) prevButton.style.display = 'flex';
        if (nextButton) nextButton.style.display = 'flex';
    }
}

// AIGC 视频生成功能
window.generateVideo = function() {
    const modalImg = document.getElementById('modalImage');
    const imagePath = modalImg.dataset.imagePath;
    
    if (!imagePath) {
        showToast('未能获取图片路径', 'error');
        return;
    }
    
    if (!window.DIARY_ID) {
        showToast('未能获取日记ID', 'error');
        return;
    }
    
    // 显示加载动画
    showLoadingSpinner();
    
    // 禁用按钮
    const aigcButton = document.getElementById('aigcButton');
    if (aigcButton) {
        aigcButton.disabled = true;
    }
    
    // 发送请求到后端
    fetch(`/diary/AIGC/${window.DIARY_ID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_path: imagePath
        })
    })
    .then(response => {
        if (response.redirected) {
            // 如果后端返回重定向，直接跳转
            window.location.href = response.url;
            return;
        }
        return response.json();
    })
    .then(data => {
        hideLoadingSpinner();
        
        if (data && data.success === false) {
            showToast(data.message || 'AI视频生成失败', 'error');
        } else {
            showToast('AI视频生成成功！页面即将刷新...', 'success');
            // 延迟刷新页面以显示成功消息
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        console.error('AI视频生成错误:', error);
        hideLoadingSpinner();
        showToast('AI视频生成过程中出现错误', 'error');
    })
    .finally(() => {
        // 重新启用按钮
        if (aigcButton) {
            aigcButton.disabled = false;
        }
    });
};

// 显示加载动画
function showLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const button = document.getElementById('aigcButton');
    
    if (spinner && button) {
        button.style.display = 'none';
        spinner.style.display = 'flex';
    }
}

// 隐藏加载动画
function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const button = document.getElementById('aigcButton');
    
    if (spinner && button) {
        spinner.style.display = 'none';
        button.style.display = 'flex';
    }
}

// 显示提示消息
function showToast(message, type = 'success') {
    // 移除现有的提示
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 创建新的提示
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // 显示提示
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// 键盘事件支持
document.addEventListener('keydown', function(event) {
    const modal = document.getElementById('imageModal');
    if (modal && modal.style.display === 'block') {
        switch(event.key) {
            case 'Escape':
                closeImageModal();
                break;
            case 'ArrowLeft':
                navigateImage(-1);
                break;
            case 'ArrowRight':
                navigateImage(1);                break;
        }    }
});

document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    checkUserSession();
    
    // 设置搜索功能
    setupSearch();
    
    // 返回顶部按钮
    setupBackToTop();
    
    // 评分系统设置
    setupRatingSystem();
    
    // 加载用户之前的评分
    loadUserRating();
    
    // 为模态框添加键盘事件监听器
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeImageModal();
        }
    });
});

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
    
    function handleSearch() {
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
        
        const searchType = searchTypeSelect.value;
        
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
    
    searchButton.addEventListener('click', handleSearch);
    
    // 回车键也可以搜索
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
}

// 返回顶部按钮
function setupBackToTop() {
    // 创建返回顶部按钮
    const backToTopButton = document.createElement('div');
    backToTopButton.className = 'back-to-top';
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTopButton);
    
    // 监听滚动事件
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });
    
    // 点击返回顶部
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 评分系统
function setupRatingSystem() {
    const ratingForm = document.querySelector('.rating-form');
    
    if (!ratingForm) return;
    
    // 创建星星评分系统
    const scoreInput = document.getElementById('score');
    const ratingContainer = document.createElement('div');
    ratingContainer.className = 'star-rating';
    
    // 在评分输入框前插入星星评分系统
    const formGroup = scoreInput.parentElement.parentElement;
    formGroup.insertBefore(ratingContainer, formGroup.firstChild);
    
    // 创建5颗星星
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('span');
        star.className = 'star empty';
        star.innerHTML = '★';
        star.setAttribute('data-value', i);
        
        star.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            scoreInput.value = value;
            
            // 更新星星显示
            updateStars(value);
        });
        
        star.addEventListener('mouseover', function() {
            const value = this.getAttribute('data-value');
            
            // 临时更新星星显示
            document.querySelectorAll('.star').forEach(s => {
                const starValue = s.getAttribute('data-value');
                if (starValue <= value) {
                    s.classList.add('filled');
                    s.classList.remove('empty');
                } else {
                    s.classList.add('empty');
                    s.classList.remove('filled');
                }
            });
        });
        
        ratingContainer.appendChild(star);
    }
    
    // 鼠标移出星星区域时恢复
    ratingContainer.addEventListener('mouseout', function() {
        updateStars(scoreInput.value);
    });
    
    // 使用全局 updateStars 函数，之前已在全局范围定义

    // 添加数字输入框变化监听，同步更新星星
    scoreInput.addEventListener('input', function() {
        updateStars(this.value);
    });
    
    // 表单提交前验证
    ratingForm.addEventListener('submit', function(e) {
        const score = parseFloat(scoreInput.value);
        
        if (isNaN(score) || score < 0 || score > 5) {
            e.preventDefault();
            alert('请输入0-5之间的评分');
            return false;
        }
    });
}

// 加载用户之前对日记的评分
function loadUserRating() {
    // 检查是否有评分表单（如果是作者自己的日记则没有评分表单）
    const ratingForm = document.querySelector('.rating-form');
    if (!ratingForm) return;
    
    // 从URL中获取日记ID
    const pathParts = window.location.pathname.split('/');
    const diaryId = pathParts[pathParts.length - 1];
    
    // 发起请求获取用户之前的评分
    fetch(`/diary/${diaryId}/user_marking`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 更新评分输入框
            const scoreInput = document.getElementById('score');
            if (scoreInput) {
                // 即使评分为 0 也要显示
                scoreInput.value = data.score !== undefined ? data.score : 0;
                
                // 更新星级显示
                updateStars(scoreInput.value);
            }
        })
        .catch(error => {
            console.error('获取用户评分时出错:', error);
        });
}

// 全局函数：更新星星显示
function updateStars(value) {
    const stars = document.querySelectorAll('.star-rating .star');
    stars.forEach(star => {
        const starValue = star.getAttribute('data-value');
        if (starValue <= value) {
            star.classList.add('filled');
            star.classList.remove('empty');
        } else {
            star.classList.add('empty');
            star.classList.remove('filled');
        }
    });
}

// 删除确认
function confirmDelete() {
    const result = confirm("确定要删除这篇日记吗？此操作不可撤销。");
    if (result) {
        document.getElementById("delete-form").submit();
    }
}
