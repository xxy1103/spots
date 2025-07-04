// ===== 现代化景区搜索交互脚本 =====

document.addEventListener('DOMContentLoaded', () => {    // ===== 全局状态管理 =====
    const state = {
        currentSpots: [],
        allSpots: [], // 存储所有景区数据
        displayedSpots: [], // 当前显示的景区
        isLoading: false,
        viewMode: 'grid',
        searchTimeout: null,
        currentPage: 1,
        hasMoreData: true,
        itemsPerPage: 16, // 每页显示16个
        currentDisplayCount: 0 // 当前显示的数量
    };

    // ===== DOM元素获取 =====
    const elements = {
        // 页面加载器
        pageLoader: document.getElementById('page-loader'),
        
        // 搜索控制元素
        searchKeyword: document.getElementById('search-keyword'),
        filterType: document.getElementById('filter-type'),
        sortBy: document.getElementById('sort-by'),
        
        // 显示元素
        spotsList: document.getElementById('spots-list'),
        noResults: document.getElementById('no-results'),
        resultsTitle: document.getElementById('results-title'),
        resultsCount: document.getElementById('results-count'),
        
        // 用户信息
        username: document.getElementById('username'),
        logoutButton: document.getElementById('logout-button'),
        
        // 头部搜索
        headerSearchSelect: document.querySelector('.header .search-bar select'),
        headerSearchInput: document.querySelector('.header .search-input input'),
        headerSearchButton: document.querySelector('.header .search-button'),
        
        // 视图模式切换
        viewModeButtons: document.querySelectorAll('.view-mode-btn'),
          // 返回顶部按钮
        backToTop: document.getElementById('back-to-top'),
        
        // 加载更多相关元素
        loadMoreContainer: document.getElementById('load-more-container'),
        loadMoreButton: document.getElementById('load-more-button'),
        loadMoreText: document.querySelector('.load-more-text'),
        loadMoreSpinner: document.querySelector('.spinner'),
        
        // 重置搜索按钮
        resetSearchBtn: document.querySelector('.reset-search-btn'),
        
        // 快速筛选标签
        filterTags: document.querySelectorAll('.filter-tag'),
        tipItems: document.querySelectorAll('.tip-item')
    };

    // ===== 景区类型数据 =====
    const spotTypes = [
        "历史建筑", "赏花胜地", "萌萌动物", "城市漫步", "夜游观景",
        "遛娃宝藏地", "展馆展览", "地标观景", "登高爬山", "踏青必去",
        "自然山水", "游乐场", "演出"
    ];    // ===== 初始化函数 =====
    function init() {
        hidePageLoader();
        setupTypeFilter();
        setupEventListeners();
        animateStatNumbers();
        checkUserSession();
        applyUrlParameters();
        setupScrollEffects();
        setupSearchSuggestions();
        adjustLayoutPositions();
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

    // ===== 统计数字动画 =====
    function animateStatNumbers() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            const target = parseInt(stat.dataset.count);
            const duration = 1000;
            const increment = target / (duration / 16);
            let current = 0;
            
            const updateNumber = () => {
                current += increment;
                if (current < target) {
                    stat.textContent = Math.floor(current);
                    requestAnimationFrame(updateNumber);
                } else {
                    stat.textContent = target;
                }
            };
              // 延迟启动动画，营造更好的视觉效果
            setTimeout(updateNumber, 750);
        });
    }

    // ===== 设置类型筛选器 =====
    function setupTypeFilter() {
        if (!elements.filterType) return;
        
        spotTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            elements.filterType.appendChild(option);
        });
    }

    // ===== 事件监听器设置 =====
    function setupEventListeners() {
        // 搜索相关
        if (elements.searchKeyword) {
            elements.searchKeyword.addEventListener('input', debouncedSearch);
            elements.searchKeyword.addEventListener('focus', showSearchSuggestions);
            elements.searchKeyword.addEventListener('blur', hideSearchSuggestions);
        }
        
        if (elements.filterType) {
            elements.filterType.addEventListener('change', fetchAndDisplaySpots);
        }
        
        if (elements.sortBy) {
            elements.sortBy.addEventListener('change', fetchAndDisplaySpots);
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

        // 视图模式切换
        elements.viewModeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.target.closest('.view-mode-btn').dataset.mode;
                switchViewMode(mode);
            });
        });

        // 返回顶部
        if (elements.backToTop) {
            elements.backToTop.addEventListener('click', scrollToTop);
        }

        // 重置搜索
        if (elements.resetSearchBtn) {
            elements.resetSearchBtn.addEventListener('click', resetSearch);
        }

        // 快速筛选标签
        elements.filterTags.forEach(tag => {
            tag.addEventListener('click', (e) => {
                const type = e.target.closest('.filter-tag').dataset.type;
                applyQuickFilter(type);
            });
        });

        // 关键词提示
        elements.tipItems.forEach(tip => {
            tip.addEventListener('click', (e) => {
                const keyword = e.target.dataset.keyword;
                if (elements.searchKeyword) {
                    elements.searchKeyword.value = keyword;
                    fetchAndDisplaySpots();
                }
            });
        });        // 窗口滚动事件
        window.addEventListener('scroll', handleScroll);
        
        // 加载更多按钮事件
        if (elements.loadMoreButton) {
            elements.loadMoreButton.addEventListener('click', loadMoreSpots);
        }
        
        // 窗口大小变化
        window.addEventListener('resize', handleResize);
    }

    // ===== 滚动效果设置 =====
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

        // 观察需要动画的元素
        document.querySelectorAll('.control-card, .spot-card').forEach(el => {
            observer.observe(el);
        });
    }

    // ===== 搜索建议功能 =====
    function setupSearchSuggestions() {
        const suggestions = [
            { text: '故宫博物院', icon: 'fas fa-monument' },
            { text: '天安门广场', icon: 'fas fa-landmark' },
            { text: '颐和园', icon: 'fas fa-tree' },
            { text: '长城', icon: 'fas fa-mountain' },
            { text: '天坛公园', icon: 'fas fa-yin-yang' }
        ];

        window.searchSuggestions = suggestions;
    }

    function showSearchSuggestions() {
        // 实现搜索建议显示逻辑
        // 这里可以根据输入内容显示相关建议
    }

    function hideSearchSuggestions() {
        setTimeout(() => {
            const suggestionsEl = document.getElementById('search-suggestions');
            if (suggestionsEl) {
                suggestionsEl.style.display = 'none';
            }
        }, 200);
    }

    // ===== 防抖搜索 =====
    function debouncedSearch() {
        if (state.searchTimeout) {
            clearTimeout(state.searchTimeout);
        }
        
        state.searchTimeout = setTimeout(() => {
            fetchAndDisplaySpots();
        }, 300);
    }

    // ===== 视图模式切换 =====
    function switchViewMode(mode) {
        state.viewMode = mode;
        
        // 更新按钮状态
        elements.viewModeButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            }
        });

        // 更新网格布局
        if (elements.spotsList) {
            elements.spotsList.classList.remove('grid-view', 'list-view');
            elements.spotsList.classList.add(`${mode}-view`);
        }

        // 添加切换动画
        if (elements.spotsList) {
            elements.spotsList.style.opacity = '0';
            setTimeout(() => {
                elements.spotsList.style.opacity = '1';
            }, 150);
        }
    }

    // ===== 快速筛选 =====
    function applyQuickFilter(type) {
        if (elements.filterType) {
            elements.filterType.value = type;
        }
        
        // 更新标签状态
        elements.filterTags.forEach(tag => {
            tag.classList.remove('active');
            if (tag.dataset.type === type) {
                tag.classList.add('active');
            }
        });
        
        fetchAndDisplaySpots();
    }    // ===== 重置搜索 =====
    function resetSearch() {
        if (elements.searchKeyword) elements.searchKeyword.value = '';
        if (elements.filterType) elements.filterType.value = '';
        if (elements.sortBy) elements.sortBy.value = 'default';
        
        // 重置快速筛选标签
        elements.filterTags.forEach(tag => {
            tag.classList.remove('active');
        });
        
        // 重置分页状态
        resetPaginationState();
        
        fetchAndDisplaySpots();
        
        // 平滑滚动到顶部
        scrollToTop();
    }

    // ===== 滚动到顶部 =====
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    // ===== 滚动处理 =====
    function handleScroll() {
        const scrollY = window.scrollY;
        
        // 显示/隐藏返回顶部按钮
        if (elements.backToTop) {
            if (scrollY > 300) {
                elements.backToTop.style.display = 'flex';
                elements.backToTop.style.opacity = '1';
            } else {
                elements.backToTop.style.opacity = '0';
                setTimeout(() => {
                    if (window.scrollY <= 300) {
                        elements.backToTop.style.display = 'none';
                    }
                }, 150);
            }
        }

        // 头部阴影效果
        const header = document.querySelector('.header');
        if (header) {
            if (scrollY > 10) {
                header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
            } else {
                header.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }
        }
    }

    // ===== 窗口大小变化处理 =====
    function handleResize() {
        // 响应式调整
        const width = window.innerWidth;
        
        if (width <= 768 && state.viewMode === 'list') {
            switchViewMode('grid');
        }
    }

    // ===== URL参数解析 =====
    function applyUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const keywordParam = urlParams.get('keyword');
        const typeParam = urlParams.get('type');

        if (elements.searchKeyword && keywordParam) {
            elements.searchKeyword.value = keywordParam;
        }
        
        if (elements.filterType && typeParam && spotTypes.includes(typeParam)) {
            elements.filterType.value = typeParam;
        }
        
        fetchAndDisplaySpots();
    }

    // ===== 获取并显示景区数据 =====
    async function fetchAndDisplaySpots() {
        if (!elements.spotsList || state.isLoading) return;
        
        state.isLoading = true;
        showLoadingState();

        const keyword = elements.searchKeyword ? elements.searchKeyword.value.trim() : '';
        const selectedType = elements.filterType ? elements.filterType.value : '';
        const sortValue = elements.sortBy ? elements.sortBy.value : 'default';

        const apiUrl = new URL('/api/search-spots', window.location.origin);
        if (keyword) apiUrl.searchParams.append('keyword', keyword);
        if (selectedType) apiUrl.searchParams.append('type', selectedType);
        if (sortValue !== 'default') apiUrl.searchParams.append('sort_by', sortValue);

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
              const data = await response.json();            if (data.success && Array.isArray(data.spots)) {
                state.allSpots = data.spots; // 存储所有数据
                state.currentDisplayCount = 0; // 重置显示计数
                
                // 显示前16个景区
                displayInitialSpots();
                updateResultsInfo(data.spots.length, keyword, selectedType);
                // updateLoadMoreButton 已在 displayInitialSpots 中调用
            } else {
                handleError('数据格式错误');
                displaySpots([]);
            }} catch (error) {
            console.error('Error fetching search results:', error);
            handleError('网络连接失败，请检查网络或稍后重试');
            resetPaginationState(); // 重置分页状态
            displaySpots([]);
        } finally {
            state.isLoading = false;
        }
    }    // ===== 显示初始景区 =====
    function displayInitialSpots() {
        const spotsToShow = state.allSpots.slice(0, state.itemsPerPage);
        state.displayedSpots = spotsToShow;
        state.currentDisplayCount = spotsToShow.length;
        
        displaySpots(spotsToShow);
        updateLoadMoreButton(); // 确保按钮状态正确更新
    }    // ===== 性能监控 =====
    function measureLoadTime(label, fn) {
        const startTime = performance.now();
        const result = fn();
        const endTime = performance.now();
        console.log(`${label}: ${endTime - startTime}ms`);
        return result;
    }

    // ===== 优化的加载更多景区（带性能监控）=====
    function loadMoreSpotsOptimized() {
        return measureLoadTime('LoadMore', () => {
            if (state.isLoading || state.currentDisplayCount >= state.allSpots.length) {
                return;
            }

            // 显示加载状态
            showLoadMoreLoading();

            // 立即获取下一批数据
            const nextBatch = state.allSpots.slice(
                state.currentDisplayCount, 
                state.currentDisplayCount + state.itemsPerPage
            );

            if (nextBatch.length > 0) {
                // 立即追加新的景区卡片到现有列表
                appendSpots(nextBatch);
                state.displayedSpots.push(...nextBatch);
                state.currentDisplayCount += nextBatch.length;
            }

            // 立即隐藏加载状态并更新按钮
            hideLoadMoreLoading();
            updateLoadMoreButton();
        });
    }

    // 覆盖原函数以使用优化版本
    // loadMoreSpots = loadMoreSpotsOptimized;

    // ===== 加载更多景区 =====
    function loadMoreSpots() {
        if (state.isLoading || state.currentDisplayCount >= state.allSpots.length) {
            return;
        }

        // 显示加载状态
        showLoadMoreLoading();

        // 立即获取下一批数据
        const nextBatch = state.allSpots.slice(
            state.currentDisplayCount, 
            state.currentDisplayCount + state.itemsPerPage
        );

        if (nextBatch.length > 0) {
            // 立即追加新的景区卡片到现有列表
            appendSpots(nextBatch);
            state.displayedSpots.push(...nextBatch);
            state.currentDisplayCount += nextBatch.length;
            
            // 异步加载新图片（不阻塞UI）
            loadSpotImages(nextBatch);
        }

        // 立即隐藏加载状态并更新按钮
        hideLoadMoreLoading();
        updateLoadMoreButton();
    }    // ===== 追加景区卡片 =====
    function appendSpots(spotsToAdd) {
        if (!elements.spotsList || !spotsToAdd || spotsToAdd.length === 0) return;

        // 先批量添加所有卡片到DOM
        const fragment = document.createDocumentFragment();
        const cards = [];

        spotsToAdd.forEach((spot, index) => {
            const li = createSpotCard(spot, state.currentDisplayCount + index);
            fragment.appendChild(li);
            cards.push(li);
        });

        // 一次性添加到DOM中
        elements.spotsList.appendChild(fragment);

        // 立即触发所有卡片的动画，提供最快的视觉反馈
        requestAnimationFrame(() => {
            cards.forEach(card => {
                card.classList.add('animate-in');
            });
        });

        // 重新设置观察器
        setupScrollEffects();
    }// ===== 更新加载更多按钮状态 =====
    function updateLoadMoreButton() {
        if (!elements.loadMoreContainer || !elements.loadMoreButton) return;

        const hasMore = state.currentDisplayCount < state.allSpots.length;
        
        if (state.allSpots.length === 0) {
            // 没有数据时隐藏按钮
            elements.loadMoreContainer.style.display = 'none';
        } else if (hasMore) {
            // 还有更多数据时显示按钮
            elements.loadMoreContainer.style.display = 'block';
            elements.loadMoreButton.disabled = false;
            
            const remaining = state.allSpots.length - state.currentDisplayCount;
            const nextBatchSize = Math.min(remaining, state.itemsPerPage);
            // 修复：显示当前已显示数量和总数量
            elements.loadMoreText.textContent = `显示更多景区 (${state.currentDisplayCount}/${state.allSpots.length})`;
        } else {
            // 没有更多数据时隐藏按钮或显示完成状态
            elements.loadMoreContainer.style.display = 'none';
            // 或者可以显示"已显示全部"的消息
            // elements.loadMoreText.textContent = '已显示全部景区';
            // elements.loadMoreButton.disabled = true;
        }
    }

    // ===== 显示加载状态 =====
    function showLoadingState() {
        if (elements.spotsList) {
            elements.spotsList.innerHTML = `
                <li class="loading-placeholder">
                    <div class="placeholder-content">
                        <div class="placeholder-spinner">
                            <i class="fas fa-compass fa-spin"></i>
                        </div>
                        <p>正在为您精心挑选景区...</p>
                    </div>
                </li>
            `;
        }
        
        if (elements.noResults) {
            elements.noResults.style.display = 'none';
        }
    }

    // ===== 显示加载更多的加载状态 =====
    function showLoadMoreLoading() {
        if (elements.loadMoreText) {
            elements.loadMoreText.textContent = '正在加载更多...';
        }
        if (elements.loadMoreSpinner) {
            elements.loadMoreSpinner.style.display = 'inline-block';
        }
        if (elements.loadMoreButton) {
            elements.loadMoreButton.disabled = true;
        }
        state.isLoading = true;
    }

    // ===== 隐藏加载更多的加载状态 =====
    function hideLoadMoreLoading() {
        if (elements.loadMoreSpinner) {
            elements.loadMoreSpinner.style.display = 'none';
        }
        if (elements.loadMoreButton) {
            elements.loadMoreButton.disabled = false;
        }
        state.isLoading = false;
    }    // ===== 加载景区图片 =====    // ===== 加载景区图片 =====
    async function loadSpotImages(spots) {
        // 暂时禁用图片加载功能以提升性能
        // 可以在后端实现 /api/spots/{id}/cover 接口后重新启用
        return;
        
        if (!spots || spots.length === 0) return;

        // 并发加载所有图片，提高速度
        const imagePromises = spots.map(async (spot) => {
            if (!spot.id) return;
            
            // 为每个卡片显示加载指示器
            showImageLoading(spot.id);
            
            try {
                const response = await fetch(`/api/spots/${spot.id}/cover`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.cover_url) {
                        // 更新对应卡片的图片
                        updateSpotCardImage(spot.id, data.cover_url);
                    } else {
                        // 图片加载失败，隐藏加载指示器
                        hideImageLoading(spot.id);
                    }
                } else {
                    hideImageLoading(spot.id);
                }
            } catch (error) {
                console.warn(`Failed to load cover for spot ${spot.id}:`, error);
                hideImageLoading(spot.id);
            }
        });

        // 等待所有图片加载完成（不阻塞UI）
        await Promise.allSettled(imagePromises);
    }

    // ===== 显示图片加载指示器 =====
    function showImageLoading(spotId) {
        const spotCard = document.querySelector(`[data-spot-id="${spotId}"]`);
        if (spotCard) {
            const placeholder = spotCard.querySelector('.spot-image-placeholder');
            if (placeholder) {
                placeholder.innerHTML = `
                    <div class="image-loading">
                        <i class="fas fa-spinner fa-spin"></i>
                        <span>加载中...</span>
                    </div>
                `;
                placeholder.style.opacity = '0.7';
            }
        }
    }

    // ===== 隐藏图片加载指示器 =====
    function hideImageLoading(spotId) {
        const spotCard = document.querySelector(`[data-spot-id="${spotId}"]`);
        if (spotCard) {
            const placeholder = spotCard.querySelector('.spot-image-placeholder');
            if (placeholder) {
                placeholder.innerHTML = '暂无图片';
                placeholder.style.opacity = '1';
            }
        }
    }    // ===== 更新景区卡片图片 =====
    function updateSpotCardImage(spotId, imageUrl) {
        const spotCard = document.querySelector(`[data-spot-id="${spotId}"]`);
        if (!spotCard) return;

        const img = spotCard.querySelector('img');
        const placeholder = spotCard.querySelector('.spot-image-placeholder');
        
        if (img) {
            // 如果已有图片元素，直接更新
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
            img.src = imageUrl;
            
            img.onload = () => {
                img.style.opacity = '1';
            };
            
            img.onerror = () => {
                img.style.opacity = '1';
            };
        } else if (placeholder) {
            // 创建新的图片元素
            const newImg = document.createElement('img');
            newImg.src = imageUrl;
            newImg.alt = `景区图片`;
            newImg.loading = 'lazy';
            newImg.style.opacity = '0';
            newImg.style.transition = 'opacity 0.3s ease';
            newImg.style.width = '100%';
            newImg.style.height = '100%';
            newImg.style.objectFit = 'cover';
            
            newImg.onload = () => {
                newImg.style.opacity = '1';
                // 图片加载成功后替换占位符
                if (placeholder.parentNode) {
                    placeholder.parentNode.replaceChild(newImg, placeholder);
                }
            };
            
            newImg.onerror = () => {
                // 图片加载失败，恢复占位符显示
                hideImageLoading(spotId);
            };
            
            // 预加载图片
            newImg.src = imageUrl;
        }
    }

    // ===== 显示结果信息 =====
    function updateResultsInfo(count, keyword, type) {
        if (elements.resultsTitle) {
            let title = '推荐景区';
            if (keyword || type) {
                title = '搜索结果';
                if (keyword) title += ` - "${keyword}"`;
                if (type) title += ` - ${type}`;
            }
            elements.resultsTitle.textContent = title;
        }

        if (elements.resultsCount) {
            elements.resultsCount.textContent = `找到 ${count} 个景区`;
        }
    }    // ===== 显示景区列表 =====
    function displaySpots(spotsToDisplay) {
        if (!elements.spotsList) return;
        
        elements.spotsList.innerHTML = '';
        
        if (elements.noResults) {
            elements.noResults.style.display = 'none';
        }

        if (!spotsToDisplay || spotsToDisplay.length === 0) {
            resetPaginationState(); // 重置分页状态
            showNoResults();
            return;
        }

        // 使用文档片段批量添加卡片
        const fragment = document.createDocumentFragment();
        const cards = [];

        spotsToDisplay.forEach((spot, index) => {
            const li = createSpotCard(spot, index);
            fragment.appendChild(li);
            cards.push(li);
        });

        // 一次性添加到DOM
        elements.spotsList.appendChild(fragment);

        // 立即触发所有卡片的动画
        requestAnimationFrame(() => {
            cards.forEach(card => {
                card.classList.add('animate-in');
            });
        });

        // 重新设置观察器
        setupScrollEffects();
    }// ===== 创建景区卡片 =====
    function createSpotCard(spot, index) {
        const li = document.createElement('li');
        li.classList.add('spot-card');
        li.setAttribute('data-spot-id', spot.id); // 添加 data-spot-id 属性
        // 移除 animationDelay 设置，避免累积延迟
        // li.style.animationDelay = `${index * 0.1}s`;

        const imgHtml = spot.img 
            ? `<img src="${spot.img}" alt="${spot.name || '景区图片'}" loading="lazy">` 
            : '<div class="spot-image-placeholder">暂无图片</div>';
        
        const name = spot.name || '未知景点';
        const scoreValue = (spot.value1 !== undefined && spot.value1 !== null) ? parseFloat(spot.value1).toFixed(1) : null;
        const scoreDisplay = scoreValue !== null ? `${scoreValue}分` : '暂无评分';
        const type = spot.type || '未知类型';
        const popularity = (spot.value2 !== undefined && spot.value2 !== null) ? parseInt(spot.value2) : 'N/A';

        li.innerHTML = `
            ${imgHtml}
            <div class="spot-info">
                <h3><a href="/spots/spot_info/${spot.id}" title="${name}">${name}</a></h3>
                <p><i class="fas fa-star"></i><span class="score">${scoreDisplay}</span></p>
                <p><i class="fas fa-fire"></i>热度: ${popularity}</p>
                <p><i class="fas fa-tag"></i>类型: <span class="type">${type}</span></p>
            </div>
        `;

        // 添加点击动画
        li.addEventListener('click', (e) => {
            if (!e.target.closest('a')) {
                li.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    li.style.transform = '';
                    window.location.href = `/spots/spot_info/${spot.id}`;
                }, 150);
            }
        });

        return li;
    }

    // ===== 显示无结果状态 =====
    function showNoResults() {
        if (elements.noResults) {
            elements.noResults.style.display = 'block';
            
            // 添加动画效果
            elements.noResults.style.opacity = '0';
            elements.noResults.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                elements.noResults.style.opacity = '1';
                elements.noResults.style.transform = 'translateY(0)';
            }, 100);
        }
    }    // ===== 错误处理 =====
    function handleError(message) {
        resetPaginationState(); // 重置分页状态
        
        if (elements.spotsList) {
            elements.spotsList.innerHTML = `
                <li class="loading-placeholder">
                    <div class="placeholder-content">
                        <div class="placeholder-spinner">
                            <i class="fas fa-exclamation-triangle" style="color: #ff6b6b;"></i>
                        </div>
                        <p style="color: #ff6b6b;">${message}</p>
                    </div>
                </li>
            `;
        }
    }    // ===== 头部搜索处理 =====
    function handleHeaderSearch() {
        if (!elements.headerSearchInput || !elements.headerSearchSelect) return;
        
        const keyword = elements.headerSearchInput.value.trim();
        
        // 移除错误样式
        elements.headerSearchInput.style.borderColor = '';
        
        if (!keyword) {
            // 空关键词提示
            elements.headerSearchInput.style.borderColor = 'red';
            elements.headerSearchInput.style.animation = 'shake 0.5s';
            setTimeout(() => {
                elements.headerSearchInput.style.borderColor = '#CCCCCC';
                elements.headerSearchInput.style.animation = '';
            }, 500);
            return;
        }

        const searchType = elements.headerSearchSelect.value;
        
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

    // ===== 登出处理 =====
    async function handleLogout() {
        try {
            // 添加加载动画
            if (elements.logoutButton) {
                elements.logoutButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 登出中...';
                elements.logoutButton.disabled = true;
            }
            
            await fetch('/api/logout', { method: 'POST' });
            
            // 添加淡出效果
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s';
            
            setTimeout(() => {
                window.location.href = '/login';
            }, 500);
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }

    // ===== 用户会话检查 =====
    async function checkUserSession() {
        try {
            const response = await fetch('/api/check-session');
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return;
            }
              const data = await response.json();
            if (data && data.success && data.user) {
                if (elements.username) {
                    elements.username.textContent = data.user.username || '用户';
                    
                    // 设置用户名链接到用户的日记页面
                    if (data.user.user_id) {
                        elements.username.href = `/diary/user/${data.user.user_id}`;
                    }
                    
                    // 添加欢迎动画
                    elements.username.style.opacity = '0';
                    setTimeout(() => {
                        elements.username.style.opacity = '1';
                    }, 500);
                }
            } else {
                console.error('Session check failed:', data ? data.message : 'No data');
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error checking session:', error);
            if (elements.username) {
                elements.username.textContent = '访客';
            }
        }
    }

    // ===== 键盘快捷键支持 =====
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K 聚焦搜索框
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (elements.searchKeyword) {
                elements.searchKeyword.focus();
            }
        }
        
        // ESC 清空搜索
        if (e.key === 'Escape') {
            if (elements.searchKeyword && elements.searchKeyword === document.activeElement) {
                elements.searchKeyword.blur();
            }
        }
    });

    // ===== 启动应用 =====
    init();

    // ===== 性能优化：图片懒加载 =====
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });

        // 为动态添加的图片设置观察器
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        const images = node.querySelectorAll('img[data-src]');
                        images.forEach(img => imageObserver.observe(img));
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }
});
