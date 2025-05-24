// ===== 现代化旅游日记搜索交互脚本 =====

document.addEventListener('DOMContentLoaded', () => {
    // ===== 全局状态管理 =====
    const state = {
        currentDiaries: [],
        isLoading: false,
        searchTimeout: null,
        currentPage: 1,
        hasMoreData: true,
        selectedFilters: new Set()
    };

    // ===== DOM元素获取 =====
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
        diaryCardsContainer: document.querySelector('.diary-cards-container'),
        noResults: document.querySelector('.no-results-container'),
        resultsStats: document.querySelector('.search-results-stats'),
        
        // 用户信息
        username: document.getElementById('username'),
        logoutButton: document.getElementById('logout-button'),
        
        // 头部搜索
        headerSearchSelect: document.querySelector('.header .search-bar select'),
        headerSearchInput: document.querySelector('.header .search-input input'),
        headerSearchButton: document.querySelector('.header .search-button'),
        
        // 返回顶部按钮
        backToTop: document.getElementById('back-to-top'),
        
        // 日记卡片
        diaryCards: document.querySelectorAll('.diary-card'),
        viewDiaryBtns: document.querySelectorAll('.view-diary-btn')
    };    // ===== 初始化函数 =====
    function init() {
        hidePageLoader();
        setupEventListeners();
        checkUserSession();
        setupScrollEffects();
        setupImageLazyLoading();
        setupImagePreloading();
        setupSearchEnhancements();
        animateCards();
        setupFormValidation();
    }

    // ===== 页面加载器控制 =====
    function hidePageLoader() {
        setTimeout(() => {
            if (elements.pageLoader) {
                elements.pageLoader.classList.add('hidden');
                setTimeout(() => {
                    elements.pageLoader.remove();
                }, 500);
            }
        }, 1000);
    }

    // ===== 事件监听器设置 =====
    function setupEventListeners() {
        // 搜索表单
        if (elements.searchForm) {
            elements.searchForm.addEventListener('submit', handleFormSubmit);
        }
        
        // 搜索输入框
        if (elements.searchKeyword) {
            elements.searchKeyword.addEventListener('input', debouncedSearchSuggestions);
            elements.searchKeyword.addEventListener('focus', showSearchSuggestions);
            elements.searchKeyword.addEventListener('blur', hideSearchSuggestions);
            elements.searchKeyword.addEventListener('keypress', handleKeyPress);
        }
        
        // 筛选和排序
        if (elements.searchType) {
            elements.searchType.addEventListener('change', handleFilterChange);
        }
        
        if (elements.sortBy) {
            elements.sortBy.addEventListener('change', handleSortChange);
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

        // 用户操作
        if (elements.logoutButton) {
            elements.logoutButton.addEventListener('click', handleLogout);
        }

        // 返回顶部
        if (elements.backToTop) {
            elements.backToTop.addEventListener('click', scrollToTop);
        }

        // 日记卡片交互
        elements.diaryCards.forEach(card => {
            card.addEventListener('mouseenter', handleCardHover);
            card.addEventListener('mouseleave', handleCardLeave);
            card.addEventListener('click', handleCardClick);
        });

        // 查看详情按钮
        elements.viewDiaryBtns.forEach(btn => {
            btn.addEventListener('click', handleViewDiary);
        });

        // 窗口事件
        window.addEventListener('scroll', handleScroll);
        window.addEventListener('resize', handleResize);
        
        // 键盘导航
        document.addEventListener('keydown', handleKeyboardNavigation);
    }

    // ===== 表单提交处理 =====
    function handleFormSubmit(e) {
        // 允许正常提交，但添加加载状态
        showLoadingState();
        
        // 保存搜索参数到会话存储
        const formData = new FormData(elements.searchForm);
        const searchParams = Object.fromEntries(formData.entries());
        sessionStorage.setItem('diarySearchParams', JSON.stringify(searchParams));
    }

    // ===== 键盘事件处理 =====
    function handleKeyPress(e) {
        if (e.key === 'Enter' && e.target === elements.searchKeyword) {
            // 如果在搜索框中按回车，触发搜索
            elements.searchSubmitBtn.click();
        }
    }

    // ===== 筛选和排序处理 =====
    function handleFilterChange() {
        // 自动提交表单当筛选条件改变时
        debounce(() => {
            elements.searchForm.submit();
        }, 300)();
    }

    function handleSortChange() {
        // 自动提交表单当排序改变时
        debounce(() => {
            elements.searchForm.submit();
        }, 300)();
    }

    // ===== 头部搜索处理 =====
    function handleHeaderSearch() {
        const searchValue = elements.headerSearchInput?.value.trim();
        const searchType = elements.headerSearchSelect?.value;
        
        if (!searchValue) return;
        
        if (searchType === 'diary') {
            // 当前页面搜索
            elements.searchKeyword.value = searchValue;
            elements.searchForm.submit();
        } else if (searchType === 'spot') {
            // 跳转到景区搜索
            window.location.href = `/spots/search?keyword=${encodeURIComponent(searchValue)}`;
        }
    }

    // ===== 用户会话处理 =====
    function checkUserSession() {
        const usernameSpan = elements.username;
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
                if (usernameSpan) {
                    usernameSpan.textContent = '错误';
                }
                // 可选：也在此处重定向到登录页
                window.location.href = '/login';
            });
    }

    function handleLogout() {
        if (confirm('确定要登出吗？')) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
    }

    // ===== 卡片交互处理 =====
    function handleCardHover(e) {
        const card = e.currentTarget;
        card.style.transform = 'translateY(-8px) scale(1.02)';
        
        // 添加悬浮效果
        const image = card.querySelector('.diary-card-image img');
        if (image) {
            image.style.transform = 'scale(1.05)';
        }
    }

    function handleCardLeave(e) {
        const card = e.currentTarget;
        card.style.transform = '';
        
        const image = card.querySelector('.diary-card-image img');
        if (image) {
            image.style.transform = '';
        }
    }

    function handleCardClick(e) {
        // 如果点击的不是按钮，则导航到日记详情
        if (!e.target.closest('.view-diary-btn')) {
            const diaryId = e.currentTarget.dataset.diaryId;
            if (diaryId) {
                window.location.href = `/diary/${diaryId}`;
            }
        }
    }

    function handleViewDiary(e) {
        e.stopPropagation();
        
        // 添加点击动画
        const btn = e.currentTarget;
        btn.style.transform = 'translateY(1px)';
        setTimeout(() => {
            btn.style.transform = '';
        }, 150);
    }

    // ===== 滚动效果处理 =====
    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // 返回顶部按钮显示/隐藏
        if (elements.backToTop) {
            if (scrollTop > 300) {
                elements.backToTop.classList.add('visible');
            } else {
                elements.backToTop.classList.remove('visible');
            }
        }
        
        // 视差效果
        applyParallaxEffect(scrollTop);
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    // ===== 响应式处理 =====
    function handleResize() {
        debounce(() => {
            adjustLayoutForScreenSize();
        }, 250)();
    }

    function adjustLayoutForScreenSize() {
        const width = window.innerWidth;
        
        if (width < 768) {
            // 移动端调整
            adjustMobileLayout();
        } else {
            // 桌面端调整
            adjustDesktopLayout();
        }
    }

    function adjustMobileLayout() {
        // 移动端特定调整
        const searchForm = elements.searchForm;
        if (searchForm) {
            searchForm.style.gridTemplateColumns = '1fr';
        }
    }

    function adjustDesktopLayout() {
        // 桌面端特定调整
        const searchForm = elements.searchForm;
        if (searchForm) {
            searchForm.style.gridTemplateColumns = 'repeat(auto-fit, minmax(250px, 1fr))';
        }
    }

    // ===== 视差效果 =====
    function applyParallaxEffect(scrollTop) {
        const title = document.querySelector('.diary-search-page-title');
        if (title) {
            const parallaxSpeed = 0.3;
            title.style.transform = `translateY(${scrollTop * parallaxSpeed}px)`;
        }
    }

    // ===== 滚动动画设置 =====
    function setupScrollEffects() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // 观察所有日记卡片
        elements.diaryCards.forEach(card => {
            observer.observe(card);
        });

        // 观察其他需要动画的元素
        const animatedElements = document.querySelectorAll(
            '.diary-search-controls, .search-results-stats, .no-results-container'
        );
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }    // ===== 图片懒加载 =====
    function setupImageLazyLoading() {
        // 创建 Intersection Observer 来监控图片
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    loadImage(img);
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px', // 提前50px开始加载
            threshold: 0.1
        });

        // 观察所有懒加载图片
        const lazyImages = document.querySelectorAll('img.lazy-load');
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });

        // 预加载前几张图片
        preloadInitialImages(lazyImages);
    }    function loadImage(img) {
        const src = img.dataset.src;
        if (!src) return;

        // 显示加载状态
        img.classList.add('loading');
        
        // 获取相关元素
        const wrapper = img.closest('.image-wrapper');
        const skeleton = wrapper?.querySelector('.image-skeleton');
        const loadingIndicator = wrapper?.querySelector('.image-loading-indicator');
        const progressBar = wrapper?.querySelector('.image-progress-bar');
        
        // 显示加载指示器
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        
        // 启动进度条动画
        if (progressBar) {
            progressBar.classList.add('loading');
        }
        
        // 创建新的图片对象来预加载
        const imageLoader = new Image();
        
        // 设置加载超时
        const loadTimeout = setTimeout(() => {
            imageLoader.onload = null;
            imageLoader.onerror();
        }, 10000); // 10秒超时
        
        imageLoader.onload = () => {
            clearTimeout(loadTimeout);
            
            // 图片加载成功
            img.src = src;
            img.classList.remove('loading');
            img.classList.add('loaded', 'high-quality');
            
            // 隐藏加载元素
            if (skeleton) {
                skeleton.classList.add('hidden');
                setTimeout(() => skeleton.remove(), 300);
            }
            
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            if (progressBar) {
                progressBar.style.transform = 'scaleX(1)';
                setTimeout(() => {
                    progressBar.classList.remove('loading');
                    progressBar.style.display = 'none';
                }, 500);
            }
            
            // 添加淡入动画
            requestAnimationFrame(() => {
                img.style.opacity = '1';
            });
            
            // 图片加载完成事件
            img.dispatchEvent(new CustomEvent('imageLoaded', {
                detail: { src, loadTime: Date.now() }
            }));
        };
        
        imageLoader.onerror = () => {
            clearTimeout(loadTimeout);
            
            // 图片加载失败
            img.classList.remove('loading');
            img.classList.add('error');
            
            // 隐藏加载指示器
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            if (progressBar) {
                progressBar.classList.remove('loading');
                progressBar.style.display = 'none';
            }
            
            // 显示错误占位符
            if (skeleton) {
                skeleton.innerHTML = `
                    <div class="image-error-placeholder">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>图片加载失败</span>
                        <button class="retry-load-btn" data-src="${src}">重试</button>
                    </div>
                `;
                skeleton.classList.remove('hidden');
                
                // 添加重试功能
                const retryBtn = skeleton.querySelector('.retry-load-btn');
                if (retryBtn) {
                    retryBtn.addEventListener('click', () => {
                        img.classList.remove('error');
                        loadImage(img);
                    });
                }
            }
            
            // 图片加载失败事件
            img.dispatchEvent(new CustomEvent('imageError', {
                detail: { src, error: 'Load failed' }
            }));
        };
        
        // 开始加载图片
        imageLoader.src = src;
    }

    function preloadInitialImages(lazyImages) {
        // 预加载前6张图片以提供更好的用户体验
        const initialCount = Math.min(6, lazyImages.length);
        
        for (let i = 0; i < initialCount; i++) {
            const img = lazyImages[i];
            if (img && !img.src) {
                loadImage(img);
            }
        }
    }

    // ===== 图片预加载优化 =====
    function setupImagePreloading() {
        // 当用户快速滚动时，预加载即将进入视口的图片
        let scrollTimeout;
        
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                preloadUpcomingImages();
            }, 100);
        });
    }

    function preloadUpcomingImages() {
        const scrollTop = window.pageYOffset;
        const windowHeight = window.innerHeight;
        const preloadDistance = windowHeight * 2; // 预加载距离：2个屏幕高度
        
        const lazyImages = document.querySelectorAll('img.lazy-load:not(.loaded):not(.loading)');
        
        lazyImages.forEach(img => {
            const rect = img.getBoundingClientRect();
            const elementTop = rect.top + scrollTop;
            
            // 如果图片在预加载距离内，开始加载
            if (elementTop - scrollTop < windowHeight + preloadDistance) {
                loadImage(img);
            }
        });
    }

    // ===== 搜索增强功能 =====
    function setupSearchEnhancements() {
        // 搜索历史功能
        loadSearchHistory();
        
        // 搜索建议功能
        setupSearchSuggestions();
        
        // 自动完成功能
        setupAutoComplete();
    }

    function loadSearchHistory() {
        const history = JSON.parse(localStorage.getItem('diarySearchHistory') || '[]');
        // 可以在这里显示搜索历史
    }

    function saveSearchTerm(term) {
        if (!term.trim()) return;
        
        let history = JSON.parse(localStorage.getItem('diarySearchHistory') || '[]');
        history = history.filter(item => item !== term);
        history.unshift(term);
        history = history.slice(0, 10); // 保留最近10个搜索
        
        localStorage.setItem('diarySearchHistory', JSON.stringify(history));
    }

    function setupSearchSuggestions() {
        // 这里可以添加搜索建议逻辑
        // 例如从服务器获取热门搜索词
    }

    function setupAutoComplete() {
        // 这里可以添加自动完成逻辑
    }

    // ===== 表单验证 =====
    function setupFormValidation() {
        if (elements.searchKeyword) {
            elements.searchKeyword.addEventListener('input', validateSearchInput);
        }
    }

    function validateSearchInput() {
        const value = elements.searchKeyword.value;
        const isValid = value.length <= 100; // 限制搜索关键词长度
        
        if (!isValid) {
            elements.searchKeyword.setCustomValidity('搜索关键词不能超过100个字符');
        } else {
            elements.searchKeyword.setCustomValidity('');
        }
    }

    // ===== 卡片动画 =====
    function animateCards() {
        elements.diaryCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-in');
        });
    }

    // ===== 加载状态 =====
    function showLoadingState() {
        if (elements.searchSubmitBtn) {
            elements.searchSubmitBtn.disabled = true;
            elements.searchSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 搜索中...';
        }
    }

    function hideLoadingState() {
        if (elements.searchSubmitBtn) {
            elements.searchSubmitBtn.disabled = false;
            elements.searchSubmitBtn.innerHTML = '<i class="fas fa-search"></i> 搜索日记';
        }
    }

    // ===== 键盘导航 =====
    function handleKeyboardNavigation(e) {
        // ESC键清除搜索
        if (e.key === 'Escape') {
            if (elements.searchKeyword && elements.searchKeyword === document.activeElement) {
                elements.searchKeyword.blur();
            }
        }
        
        // Ctrl+K 聚焦搜索框
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            if (elements.searchKeyword) {
                elements.searchKeyword.focus();
                elements.searchKeyword.select();
            }
        }
    }

    // ===== 搜索建议功能 =====
    const debouncedSearchSuggestions = debounce(() => {
        // 这里可以实现搜索建议功能
        const query = elements.searchKeyword?.value.trim();
        if (query && query.length > 2) {
            // 获取搜索建议
            fetchSearchSuggestions(query);
        }
    }, 300);

    function showSearchSuggestions() {
        // 显示搜索建议下拉框
    }

    function hideSearchSuggestions() {
        // 隐藏搜索建议下拉框
        setTimeout(() => {
            // 延迟隐藏以允许点击建议项
        }, 200);
    }

    function fetchSearchSuggestions(query) {
        // 这里可以向服务器请求搜索建议
        // fetch(`/api/diary/search-suggestions?q=${encodeURIComponent(query)}`)
    }

    // ===== 工具函数 =====
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
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }    // ===== 性能优化 =====
    function setupPerformanceOptimizations() {
        // 使用 requestIdleCallback 进行非关键任务
        if (window.requestIdleCallback) {
            requestIdleCallback(() => {
                // 预加载关键资源
                preloadCriticalResources();
                // 设置图片缓存策略
                setupImageCaching();
            });
        }
        
        // 内存管理
        setupMemoryManagement();
        
        // 网络优化
        setupNetworkOptimizations();
    }

    function preloadCriticalResources() {
        // 预加载可能需要的图片或资源
        const imageUrls = Array.from(elements.diaryCards)
            .slice(0, 6) // 只预加载前6个
            .map(card => card.querySelector('img.lazy-load'))
            .filter(img => img && img.dataset.src)
            .map(img => img.dataset.src);
        
        imageUrls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            link.as = 'image';
            document.head.appendChild(link);
        });
    }

    function setupImageCaching() {
        // 设置图片缓存策略
        if ('serviceWorker' in navigator) {
            // 可以在这里注册 Service Worker 来缓存图片
            navigator.serviceWorker.register('/sw.js').catch(() => {
                // 静默失败
            });
        }
    }

    function setupMemoryManagement() {
        // 当页面隐藏时，清理不必要的资源
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // 页面隐藏时的清理工作
                cleanupOffscreenImages();
            }
        });
    }

    function cleanupOffscreenImages() {
        // 清理距离当前视口很远的已加载图片，释放内存
        const scrollTop = window.pageYOffset;
        const windowHeight = window.innerHeight;
        const cleanupDistance = windowHeight * 5; // 超过5个屏幕高度的图片
        
        const loadedImages = document.querySelectorAll('img.lazy-load.loaded');
        
        loadedImages.forEach(img => {
            const rect = img.getBoundingClientRect();
            const elementTop = rect.top + scrollTop;
            
            // 如果图片距离当前视口很远，清理它
            if (Math.abs(elementTop - scrollTop) > cleanupDistance) {
                // 保存原始src到data-src，清空当前src
                if (img.src && !img.dataset.originalSrc) {
                    img.dataset.originalSrc = img.src;
                    img.src = '';
                    img.classList.remove('loaded');
                    
                    // 重新观察这个图片
                    setupImageObserver(img);
                }
            }
        });
    }

    function setupImageObserver(img) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const targetImg = entry.target;
                    if (targetImg.dataset.originalSrc) {
                        targetImg.src = targetImg.dataset.originalSrc;
                        targetImg.classList.add('loaded');
                        delete targetImg.dataset.originalSrc;
                    } else if (targetImg.dataset.src) {
                        loadImage(targetImg);
                    }
                    imageObserver.unobserve(targetImg);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });
        
        imageObserver.observe(img);
    }

    function setupNetworkOptimizations() {
        // 检测网络连接质量
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            // 根据网络质量调整图片加载策略
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                // 慢网络：减少预加载数量
                window.PRELOAD_COUNT = 2;
                window.PRELOAD_DISTANCE = window.innerHeight;
            } else if (connection.effectiveType === '3g') {
                // 中等网络：正常预加载
                window.PRELOAD_COUNT = 4;
                window.PRELOAD_DISTANCE = window.innerHeight * 1.5;
            } else {
                // 快网络：增加预加载
                window.PRELOAD_COUNT = 8;
                window.PRELOAD_DISTANCE = window.innerHeight * 2;
            }
        }
    }

    // ===== 错误处理 =====
    function handleError(error, context = '') {
        console.error(`Error in diary search ${context}:`, error);
        
        // 可以在这里添加错误报告逻辑
        // 或显示用户友好的错误消息
    }

    // ===== 分析和统计 =====
    function trackUserAction(action, data = {}) {
        // 这里可以添加用户行为分析
        // 例如发送到 Google Analytics 或其他分析服务
        console.log(`User action: ${action}`, data);
    }

    // ===== 无障碍支持 =====
    function setupAccessibility() {
        // 为动态内容添加 ARIA 标签
        if (elements.resultsStats) {
            elements.resultsStats.setAttribute('role', 'status');
            elements.resultsStats.setAttribute('aria-live', 'polite');
        }
        
        // 键盘导航支持
        elements.diaryCards.forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'article');
        });
    }

    // ===== 初始化执行 =====
    init();
    setupPerformanceOptimizations();
    setupAccessibility();
    
    // 页面卸载时清理
    window.addEventListener('beforeunload', () => {
        // 清理定时器和事件监听器
        if (state.searchTimeout) {
            clearTimeout(state.searchTimeout);
        }
    });
});

// ===== 全局可用的实用函数 =====
window.DiarySearch = {
    // 刷新搜索结果
    refresh: () => {
        window.location.reload();
    },
    
    // 清除搜索
    clearSearch: () => {
        const form = document.querySelector('.search-form');
        if (form) {
            form.reset();
            form.submit();
        }
    },
    
    // 跳转到指定日记
    goToDiary: (id) => {
        window.location.href = `/diary/${id}`;
    }
};
