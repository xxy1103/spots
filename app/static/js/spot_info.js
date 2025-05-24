document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    checkUserSession();
    
    // 设置搜索功能
    setupSearch();
    
    // 设置图片懒加载
    setupLazyLoading();
    
    // 返回顶部按钮
    setupBackToTop();
    
    // 相关景点推荐
    loadRelatedSpots();
    
    // 地图功能
    setupMapFeatures();
    
    // 图片预览功能
    setupImagePreview();
    
    // 设置登出功能
    setupLogout();
    
    // 浮动动画效果
    createFloatingElements();
    
    // 加载用户评价
    loadUserReviews();
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

// 图片懒加载
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.classList.remove('loading');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            img.classList.remove('loading');
        });
    }
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

// 加载相关景点推荐
function loadRelatedSpots() {
    const relatedContainer = document.querySelector('.related-grid');
    if (!relatedContainer) return;
    
    // 获取当前景点ID
    const spotId = getSpotIdFromUrl();
    if (!spotId) return;
    
    // 显示加载状态
    showLoadingPlaceholders(relatedContainer, 3);
    
    fetch(`/api/spots/related/${spotId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.spots) {
                renderRelatedSpots(data.spots, relatedContainer);
            } else {
                showEmptyMessage(relatedContainer, '暂无相关推荐');
            }
        })
        .catch(error => {
            console.error('Error loading related spots:', error);
            showEmptyMessage(relatedContainer, '加载失败');
        });
}

// 渲染相关景点
function renderRelatedSpots(spots, container) {
    container.innerHTML = '';
    
    spots.forEach((spot, index) => {
        const spotElement = document.createElement('a');
        spotElement.className = 'related-item';
        spotElement.href = `/spots/spot_info/${spot.id}`;
        spotElement.style.animationDelay = `${index * 0.1}s`;
        
        spotElement.innerHTML = `
            <img src="${spot.img || '/static/placeholder-image.jpg'}" 
                 alt="${spot.name}" 
                 class="related-image"
                 onerror="this.src='/static/placeholder-image.jpg'">
            <div class="related-info">
                <div class="related-name">${spot.name}</div>
                <div class="related-type">${spot.type} • ⭐ ${spot.score}</div>
            </div>
        `;
        
        container.appendChild(spotElement);
    });
}

// 显示加载占位符
function showLoadingPlaceholders(container, count) {
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const placeholder = document.createElement('div');
        placeholder.className = 'loading-placeholder-card';
        placeholder.innerHTML = `
            <div class="loading-placeholder image"></div>
            <div class="loading-placeholder text"></div>
            <div class="loading-placeholder text" style="width: 60%;"></div>
        `;
        container.appendChild(placeholder);
    }
}

// 显示空消息
function showEmptyMessage(container, message) {
    container.innerHTML = `<div class="empty-message">${message}</div>`;
}

// 从URL获取景点ID
function getSpotIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    return pathParts[pathParts.length - 1];
}

// 地图功能设置
function setupMapFeatures() {
    // 这里可以添加地图相关的功能
    console.log('Map features setup complete');
}

// 打开地图模态框
function openMapModal(spotId) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'map-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '2000';
    
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '2rem';
    modalContent.style.borderRadius = '12px';
    modalContent.style.maxWidth = '90%';
    modalContent.style.maxHeight = '90%';
    modalContent.style.width = '800px';
    modalContent.style.height = '600px';
    modalContent.style.position = 'relative';
    
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #0052d9;">景点位置</h3>
            <button onclick="closeMapModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
        </div>
        <iframe src="/map/${spotId}" 
                style="width: 100%; height: calc(100% - 60px); border: none; border-radius: 8px;">
        </iframe>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeMapModal();
        }
    });
    
    // 存储模态框引用
    window.currentMapModal = modal;
}

// 关闭地图模态框
window.closeMapModal = function() {
    if (window.currentMapModal) {
        document.body.removeChild(window.currentMapModal);
        window.currentMapModal = null;
    }
};

// 设置图片预览功能
function setupImagePreview() {
    const mainImage = document.querySelector('.main-image');
    const viewFullBtn = document.querySelector('.view-full-btn');
    const modal = document.getElementById('imageModal');
    const modalImage = modal?.querySelector('.modal-image');
    const closeModal = modal?.querySelector('.close-modal');
    
    if (viewFullBtn && modal && modalImage && mainImage) {
        viewFullBtn.addEventListener('click', function() {
            modalImage.src = mainImage.src;
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
        
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
}

// 加载用户评价数据 (初始加载)
function loadUserReviews() {
    const spotId = getSpotIdFromUrl();
    if (!spotId) {
        showEmptyMessage('reviewsList', '无法获取景点ID');
        return;
    }

    const reviewsList = document.getElementById('reviewsList');
    if (!reviewsList) return;
    
    // 显示加载占位符
    reviewsList.innerHTML = '<div class="loading-reviews">正在加载评价...</div>';
    
    // 从API获取日记/评价数据
    fetch(`/diary/spot/${spotId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data) && data.length > 0) {
                // 限制首页显示的评价数量
                const previewReviews = data.slice(0, 3);
                renderReviews(previewReviews, reviewsList);
                
                // 如果有更多评价可加载，确保"加载更多"按钮可用
                const loadMoreBtn = document.querySelector('.view-all-reviews-btn');
                if (loadMoreBtn) {
                    if (data.length > 3) {
                        loadMoreBtn.disabled = false;
                        loadMoreBtn.textContent = '加载更多评价';
                    } else {
                        loadMoreBtn.disabled = true;
                        loadMoreBtn.textContent = '没有更多评价了';
                    }
                }
            } else {
                showEmptyMessage('reviewsList', '暂无评价');
                
                // 禁用"加载更多"按钮
                const loadMoreBtn = document.querySelector('.view-all-reviews-btn');
                if (loadMoreBtn) {
                    loadMoreBtn.disabled = true;
                    loadMoreBtn.textContent = '没有评价';
                }
            }
        })
        .catch(error => {
            console.error('获取评价数据出错:', error);
            showEmptyMessage('reviewsList', '加载评价失败，请稍后再试');
            
            // 禁用"加载更多"按钮
            const loadMoreBtn = document.querySelector('.view-all-reviews-btn');
            if (loadMoreBtn) {
                loadMoreBtn.disabled = true;
                loadMoreBtn.textContent = '加载失败';
            }
        });
}

// 渲染评价列表
function renderReviews(reviews, container) {
    if (!container) return;
    
    // 清空容器
    container.innerHTML = '';
    
    if (!reviews || reviews.length === 0) {
        showEmptyMessage(container.id, '暂无评价');
        return;
    }
    
    // 创建评价项元素
    reviews.forEach(review => {
        const reviewElement = createReviewElement(review);
        container.appendChild(reviewElement);
    });
}

// 创建单个评价元素
function createReviewElement(review) {
    const reviewItem = document.createElement('div');
    reviewItem.className = 'review-item';
    
    // 计算星级评分(假设评分范围是1-5)
    let score = review.scoreToSpot || 5.0; // 默认5分
    if (typeof score !== 'number') {
        score = parseFloat(score) || 5.0;
    }
    score = Math.min(5, Math.max(1, score)); // 范围限制在1-5之间
    
    // 创建星级HTML
    const starsHTML = createStarsHTML(score);
    
    // 格式化日期
    const formattedDate = formatDate(review.create_time);
    
    // 截取内容预览(如果内容太长)
    let content = review.content || '';
    const isLongContent = content.length > 100;
    const previewContent = isLongContent ? `${content.substring(0, 100)}...` : content;
    
    // 用户名信息
    const userName = review.user_name || '匿名用户';
      // 构建评价项的HTML结构
    const userId = review.user || '';
    const diaryId = review.id || '';
    
    reviewItem.innerHTML = `
        <div class="review-header">
            <div class="review-author-container">
                <a href="/diary/user/${userId}" class="user-avatar-link">
                    <img src="/static/dogo.png" alt="${userName}" class="user-avatar">
                </a>
                <a href="/diary/user/${userId}" class="review-author-link">
                    <span class="review-author">${userName}</span>
                </a>
            </div>
            <div class="review-rating">${starsHTML}</div>
        </div>
        <a href="/diary/${diaryId}" class="review-content-link">
            <div class="review-title">${review.title || '无标题'}</div>
            <div class="review-content">${previewContent}</div>
        </a>
        ${isLongContent ? '<button class="read-more-btn">查看更多</button>' : ''}
    `;
      // 为"查看更多"按钮添加点击事件
    if (isLongContent) {
        const readMoreBtn = reviewItem.querySelector('.read-more-btn');
        readMoreBtn.addEventListener('click', function(event) {
            // 阻止事件冒泡，避免点击"查看更多"时触发父元素的链接
            event.preventDefault();
            event.stopPropagation();
            
            const contentElement = reviewItem.querySelector('.review-content');
            if (contentElement.textContent.length <= 103) { // "100..." 的长度
                contentElement.textContent = content;
                readMoreBtn.textContent = '收起';
            } else {
                contentElement.textContent = previewContent;
                readMoreBtn.textContent = '查看更多';
            }
        });
    }
    
    return reviewItem;
}

// 创建星级HTML
function createStarsHTML(score) {
    const fullStars = Math.floor(score);
    const hasHalfStar = score - fullStars >= 0.5;
    let starsHTML = '';
    
    // 完整星星
    for (let i = 0; i < fullStars; i++) {
        starsHTML += '<span class="star filled">★</span>';
    }
    
    // 半星
    if (hasHalfStar) {
        starsHTML += '<span class="star half-filled">★</span>';
    }
    
    // 空星星
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        starsHTML += '<span class="star">☆</span>';
    }
    
    return starsHTML;
}

// 显示全部评价
function showAllReviews() {
    const allReviewsModal = document.getElementById('reviewsModal');
    const allReviewsList = document.getElementById('allReviewsList');
    
    if (!allReviewsModal || !allReviewsList) return;
    
    // 清空并显示加载提示
    allReviewsList.innerHTML = '<div class="loading-reviews">正在加载所有评价...</div>';
    
    // 显示模态框
    allReviewsModal.style.display = 'block';
    
    // 不论是否有缓存数据，都重新获取更多评价
    loadAllReviews();
    
    // 为模态框添加关闭事件
    const closeButton = allReviewsModal.querySelector('.close-modal');
    if (closeButton) {
        // 移除可能存在的旧事件监听器
        const newCloseButton = closeButton.cloneNode(true);
        closeButton.parentNode.replaceChild(newCloseButton, closeButton);
        
        newCloseButton.addEventListener('click', function() {
            allReviewsModal.style.display = 'none';
        });
    }
    
    // 点击模态框背景也可以关闭
    const handleModalClick = function(event) {
        if (event.target === allReviewsModal) {
            allReviewsModal.style.display = 'none';
            window.removeEventListener('click', handleModalClick);
        }
    };
    
    window.addEventListener('click', handleModalClick);
}

// 直接在页面中加载更多评价
function loadMoreReviews() {
    // 获取当前显示的评价列表
    const reviewsList = document.getElementById('reviewsList');
    if (!reviewsList) return;
    
    // 替换按钮为加载中状态
    const loadMoreBtn = document.querySelector('.view-all-reviews-btn');
    if (loadMoreBtn) {
        loadMoreBtn.disabled = true;
        loadMoreBtn.innerHTML = '<span class="spinner"></span> 加载中...';
    }
    
    // 获取景点ID
    const spotId = getSpotIdFromUrl();
    if (!spotId) {
        showEmptyMessage('reviewsList', '无法获取景点ID');
        resetLoadMoreButton();
        return;
    }
    
    // 获取已显示的评价数量，用于分页加载
    const existingReviews = reviewsList.querySelectorAll('.review-item');
    const offset = existingReviews.length;
    
    // 从API获取更多评价
    fetch(`/diary/spot/${spotId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data)) {
                // 获取所有评价
                const allReviews = data;
                
                // 如果已经加载了所有的评价
                if (offset >= allReviews.length) {
                    if (loadMoreBtn) {
                        loadMoreBtn.innerHTML = '没有更多评价了';
                        loadMoreBtn.disabled = true;
                    }
                    return;
                }
                
                // 获取下一批评价（最多5条）
                const nextBatch = allReviews.slice(offset, offset + 5);
                
                if (nextBatch.length > 0) {
                    // 添加新评价到列表
                    appendReviews(nextBatch, reviewsList);
                    
                    // 如果已经加载完所有评价
                    if (offset + nextBatch.length >= allReviews.length) {
                        if (loadMoreBtn) {
                            loadMoreBtn.innerHTML = '没有更多评价了';
                            loadMoreBtn.disabled = true;
                        }
                    } else {
                        // 还有更多评价可加载
                        resetLoadMoreButton();
                    }
                } else {
                    // 没有更多评价可加载
                    if (loadMoreBtn) {
                        loadMoreBtn.innerHTML = '没有更多评价了';
                        loadMoreBtn.disabled = true;
                    }
                }
            } else {
                // 无评价数据
                if (existingReviews.length === 0) {
                    showEmptyMessage('reviewsList', '暂无评价');
                }
                
                // 更新按钮状态
                if (loadMoreBtn) {
                    loadMoreBtn.innerHTML = '没有更多评价了';
                    loadMoreBtn.disabled = true;
                }
            }
        })
        .catch(error => {
            console.error('获取评价数据出错:', error);
            
            // 只有在没有已显示评价时才显示错误消息
            if (existingReviews.length === 0) {
                showEmptyMessage('reviewsList', '加载评价失败，请稍后再试');
            }
            
            // 恢复按钮状态
            if (loadMoreBtn) {
                loadMoreBtn.innerHTML = '加载失败，点击重试';
                loadMoreBtn.disabled = false;
            }
        });
}

// 向评价列表追加新评价
function appendReviews(reviews, container) {
    if (!container || !reviews || reviews.length === 0) return;
    
    reviews.forEach((review, index) => {
        const reviewElement = createReviewElement(review);
        
        // 添加评价ID作为数据属性，用于避免重复添加
        reviewElement.setAttribute('data-review-id', review.id || index);
        
        // 添加淡入淡出动画效果
        reviewElement.classList.add('review-fade-in');
        reviewElement.style.animationDelay = `${index * 0.1}s`;
        
        container.appendChild(reviewElement);
    });
    
    // 添加CSS动画类
    const styleElement = document.createElement('style');
    if (!document.querySelector('#review-animations')) {
        styleElement.id = 'review-animations';
        styleElement.textContent = `
            @keyframes reviewFadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .review-fade-in {
                animation: reviewFadeIn 0.5s ease forwards;
                opacity: 0;
            }
        `;
        document.head.appendChild(styleElement);
    }
}

// 重置"加载更多"按钮状态
function resetLoadMoreButton() {
    const loadMoreBtn = document.querySelector('.view-all-reviews-btn');
    if (loadMoreBtn) {
        loadMoreBtn.disabled = false;
        loadMoreBtn.textContent = '加载更多评价';
    }
}

// 加载所有评价
function loadAllReviews() {
    const spotId = getSpotIdFromUrl();
    if (!spotId) {
        showEmptyMessage('allReviewsList', '无法获取景点ID');
        return;
    }
    
    // 显示加载中状态
    const allReviewsList = document.getElementById('allReviewsList');
    if (allReviewsList) {
        if (!window.allReviewsData || window.allReviewsData.length === 0) {
            allReviewsList.innerHTML = '<div class="loading-reviews">正在加载评价...</div>';
        } else {
            // 如果已有数据，则添加一个加载更多的指示器
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading-more';
            loadingIndicator.innerHTML = '<div class="spinner"></div><span>正在加载更多...</span>';
            allReviewsList.appendChild(loadingIndicator);
        }
    }
    
    fetch(`/diary/spot/${spotId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data)) {
                if (!window.allReviewsData) {
                    window.allReviewsData = data;
                } else {
                    // 如果已经有数据，则添加新数据，确保不重复
                    const existingIds = new Set(window.allReviewsData.map(review => review.id));
                    const newReviews = data.filter(review => !existingIds.has(review.id));
                    window.allReviewsData = [...window.allReviewsData, ...newReviews];
                }
                
                // 渲染所有评价
                renderAllReviews(window.allReviewsData, document.getElementById('allReviewsList'));
                
                // 如果评价数量很多，添加一个"加载更多"按钮
                if (data.length >= 10) {
                    addLoadMoreButton(allReviewsList);
                }
            } else {
                showEmptyMessage('allReviewsList', '暂无评价');
            }
        })
        .catch(error => {
            console.error('获取全部评价数据出错:', error);
            showEmptyMessage('allReviewsList', '加载评价失败，请稍后再试');
        });
}

// 渲染所有评价，包括分页逻辑
function renderAllReviews(reviews, container) {
    if (!container) return;
    
    // 清除加载指示器
    const loadingElement = container.querySelector('.loading-reviews, .loading-more');
    if (loadingElement) {
        container.removeChild(loadingElement);
    }
    
    if (!reviews || reviews.length === 0) {
        showEmptyMessage(container.id, '暂无评价');
        return;
    }
    
    // 如果是首次加载，清空容器
    if (!window.reviewsPageLoaded) {
        container.innerHTML = '';
        window.reviewsPageLoaded = true;
    }
    
    // 创建评价项元素
    reviews.forEach(review => {
        // 检查此评价是否已经渲染过
        const existingReview = container.querySelector(`[data-review-id="${review.id}"]`);
        if (!existingReview) {
            const reviewElement = createReviewElement(review);
            reviewElement.setAttribute('data-review-id', review.id);
            container.appendChild(reviewElement);
        }
    });
}

// 添加"加载更多"按钮
function addLoadMoreButton(container) {
    // 移除现有的加载更多按钮（如果有）
    const existingButton = container.querySelector('.load-more-btn');
    if (existingButton) {
        container.removeChild(existingButton);
    }
    
    // 创建新的加载更多按钮
    const loadMoreBtn = document.createElement('button');
    loadMoreBtn.className = 'load-more-btn';
    loadMoreBtn.textContent = '加载更多评价';
    loadMoreBtn.addEventListener('click', function() {
        // 点击后替换为加载中状态
        loadMoreBtn.innerHTML = '<span class="spinner small"></span> 加载中...';
        loadMoreBtn.disabled = true;
        
        // 这里模拟加载更多的逻辑
        setTimeout(() => {
            // 实际应用中应该发送带有分页参数的请求
            loadAllReviews();
            
            // 移除当前的加载更多按钮
            if (container.contains(loadMoreBtn)) {
                container.removeChild(loadMoreBtn);
            }
        }, 800);
    });
    
    container.appendChild(loadMoreBtn);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 设置登出功能
function setupLogout() {
    const logoutBtn = document.getElementById('logout-button');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            fetch('/api/logout', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('登出成功', 'success');
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 1000);
                    } else {
                        showNotification('登出失败', 'error');
                    }
                })
                .catch(error => {
                    console.error('Logout error:', error);
                    showNotification('登出失败', 'error');
                });
        });
    }
}

// 创建浮动元素动画
function createFloatingElements() {
    const container = document.querySelector('.main-content');
    if (!container) return;
    
    for (let i = 0; i < 8; i++) {
        const element = document.createElement('div');
        element.className = 'floating-element';
        element.style.position = 'absolute';
        element.style.width = Math.random() * 15 + 5 + 'px';
        element.style.height = element.style.width;
        element.style.background = `rgba(0, 82, 217, ${Math.random() * 0.1 + 0.02})`;
        element.style.left = Math.random() * 100 + '%';
        element.style.top = Math.random() * 100 + '%';
        element.style.animation = `float ${Math.random() * 4 + 4}s ease-in-out infinite`;
        element.style.animationDelay = Math.random() * 2 + 's';
        element.style.zIndex = '-1';
        
        container.appendChild(element);
    }
}

// 数据统计动画
function animateStats() {
    const statsNumbers = document.querySelectorAll('.stats-number');
    
    statsNumbers.forEach(stat => {
        const target = parseInt(stat.textContent);
        const duration = 2000; // 2 seconds
        const step = target / (duration / 16); // 60fps
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            stat.textContent = Math.floor(current);
        }, 16);
    });
}

// 页面可见时触发统计动画
function setupStatsAnimation() {
    const statsCards = document.querySelectorAll('.stats-card');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        statsCards.forEach(card => observer.observe(card));
    }
}

// 收藏功能
function setupFavoriteFeature() {
    const favoriteButtons = document.querySelectorAll('[data-action="favorite"]');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const spotId = this.dataset.spotId || getSpotIdFromUrl();
            const isFavorited = this.classList.contains('favorited');
            
            // 切换收藏状态
            toggleFavorite(spotId, !isFavorited, this);
        });
    });
}

// 切换收藏状态
function toggleFavorite(spotId, favorite, button) {
    const action = favorite ? 'add' : 'remove';
    
    fetch(`/api/favorites/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ spot_id: spotId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (favorite) {
                button.classList.add('favorited');
                button.innerHTML = '<i class="fas fa-heart"></i> 已收藏';
                showNotification('已添加到收藏', 'success');
            } else {
                button.classList.remove('favorited');
                button.innerHTML = '<i class="far fa-heart"></i> 收藏';
                showNotification('已取消收藏', 'info');
            }
        } else {
            showNotification(data.message || '操作失败', 'error');
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        showNotification('操作失败，请重试', 'error');
    });
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '1rem 1.5rem';
    notification.style.borderRadius = '8px';
    notification.style.zIndex = '3000';
    notification.style.transform = 'translateX(400px)';
    notification.style.transition = 'transform 0.3s ease';
    
    // 设置颜色
    const colors = {
        success: { bg: '#d4edda', text: '#155724', border: '#c3e6cb' },
        error: { bg: '#f8d7da', text: '#721c24', border: '#f5c6cb' },
        info: { bg: '#d1ecf1', text: '#0c5460', border: '#bee5eb' }
    };
    
    const color = colors[type] || colors.info;
    notification.style.backgroundColor = color.bg;
    notification.style.color = color.text;
    notification.style.border = `1px solid ${color.border}`;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 滑入动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动移除
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // ESC键关闭模态框
    if (e.key === 'Escape') {
        closeMapModal();
        const imageOverlay = document.querySelector('.image-preview-overlay');
        if (imageOverlay) {
            document.body.removeChild(imageOverlay);
        }
    }
    
    // Alt + M 打开地图
    if (e.altKey && e.key === 'm') {
        e.preventDefault();
        const mapButton = document.querySelector('[data-action="view-map"]');
        if (mapButton) {
            mapButton.click();
        }
    }
    
    // Alt + F 收藏/取消收藏
    if (e.altKey && e.key === 'f') {
        e.preventDefault();
        const favoriteButton = document.querySelector('[data-action="favorite"]');
        if (favoriteButton) {
            favoriteButton.click();
        }
    }
});

// 页面初始化完成后的设置
window.addEventListener('load', function() {
    setupStatsAnimation();
    setupFavoriteFeature();
});
