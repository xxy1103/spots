// ===== 高性能旅游日记搜索交互脚本 - 优化版本 =====

document.addEventListener('DOMContentLoaded', () => {
    // ===== 全局状态管理 =====
    const state = {
        currentDiaries: [],
        isLoading: false,
        searchTimeout: null,
        currentPage: 1,
        hasMoreData: true,
        selectedFilters: new Set(),
        visibleCards: new Set(),
        intersectionObserver: null,
        loadMoreObserver: null,
        isInfiniteScrollEnabled: true,
        imageCache: new Map(),
        renderQueue: [],
        isProcessingQueue: false
    };

    // ===== 性能配置 =====
    const config = {
        lazyLoadOffset: 100,
        batchSize: 10,
        maxCacheSize: 100,
        debounceDelay: 300,
        throttleDelay: 16,
        animationDelay: 50,
        preloadDistance: window.innerHeight * 1.5
    };

    // ===== DOM元素获取（优化版本） =====
    const elements = {
        // 页面加载器
        pageLoader: document.getElementById('page-loader'),
        
        // 搜索表单元素
        searchForm: document.querySelector('.search-form'),
        searchKeyword: document.getElementById('keyword'),
        searchType: document.getElementById('type'),
        sortBy: document.getElementById('sort_by'),
        searchSubmitBtn: document.querySelector('.search-submit-btn'),
        
        // 显示元素
        diaryGrid: document.getElementById('diary-grid'),
        virtualScrollContainer: document.getElementById('virtual-scroll-container'),
        diaryCardsContainer: document.querySelector('.diary-cards-container'),
        noResults: document.querySelector('.no-results-container'),
        resultsStats: document.querySelector('.search-results-stats'),
        
        // 分页和加载更多
        loadMoreBtn: document.getElementById('load-more-btn'),
        scrollLoading: document.getElementById('scroll-loading'),
        paginationNav: document.querySelector('.pagination-nav'),
        
        // 用户信息
        username: document.getElementById('username'),
        logoutButton: document.getElementById('logout-button'),
        
        // 头部搜索
        headerSearchSelect: document.querySelector('.header .search-bar select'),
        headerSearchInput: document.querySelector('.header .search-input input'),
        headerSearchButton: document.querySelector('.header .search-button'),
        
        // 返回顶部按钮
        backToTop: document.getElementById('back-to-top')
    };

    // ===== 初始化函数 =====
    function init() {
        console.time('页面初始化');
        
        hidePageLoader();
        setupEventListeners();
        checkUserSession();
        setupOptimizedScrollEffects();
        setupOptimizedImageLazyLoading();
        setupInfiniteScroll();
        setupSearchEnhancements();
        setupFormValidation();
        initializeVisibleCards();
        setupPerformanceOptimizations();
        
        console.timeEnd('页面初始化');
    }

    // ===== 页面加载器控制（优化） =====
    function hidePageLoader() {
        requestAnimationFrame(() => {
            if (elements.pageLoader) {
                elements.pageLoader.style.opacity = '0';
                setTimeout(() => {
                    elements.pageLoader.remove();
                }, 300);
            }
        });
    }

    // ===== 优化的事件监听器设置 =====
    function setupEventListeners() {
        // 使用事件委托减少内存占用
        if (elements.diaryGrid) {
            elements.diaryGrid.addEventListener('click', handleDiaryGridClick);
            elements.diaryGrid.addEventListener('mouseenter', handleDiaryGridHover, true);
            elements.diaryGrid.addEventListener('mouseleave', handleDiaryGridLeave, true);
        }
        
        // 搜索表单
        if (elements.searchForm) {
            elements.searchForm.addEventListener('submit', handleFormSubmit);
        }
        
        // 搜索输入框（防抖处理）
        if (elements.searchKeyword) {
            elements.searchKeyword.addEventListener('input', debouncedSearchSuggestions);
            elements.searchKeyword.addEventListener('keypress', handleKeyPress);
        }
        
        // 筛选和排序（防抖处理）
        if (elements.searchType) {
            elements.searchType.addEventListener('change', debouncedFilterChange);
        }
        
        if (elements.sortBy) {
            elements.sortBy.addEventListener('change', debouncedSortChange);
        }

        // 头部搜索
        if (elements.headerSearchButton) {
            elements.headerSearchButton.addEventListener('click', handleHeaderSearch);
        }
        
        if (elements.headerSearchInput) {
            elements.headerSearchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleHeaderSearch();
            });
        }

        // 加载更多按钮
        if (elements.loadMoreBtn) {
            elements.loadMoreBtn.addEventListener('click', handleLoadMore);
        }

        // 用户操作
        if (elements.logoutButton) {
            elements.logoutButton.addEventListener('click', handleLogout);
        }

        // 返回顶部
        if (elements.backToTop) {
            elements.backToTop.addEventListener('click', scrollToTop);
        }

        // 窗口事件（节流处理）
        window.addEventListener('scroll', throttledScrollHandler);
        window.addEventListener('resize', throttledResizeHandler);
        
        // 键盘导航
        document.addEventListener('keydown', handleKeyboardNavigation);
    }

    // ===== 优化的日记网格事件处理（事件委托） =====
    function handleDiaryGridClick(e) {
        const card = e.target.closest('.diary-card');
        if (!card) return;
        
        // 如果点击的是详情按钮，阻止卡片点击
        if (e.target.closest('.view-diary-btn')) {
            return;
        }
        
        const diaryId = card.dataset.diaryId;
        if (diaryId) {
            window.location.href = `/diary/${diaryId}`;
        }
    }

    function handleDiaryGridHover(e) {
        const card = e.target.closest('.diary-card');
        if (!card) return;
        
        // 预加载图片
        preloadCardImages(card);
        
        // 添加悬停效果（使用 CSS transform 而不是 JavaScript 动画）
        card.style.transform = 'translateY(-4px)';
        card.style.boxShadow = '0 12px 40px rgba(0, 82, 217, 0.15)';
    }

    function handleDiaryGridLeave(e) {
        const card = e.target.closest('.diary-card');
        if (!card) return;
        
        card.style.transform = '';
        card.style.boxShadow = '';
    }

    // ===== 优化的图片懒加载 =====
    function setupOptimizedImageLazyLoading() {
        // 创建高性能的 Intersection Observer
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    loadImageOptimized(img);
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: `${config.preloadDistance}px 0px`,
            threshold: 0.01
        });

        // 观察所有懒加载图片
        const lazyImages = document.querySelectorAll('img.lazy-load');
        lazyImages.forEach(img => {
            imageObserver.observe(img);
            img.classList.add('observed'); // 标记为已观察
        });
    }

    // ===== 优化的图片加载函数 =====
    function loadImageOptimized(img) {
        const src = img.dataset.src;
        if (!src || img.classList.contains('loading') || img.classList.contains('loaded')) return;

        // 标记正在加载
        img.classList.add('loading');

        // 检查缓存
        if (state.imageCache.has(src)) {
            const cachedImg = state.imageCache.get(src);
            if (cachedImg.complete) {
                setImageSource(img, src);
                return;
            }
        }

        // 显示加载状态
        const wrapper = img.closest('.image-wrapper');
        const skeleton = wrapper?.querySelector('.image-skeleton');
        const loadingIndicator = wrapper?.querySelector('.image-loading-indicator');
        
        if (skeleton) skeleton.style.display = 'block';
        if (loadingIndicator) loadingIndicator.style.display = 'flex';

        // 创建新的图片对象进行预加载
        const newImg = new Image();
        
        newImg.onload = () => {
            // 缓存图片
            state.imageCache.set(src, newImg);
            
            // 清理缓存大小
            if (state.imageCache.size > config.maxCacheSize) {
                const firstKey = state.imageCache.keys().next().value;
                state.imageCache.delete(firstKey);
            }
            
            // 使用 requestAnimationFrame 优化动画
            requestAnimationFrame(() => {
                setImageSource(img, src);
                hideLoadingStates(wrapper);
                img.classList.remove('loading');
            });
        };
        
        newImg.onerror = () => {
            console.warn('图片加载失败:', src);
            hideLoadingStates(wrapper);
            showImageError(img);
            img.classList.remove('loading');
            img.classList.add('error');
        };
        
        // 设置超时处理
        setTimeout(() => {
            if (!img.classList.contains('loaded')) {
                newImg.src = src;
            }
        }, 50);
    }

    function setImageSource(img, src) {
        img.src = src;
        img.classList.add('loaded');
        img.style.opacity = '1';
    }

    function hideLoadingStates(wrapper) {
        if (!wrapper) return;
        
        const skeleton = wrapper.querySelector('.image-skeleton');
        const loadingIndicator = wrapper.querySelector('.image-loading-indicator');
        
        if (skeleton) skeleton.style.display = 'none';
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }

    function showImageError(img) {
        const wrapper = img.closest('.image-wrapper');
        if (wrapper) {
            wrapper.innerHTML = `
                <div class="image-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>图片加载失败</span>
                </div>
            `;
        }
    }

    // ===== 无限滚动优化 =====
    function setupInfiniteScroll() {
        if (!elements.loadMoreBtn) return;

        // 创建加载更多的观察器
        state.loadMoreObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !state.isLoading && state.hasMoreData) {
                    handleLoadMore();
                }
            });
        }, {
            rootMargin: '100px 0px'
        });

        // 观察加载更多按钮
        state.loadMoreObserver.observe(elements.loadMoreBtn);
    }

    // ===== 优化的加载更多功能 =====
    async function handleLoadMore() {
        if (state.isLoading || !state.hasMoreData) return;

        state.isLoading = true;
        showScrollLoading();

        try {
            const nextPage = elements.loadMoreBtn?.dataset.nextPage;
            if (!nextPage) return;

            const url = new URL(window.location.href);
            url.searchParams.set('page', nextPage);
            url.searchParams.set('ajax', '1');

            const response = await fetch(url.toString());
            const data = await response.json();

            if (data.success && data.diaries?.length > 0) {
                await appendNewDiaries(data.diaries);
                updatePaginationState(data.pagination);
            } else {
                state.hasMoreData = false;
                hideLoadMoreButton();
            }
        } catch (error) {
            console.error('加载更多日记失败:', error);
            showErrorMessage('加载失败，请稍后重试');
        } finally {
            state.isLoading = false;
            hideScrollLoading();
        }
    }

    // ===== 批量渲染新日记 =====    
    async function appendNewDiaries(diaries) {
        const fragment = document.createDocumentFragment();
        
        diaries.forEach((diary, index) => {
            const cardElement = createDiaryCard(diary, state.currentDiaries.length + index);
            fragment.appendChild(cardElement);
        });        // 使用 requestAnimationFrame 优化渲染
        requestAnimationFrame(() => {
            elements.diaryGrid.appendChild(fragment);
            
            // 重新初始化所有懒加载图片（包括新加载的）
            reinitializeLazyLoading();
            
            // 强制检查新添加的图片是否在可视区域
            setTimeout(() => {
                const newCards = elements.diaryGrid.querySelectorAll('.diary-card:not(.initialized)');
                newCards.forEach(card => {
                    card.classList.add('initialized');
                    const img = card.querySelector('img.lazy-load');
                    if (img && img.dataset.src) {
                        const rect = img.getBoundingClientRect();
                        const isVisible = rect.top < window.innerHeight + 200 && rect.bottom > -200;
                        if (isVisible) {
                            loadImageOptimized(img);
                        }
                    }
                });
            }, 100);
            
            // 更新状态
            state.currentDiaries.push(...diaries);
            
            // 触发动画
            animateNewCards();
        });
    }    // ===== 重新初始化懒加载功能 =====
    function reinitializeLazyLoading() {
        // 查找所有还没有被观察的懒加载图片
        const allLazyImages = document.querySelectorAll('img.lazy-load:not(.observed)');
        
        if (allLazyImages.length > 0) {
            // 创建新的图片observer
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        loadImageOptimized(img);
                        imageObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: `${config.preloadDistance}px 0px`,
                threshold: 0.01
            });

            // 观察所有新的懒加载图片
            allLazyImages.forEach(img => {
                imageObserver.observe(img);
                img.classList.add('observed'); // 标记为已观察
                
                // 立即检查是否在可视区域内
                const rect = img.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                if (isVisible) {
                    // 如果图片已在可视区域，立即加载
                    setTimeout(() => loadImageOptimized(img), 100);
                }
            });
        }
    }

    // ===== 创建日记卡片 =====
    function createDiaryCard(diary, index) {
        const card = document.createElement('div');
        card.className = 'diary-card';
        card.dataset.diaryId = diary.id;
        card.dataset.index = index;
        
        card.innerHTML = `
            <div class="diary-card-image">
                ${diary.img_list && diary.img_list[0] ? `
                    <div class="image-wrapper">
                        <img 
                            class="lazy-load" 
                            data-src="/${diary.img_list[0]}" 
                            alt="${diary.title}"
                            loading="lazy"
                            decoding="async">
                        <div class="image-skeleton">
                            <div class="skeleton-shimmer"></div>
                        </div>
                        <div class="image-loading-indicator">
                            <i class="fas fa-spinner image-loading-spinner"></i>
                        </div>
                        <div class="image-progress-bar"></div>
                    </div>
                ` : `
                    <div class="diary-image-placeholder">
                        <i class="fas fa-image"></i>
                        <span>暂无图片</span>
                    </div>
                `}
            </div>
            <div class="diary-card-content">
                <h3 class="diary-card-title">${diary.title}</h3>
                <p class="diary-card-preview">${(diary.content || "暂无内容").substring(0, 120)}${diary.content && diary.content.length > 120 ? '...' : ''}</p>
                
                <div class="diary-card-rating">
                    <div class="rating-stars">
                        ${generateStars(diary.value1)}
                        <span class="rating-score">${diary.value1}</span>
                    </div>
                </div>
                
                <div class="diary-card-meta">
                    <div class="diary-stats">
                        <span class="stat-item">
                            <i class="fas fa-eye"></i>
                            ${diary.value2}
                        </span>
                        <span class="stat-item">
                            <i class="fas fa-star"></i>
                            ${diary.scoreToSpot}
                        </span>
                    </div>
                    <div class="diary-date">${diary.time}</div>
                </div>
                
                <div class="diary-card-actions">
                    <a href="/diary/${diary.id}" class="view-diary-btn">
                        查看详情 <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
        `;
        
        return card;
    }

    // ===== 生成星级评分 =====
    function generateStars(rating) {
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        
        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars.push('<i class="fas fa-star"></i>');
            } else if (i === fullStars && hasHalfStar) {
                stars.push('<i class="fas fa-star-half-alt"></i>');
            } else {
                stars.push('<i class="far fa-star"></i>');
            }
        }
        
        return stars.join('');
    }

    // ===== 优化的滚动效果 =====
    function setupOptimizedScrollEffects() {
        state.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    state.visibleCards.add(entry.target);
                } else {
                    state.visibleCards.delete(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // 观察所有现有的日记卡片
        const diaryCards = document.querySelectorAll('.diary-card');
        diaryCards.forEach(card => {
            state.intersectionObserver.observe(card);
        });
    }

    // ===== 初始化可见卡片 =====
    function initializeVisibleCards() {
        const cards = document.querySelectorAll('.diary-card');
        cards.forEach((card, index) => {
            // 分批动画，避免同时触发太多动画
            setTimeout(() => {
                card.classList.add('animate-in');
            }, index * config.animationDelay);
        });
    }

    // ===== 新卡片动画 =====
    function animateNewCards() {
        const newCards = elements.diaryGrid.querySelectorAll('.diary-card:not(.animate-in)');
        newCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animate-in');
            }, index * 50);
        });
    }

    // ===== 预加载卡片图片 =====
    function preloadCardImages(card) {
        const img = card.querySelector('img.lazy-load:not(.loaded)');
        if (img && img.dataset.src) {
            loadImageOptimized(img);
        }
    }

    // ===== 显示和隐藏加载状态 =====
    function showScrollLoading() {
        if (elements.scrollLoading) {
            elements.scrollLoading.style.display = 'block';
        }
        if (elements.loadMoreBtn) {
            elements.loadMoreBtn.style.display = 'none';
        }
    }

    function hideScrollLoading() {
        if (elements.scrollLoading) {
            elements.scrollLoading.style.display = 'none';
        }
    }

    function hideLoadMoreButton() {
        if (elements.loadMoreBtn) {
            elements.loadMoreBtn.style.display = 'none';
        }
    }

    // ===== 更新分页状态 =====
    function updatePaginationState(pagination) {
        if (pagination) {
            state.hasMoreData = pagination.has_next;
            if (pagination.has_next && elements.loadMoreBtn) {
                elements.loadMoreBtn.dataset.nextPage = pagination.next_num;
                elements.loadMoreBtn.style.display = 'block';
            } else {
                hideLoadMoreButton();
            }
        }
    }

    // ===== 错误消息显示 =====
    function showErrorMessage(message) {
        // 可以在这里添加更好的错误提示UI
        console.error(message);
    }

    // ===== 防抖和节流函数 =====
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

    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // ===== 防抖处理的事件函数 =====
    const debouncedSearchSuggestions = debounce(() => {
        const query = elements.searchKeyword?.value.trim();
        if (query && query.length > 2) {
            // 搜索建议功能
        }
    }, config.debounceDelay);

    const debouncedFilterChange = debounce(() => {
        if (elements.searchForm) {
            elements.searchForm.submit();
        }
    }, config.debounceDelay);

    const debouncedSortChange = debounce(() => {
        if (elements.searchForm) {
            elements.searchForm.submit();
        }
    }, config.debounceDelay);

    // ===== 节流处理的滚动和窗口大小调整 =====
    const throttledScrollHandler = throttle(() => {
        handleScroll();
    }, config.throttleDelay);

    const throttledResizeHandler = throttle(() => {
        handleResize();
    }, 250);

    // ===== 其他功能函数（保持原有逻辑） =====
    function handleFormSubmit(e) {
        showLoadingState();
        const formData = new FormData(elements.searchForm);
        const searchParams = Object.fromEntries(formData.entries());
        sessionStorage.setItem('diarySearchParams', JSON.stringify(searchParams));
    }

    function handleKeyPress(e) {
        if (e.key === 'Enter' && e.target === elements.searchKeyword) {
            elements.searchSubmitBtn?.click();
        }
    }    function handleHeaderSearch() {
        const keyword = elements.headerSearchInput?.value.trim();
        const searchType = elements.headerSearchSelect?.value;
        
        if (!keyword) {
            // 空关键词提示
            if (elements.headerSearchInput) {
                elements.headerSearchInput.style.borderColor = 'red';
                elements.headerSearchInput.style.animation = 'shake 0.5s';
                setTimeout(() => {
                    elements.headerSearchInput.style.borderColor = '#CCCCCC';
                    elements.headerSearchInput.style.animation = '';
                }, 500);
            }
            return;
        }
        
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

    function checkUserSession() {
        const usernameSpan = elements.username;
        fetch('/api/check-session')
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.href = '/login';
                    } else {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success) {
                    if (usernameSpan) {
                        usernameSpan.textContent = data.user.username || '用户';
                        if (data.user.user_id) {
                            usernameSpan.href = `/diary/user/${data.user.user_id}`;
                        }
                    }
                } else if (data) {
                    console.error('会话检查失败:', data.message);
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                console.error('检查会话时出错:', error);
                if (usernameSpan) {
                    usernameSpan.textContent = '错误';
                }
                window.location.href = '/login';
            });
    }

    function handleLogout() {
        fetch('/api/logout', { method: 'POST' })
            .then(() => {
                window.location.href = '/login';
            })
            .catch(error => {
                console.error('登出失败:', error);
                window.location.href = '/login';
            });
    }

    function handleScroll() {
        const scrollTop = window.pageYOffset;
        
        // 返回顶部按钮显示/隐藏
        if (elements.backToTop) {
            elements.backToTop.style.display = scrollTop > 300 ? 'block' : 'none';
        }
    }

    function handleResize() {
        // 响应式调整
        adjustLayoutForScreenSize();
    }

    function adjustLayoutForScreenSize() {
        const width = window.innerWidth;
        if (width < 768) {
            // 移动端优化
            config.batchSize = 5;
            config.preloadDistance = window.innerHeight;
        } else {
            // 桌面端优化
            config.batchSize = 10;
            config.preloadDistance = window.innerHeight * 1.5;
        }
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    function setupSearchEnhancements() {
        // 搜索增强功能
    }

    function setupFormValidation() {
        if (elements.searchKeyword) {
            elements.searchKeyword.addEventListener('input', validateSearchInput);
        }
    }

    function validateSearchInput() {
        const value = elements.searchKeyword.value;
        const isValid = value.length <= 100;
        
        if (!isValid) {
            elements.searchKeyword.setCustomValidity('搜索关键词不能超过100个字符');
        } else {
            elements.searchKeyword.setCustomValidity('');
        }
    }

    function showLoadingState() {
        if (elements.searchSubmitBtn) {
            elements.searchSubmitBtn.disabled = true;
            elements.searchSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 搜索中...';
        }
    }

    function handleKeyboardNavigation(e) {
        if (e.key === 'Escape') {
            if (elements.searchKeyword && elements.searchKeyword === document.activeElement) {
                elements.searchKeyword.blur();
            }
        }
        
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            if (elements.searchKeyword) {
                elements.searchKeyword.focus();
                elements.searchKeyword.select();
            }
        }
    }

    // ===== 性能优化 =====
    function setupPerformanceOptimizations() {
        // 预连接到图片服务器
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = window.location.origin;
        document.head.appendChild(link);
        
        // 设置网络质量检测
        if ('connection' in navigator) {
            const connection = navigator.connection;
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                config.batchSize = 3;
                config.preloadDistance = window.innerHeight * 0.5;
            }
        }
        
        // 内存清理
        setInterval(() => {
            cleanupOffscreenElements();
        }, 30000); // 每30秒清理一次
    }

    function cleanupOffscreenElements() {
        // 清理不在视窗内的图片
        const cards = document.querySelectorAll('.diary-card');
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const isOffscreen = rect.bottom < -window.innerHeight || rect.top > window.innerHeight * 2;
            
            if (isOffscreen) {
                const img = card.querySelector('img.loaded');
                if (img && img.src !== img.dataset.src) {
                    // 重置为懒加载状态以节省内存
                    img.src = '';
                    img.classList.remove('loaded');
                    img.style.opacity = '0';
                }
            }
        });
    }

    // ===== 初始化执行 =====
    init();
    
    // 页面卸载时清理
    window.addEventListener('beforeunload', () => {
        if (state.searchTimeout) {
            clearTimeout(state.searchTimeout);
        }
        if (state.intersectionObserver) {
            state.intersectionObserver.disconnect();
        }
        if (state.loadMoreObserver) {
            state.loadMoreObserver.disconnect();
        }
        state.imageCache.clear();
    });
});

// ===== 全局可用的实用函数 =====
window.DiarySearchOptimized = {
    refresh: () => {
        window.location.reload();
    },
    
    clearSearch: () => {
        const form = document.querySelector('.search-form');
        if (form) {
            form.reset();
            form.submit();
        }
    },
    
    goToDiary: (id) => {
        window.location.href = `/diary/${id}`;
    }
};
