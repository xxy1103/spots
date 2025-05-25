document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    checkUserSession();
    
    // 设置搜索功能
    setupSearch();
    
    // 图片预览功能
    setupImagePreview();
    
    // 返回顶部按钮
    setupBackToTop();
    
    // 评分系统设置
    setupRatingSystem();
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

// 图片预览功能
function setupImagePreview() {
    const images = document.querySelectorAll('.image-gallery img');
    
    images.forEach(img => {
        img.addEventListener('click', function() {
            // 创建覆盖层
            const overlay = document.createElement('div');
            overlay.className = 'image-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';
            overlay.style.cursor = 'zoom-out';
            
            // 创建大图
            const fullImg = document.createElement('img');
            fullImg.src = this.src;
            fullImg.style.maxWidth = '90%';
            fullImg.style.maxHeight = '90%';
            fullImg.style.objectFit = 'contain';
            fullImg.style.boxShadow = '0 0 20px rgba(255, 255, 255, 0.1)';
            fullImg.style.transition = 'transform 0.3s ease';
            
            // 将图片添加到覆盖层
            overlay.appendChild(fullImg);
            
            // 添加关闭功能
            overlay.addEventListener('click', function() {
                document.body.removeChild(overlay);
            });
            
            // 添加到body
            document.body.appendChild(overlay);
        });
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
    
    // 更新星星显示的函数
    function updateStars(value) {
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
    }
    
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

// 删除确认
function confirmDelete() {
    const result = confirm("确定要删除这篇日记吗？此操作不可撤销。");
    if (result) {
        document.getElementById("delete-form").submit();
    }
}
