document.addEventListener('DOMContentLoaded', () => {
    const usernameSpan = document.getElementById('username');
    const logoutButton = document.getElementById('logout-button');
    const searchBar = document.querySelector('.search-bar');
    const searchSelect = searchBar.querySelector('select');
    const searchInput = searchBar.querySelector('input');
    const searchButton = searchBar.querySelector('.search-button');
    
    // 选项卡切换功能
    const tabs = document.querySelectorAll('.tab-item');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            
            // 移除所有激活状态
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // 设置当前选中项为激活状态
            tab.classList.add('active');
            
            // 获取对应内容并显示
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
            
            // 如果对应内容为空，则加载数据
            const gridElement = document.getElementById(`${targetId}-grid`);
            if (gridElement && gridElement.children.length === 0) {
                loadTabContent(targetId);
            }
        });
    });
    
    // 按评分加载不同类别的景区
    function loadTabContent(tabId) {
        const gridElement = document.getElementById(`${tabId}-grid`);
        if (!gridElement) return;
        
        // 显示加载中
        gridElement.innerHTML = '<div class="spot-card"><div style="height: 150px; background: #eee; display: flex; align-items: center; justify-content: center; color: #aaa;">加载中...</div></div>';
        
        // 构建API请求
        let apiUrl = '/api/search-spots';
        let params = new URLSearchParams();
        
        // 根据tabId设置不同的筛选条件
        switch(tabId) {
            case 'recommended':
                // 推荐景区：显示带有用户注册时选择的喜好标签的景区（刨去spot_type为"演出"）
                params.append('exclude_type', '演出');
                params.append('user_preference', 'true');
                break;
            case '5star':
                // 5分景区：只显示spot.score为5.0的景区（刨去spot_type为"演出"）
                params.append('min_score', '5.0');
                params.append('max_score', '5.0');
                params.append('exclude_type', '演出');
                break;
            case '4star':
                // 4分景区：只显示spot.score为4.0~4.9的景区（刨去spot_type为"演出"）
                params.append('min_score', '4.0');
                params.append('max_score', '4.9');
                params.append('exclude_type', '演出');
                break;
            case '3star':
                // 3分景区：只显示spot.score为3.0~3.9的景区（刨去spot_type为"演出"）
                params.append('min_score', '3.0');
                params.append('max_score', '3.9');
                params.append('exclude_type', '演出');
                break;
            case 'shows':
                // 旅游演艺：只显示spot_type为"演出"的
                params.append('type', '演出');
                break;
        }
        
        // 发送请求
        fetch(`${apiUrl}?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && Array.isArray(data.spots) && data.spots.length > 0) {
                    // 清空网格
                    gridElement.innerHTML = '';
                    
                    // 限制最多显示10个景区
                    const spotsToShow = data.spots.slice(0, 10);
                    
                    // 添加景区卡片
                    spotsToShow.forEach(spot => {
                        const spotCard = createSpotCard(spot);
                        gridElement.appendChild(spotCard);
                    });
                } else {
                    gridElement.innerHTML = '<div class="spot-card"><div style="height: 150px; display: flex; align-items: center; justify-content: center; color: #888;">暂无数据</div></div>';
                }
                
                // 确保"查看更多"按钮可见（无论是否有数据）
                const viewMoreBtn = document.getElementById(tabId).querySelector('.view-more');
                if (viewMoreBtn) {
                    viewMoreBtn.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('加载景区数据出错:', error);
                gridElement.innerHTML = '<div class="spot-card"><div style="height: 150px; display: flex; align-items: center; justify-content: center; color: #888;">加载出错，请重试</div></div>';
                
                // 确保"查看更多"按钮可见（即使出错）
                const viewMoreBtn = document.getElementById(tabId).querySelector('.view-more');
                if (viewMoreBtn) {
                    viewMoreBtn.style.display = 'block';
                }
            });
    }
    
    // 创建景区卡片元素
    function createSpotCard(spot) {
        const card = document.createElement('div');
        card.className = 'spot-card';
        
        const id = spot.id || '';
        const name = spot.name || '未知景点';
        const imgUrl = spot.img || '';
        const score = spot.value1 || 'N/A';
        // 提取地址信息 - 假设info是一个数组，里面包含地址字段
        let location = '未知地区';
        if (spot.info && Array.isArray(spot.info)) {
            const addressObj = spot.info.find(item => Object.keys(item)[0] === '地址');
            if (addressObj && addressObj['地址']) {
                // 提取地址中的省市信息 (简化处理)
                const addressText = addressObj['地址'];
                const provinceMatch = addressText.match(/([^省]+省|北京|上海|天津|重庆|江苏|浙江|安徽|福建)/);
                const cityMatch = addressText.match(/([^市]+市|[^州]+州|[^县]+县|[^区]+区)/);
                
                // 避免重复地点名称，如"四川 四川"
                if (provinceMatch && cityMatch) {
                    const province = provinceMatch[0].substring(0, 2);
                    const city = cityMatch[0].substring(0, 2);
                    
                    if (province === city) {
                        location = province;
                    } else {
                        location = `${province} ${city}`;
                    }
                } else if (provinceMatch) {
                    location = provinceMatch[0].substring(0, 2);
                } else if (cityMatch) {
                    location = cityMatch[0].substring(0, 2);
                }
            }
        }
        
        card.innerHTML = `
            ${imgUrl ? `<img src="${imgUrl}" alt="${name}">` : '<div style="height: 130px; background: #eee; display: flex; align-items: center; justify-content: center; color: #aaa;">无图片</div>'}
            <div class="spot-card-info">
                <h3><a href="/spots/spot_info/${id}" style="text-decoration: none; color: inherit;">${name}</a></h3>
                <span class="spot-location">[${location} ${score}分]</span>
                <div style="clear: both;"></div>
            </div>
        `;
        
        return card;
    }

    // 1. 检查会话并获取用户信息
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
        })        .then(data => {
            if (data && data.success) {
                usernameSpan.textContent = data.user.username || '用户';
                // 设置用户名链接到用户的日记页面
                if (data.user.user_id) {
                    usernameSpan.href = `/diary/user/${data.user.user_id}`;
                }
                // 用户信息获取成功后，获取推荐景点
                loadTabContent('recommended');
            } else if (data) {
                 // 即使成功响应，也可能业务逻辑失败
                 console.error('会话检查失败:', data.message);
                 window.location.href = '/login';
            }
            // 如果 response.ok 为 false 且非 401，则不会执行到这里
        })
        .catch(error => {
            console.error('检查会话时出错:', error);
            usernameSpan.textContent = '错误';
            // 可选：也在此处重定向到登录页
            window.location.href = '/login';
        });

    // 2. 获取推荐景点函数
    function fetchAndDisplaySpots() {
        fetch('/api/recommended-spots') // 请求新的推荐 API
            .then(response => {
                if (!response.ok) {
                     // 如果未授权，也重定向
                    if (response.status === 401) {
                        window.location.href = '/login';
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                spotsList.innerHTML = ''; // 清空加载提示
                if (data.success && data.spots && data.spots.length > 0) {
                    data.spots.forEach(spot => {
                        const li = document.createElement('li');
                        // 安全地获取每个字段，提供默认值
                        const id = spot.id || '未知ID';
                        const name = spot.name || '未知景点';
                        const score = spot.value1 !== undefined ? spot.value1 : 'N/A'; // 评分可能是 0
                        const type = spot.type || '未知类型';
                        const visitedTime = spot.value2 || '未知'; // 假设 visited_time 是一个字符串描述，如 "约2小时"
                        const imgUrl = spot.img || ''; // 图片 URL，如果没有则为空

                        // 构建列表项的 HTML 内容
                        li.innerHTML = `
                            ${imgUrl ? `<img src="${imgUrl}" alt="${name}" style="max-width: 100px; max-height: 80px; float: left; margin-right: 10px;">` : ''}
                            <h3><a href="/spots/spot_info/${id}">${name}</a></h3> <!-- 修改这里，将名字变为链接 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; font-family: serif; font-size: 0.9rem; line-height: 1.6; color: #636e72;">
                                <div>ID: ${id}</div>
                                <div>标签: ${type}</div>
                                <div>评分: ${score}</div>
                                <div>浏览: ${visitedTime}</div>
                            </div>
                            <div style="clear: both;"></div> <!-- 清除浮动 -->
                        `;
                        spotsList.appendChild(li);
                    });
                } else if (data.success) {
                    spotsList.innerHTML = '<li>暂无推荐景点。</li>';
                } else {
                    spotsList.innerHTML = `<li>加载推荐景点失败: ${data.message || '未知错误'}</li>`;
                }
            })
            .catch(error => {
                console.error('获取推荐景点时出错:', error);
                spotsList.innerHTML = '<li>加载推荐景点时出错，请稍后重试。</li>';
            });
    }

    // 3. 处理搜索
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
        
        const searchType = searchSelect.value;
        const apiUrl = new URL('/api/search-spots', window.location.origin);
        apiUrl.searchParams.append('keyword', keyword);
        if (searchType === 'diary') {
            apiUrl.searchParams.append('type', 'diary');
        }
        
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
    
    function showToast(message) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.backgroundColor = 'rgba(0,0,0,0.7)';
        toast.style.color = 'white';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '1000';
        document.body.appendChild(toast);        setTimeout(() => {
            toast.remove();
        }, 1500);
    }
    
    searchButton.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // 4. 处理登出
    logoutButton.addEventListener('click', () => {
        fetch('/api/logout', { method: 'POST' }) // 最好使用 POST 请求登出
            .then(response => {
                // 不论成功与否，都尝试重定向到登录页
                window.location.href = '/login'; // 假设登出 API 会处理重定向，或者前端强制跳转
            })
            .catch(error => {
                console.error('登出时出错:', error);
                // 即使出错，也尝试跳转
                window.location.href = '/login';
            });
    });

    // 初始加载推荐景区数据
    loadTabContent('recommended');
    
    let currentDiaryCount = 8; // 当前已加载的日记数量
    const diariesPerLoad = 8; // 每次加载的日记数量

    // 加载推荐日记
    loadRecommendedDiaries(currentDiaryCount);    // "查看更多日记"按钮事件监听
    const viewMoreDiariesButton = document.getElementById('view-more-diaries-btn');
    if (viewMoreDiariesButton) {
        viewMoreDiariesButton.addEventListener('click', () => {
            // 防止重复点击
            if (viewMoreDiariesButton.disabled) return;
            
            // 显示加载中状态
            viewMoreDiariesButton.disabled = true;
            viewMoreDiariesButton.textContent = '加载中...';
            
            // 增加请求数量
            currentDiaryCount += diariesPerLoad;
            console.log(`当前请求数量增加到: ${currentDiaryCount} 条`);
            loadRecommendedDiaries(currentDiaryCount, true); // true 表示是追加加载
        });
    }
});

// 加载推荐日记功能
function loadRecommendedDiaries(topK, append = false) {
    const diaryGrid = document.getElementById('diary-grid');
    if (!diaryGrid) return;
    
    const viewMoreDiariesButton = document.getElementById('view-more-diaries-btn');

    if (!append) {
        // 初始加载时显示加载中
        diaryGrid.innerHTML = '<div class="diary-card"><div style="height: 200px; background: #eee; display: flex; align-items: center; justify-content: center; color: #aaa;">加载中...</div></div>';
    } else {
        // 追加加载时，可以显示一个小的加载提示或禁用按钮
        if(viewMoreDiariesButton) viewMoreDiariesButton.disabled = true;
        const loadingMoreIndicator = document.createElement('div');
        loadingMoreIndicator.className = 'loading-more-indicator';
        loadingMoreIndicator.innerHTML = '<div style="text-align: center; padding: 10px; color: #aaa;">正在加载更多日记...</div>';
        diaryGrid.appendChild(loadingMoreIndicator);
    }

    // 获取当前用户信息
    fetch('/api/check-session')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(userData => {
            if (userData.success && userData.user && userData.user.user_id) {
                const userId = userData.user.user_id;
                // 获取推荐日记
                return fetch(`/diary/recommend/user/${userId}?topK=${topK}`);
            } else {
                throw new Error('无法获取用户信息');
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(diaries => {            // 移除加载更多提示
            const loadingMoreIndicator = diaryGrid.querySelector('.loading-more-indicator');
            if (loadingMoreIndicator) {
                loadingMoreIndicator.remove();
            }
            // 恢复按钮状态 - 但只有在确定有更多日记的情况下才恢复
            if(viewMoreDiariesButton && !append) {
                viewMoreDiariesButton.disabled = false;
                viewMoreDiariesButton.textContent = '查看更多日记';
            } else if (viewMoreDiariesButton && append) {
                // 追加加载时，需要等判断是否有更多日记后再设置状态
                // 先恢复默认文本
                if (diaries.length >= topK) {
                    viewMoreDiariesButton.textContent = '查看更多日记';
                    viewMoreDiariesButton.disabled = false;
                }
            }

            if (!append) {
                diaryGrid.innerHTML = ''; // 初始加载时清空
            }            if (Array.isArray(diaries) && diaries.length > 0) {
                let diariesToShow;
                if (append) {
                    // 追加加载时，只添加新的日记
                    // API 返回的是全量前 topK 条数据，我们需要筛选出尚未显示的新增日记
                    const existingDiaryIds = Array.from(diaryGrid.querySelectorAll('.diary-card')).map(card => card.dataset.diaryId);
                    diariesToShow = diaries.filter(diary => !existingDiaryIds.includes(String(diary.id)));
                    console.log(`获取到 ${diaries.length} 条日记，其中新增 ${diariesToShow.length} 条`);
                } else {
                    diariesToShow = diaries;
                }                if (diariesToShow.length > 0) {
                    diariesToShow.forEach(diary => {
                        const diaryCard = createDiaryCard(diary);
                        // 无需在这里设置dataset属性，已在createDiaryCard中设置
                        diaryGrid.appendChild(diaryCard);
                    });
                    
                    // 检查是否还有更多日记可以加载
                    // 如果当前返回的日记总数小于请求的topK，说明服务器没有更多日记了
                    if (diaries.length < topK && viewMoreDiariesButton) {
                        viewMoreDiariesButton.textContent = '没有更多日记了';
                        viewMoreDiariesButton.disabled = true;
                        console.log(`服务器返回 ${diaries.length} 条，少于请求的 ${topK} 条，无更多日记`);
                    } else {
                        console.log(`服务器返回 ${diaries.length} 条，请求了 ${topK} 条，可能还有更多日记`);
                    }
                } else if (append) {
                    // 追加加载时，如果没有新增日记，也表示没有更多了
                    if(viewMoreDiariesButton) {
                        viewMoreDiariesButton.textContent = '没有更多日记了';
                        viewMoreDiariesButton.disabled = true;
                        console.log('无新增日记，已加载全部');
                    }
                }

            } else if (!append) {
                // 初始加载且没有日记
                diaryGrid.innerHTML = `
                    <div class="diary-card">
                        <div style="height: 200px; background: #f5f5f5; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #999;">
                            <div style="font-size: 24px; margin-bottom: 8px;">📝</div>
                            <div>暂无推荐日记</div>
                            <div style="font-size: 12px; margin-top: 4px;">去发现更多精彩内容吧</div>
                        </div>
                    </div>
                `;
                if(viewMoreDiariesButton) {
                    viewMoreDiariesButton.style.display = 'none'; // 如果初始就没有日记，隐藏按钮
                }
            } else {
                 // 追加加载时，如果没有更多日记
                if(viewMoreDiariesButton) {
                    viewMoreDiariesButton.textContent = '没有更多日记了';
                    viewMoreDiariesButton.disabled = true;
                }
            }
        })        .catch(error => {
            console.error('加载推荐日记时出错:', error);
            const loadingMoreIndicator = diaryGrid.querySelector('.loading-more-indicator');
            if (loadingMoreIndicator) {
                loadingMoreIndicator.remove();
            }
            
            // 恢复按钮状态
            if(viewMoreDiariesButton) {
                viewMoreDiariesButton.disabled = false;
                viewMoreDiariesButton.textContent = '查看更多日记';
            }

            if (!append) {
                // 首次加载失败时，显示错误信息
                diaryGrid.innerHTML = `
                    <div class="diary-card">
                        <div style="height: 200px; background: #ffebee; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #f44336;">
                            <div style="font-size: 24px; margin-bottom: 8px;">⚠️</div>
                            <div>加载失败</div>
                            <div style="font-size: 12px; margin-top: 4px;">请稍后重试</div>
                        </div>
                    </div>
                `;
            } else {
                // 追加加载失败时，显示提示
                const errorMsg = document.createElement('div');
                errorMsg.className = 'load-more-error';
                errorMsg.innerHTML = `<div style="text-align: center; padding: 10px; color: #f44336;">加载更多日记失败，请重试</div>`;
                
                // 移除之前可能存在的错误信息
                const oldErrorMsg = diaryGrid.querySelector('.load-more-error');
                if (oldErrorMsg) {
                    oldErrorMsg.remove();
                }
                
                diaryGrid.appendChild(errorMsg);
                
                // 3秒后自动移除错误提示
                setTimeout(() => {
                    const currentErrorMsg = diaryGrid.querySelector('.load-more-error');
                    if (currentErrorMsg) {
                        currentErrorMsg.remove();
                    }
                }, 3000);
            }
        });
}

// 创建日记卡片
function createDiaryCard(diary) {
    const card = document.createElement('div');
    card.className = 'diary-card';
    card.dataset.diaryId = diary.id; // 设置日记ID为数据属性
    card.onclick = () => window.location.href = `/diary/${diary.id}`;
    
    // 处理图片
    let imageUrl = '';
    if (diary.img_list && diary.img_list.length > 0) {
        imageUrl = diary.img_list[0];
    }
    
    // 处理内容预览
    let content = '';
    if (diary.content) {
        // 移除HTML标签，只保留文本
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = diary.content;
        content = tempDiv.textContent || tempDiv.innerText || '';
    }
    
    // 处理评分显示
    const score = diary.score || 0;
    const scoreDisplay = score > 0 ? score.toFixed(1) : '暂无';
    
    // 处理时间显示
    let timeDisplay = '未知时间';
    if (diary.time) {
        try {
            const date = new Date(diary.time);
            timeDisplay = date.toLocaleDateString('zh-CN');
        } catch (e) {
            timeDisplay = diary.time;
        }
    }
    
    // 如果 imageUrl 是相对路径，则补全为绝对路径
    let displayImageUrl = imageUrl;
    if (imageUrl && !/^https?:\/\//i.test(imageUrl)) {
        displayImageUrl = window.location.origin + (imageUrl.startsWith('/') ? imageUrl : '/' + imageUrl);
    }

    card.innerHTML = `
        <div class="diary-card-image" ${displayImageUrl ? `style="background-image: url('${displayImageUrl}')"` : ''}>
            ${!displayImageUrl ? '<div>📝</div>' : ''}
        </div>
        <div class="diary-card-content">
            <h3 class="diary-card-title" title="${diary.title || '无标题'}">${diary.title || '无标题'}</h3>
            <div class="diary-card-meta">
                <span class="diary-card-author">${diary.user_name || '匿名用户'}</span>
                <span class="diary-card-spot-name">📍 ${diary.spot_name || '未知景点'}</span> 
            </div>
            <div class="diary-card-preview">${content || '暂无内容预览'}</div>
            <div class="diary-card-stats">
                <span>📅 ${timeDisplay}</span>
                <span>⭐ ${scoreDisplay}分</span>
                <span>👁️ ${diary.visited_time || 0}次访问</span>
            </div>
        </div>
    `;
    
    return card;
}
