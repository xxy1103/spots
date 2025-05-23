/**
 * 地图应用主脚本文件
 * 负责地图显示、POI查询、路线规划等功能
 */

// 等待文档加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化全局变量
    const MapApp = {
        // 地图图层
        poiLayer: L.layerGroup().addTo(map),
        scenicSpotLayer: L.layerGroup().addTo(map),
        routeMarkersLayer: L.layerGroup().addTo(map), // 新增：路线点标记图层
        
        // 数据存储
        currentPois: [],
        routePoints: [],
        routeMarkers: {}, // 新增：存储路线点标记的对象，键为"lat,lng"格式
        currentRouteLayer: null,
        currentLocationStringForPoiSearch: null,
        
        /**
         * 初始化应用
         */
        init: function() {
            this.bindEvents();
            this.loadScenicSpots();
        },
        
        /**
         * 绑定事件处理函数
         */
        bindEvents: function() {
            // 标签切换事件
            document.querySelectorAll('.tab-button').forEach(button => {
                button.addEventListener('click', function() {
                    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                    this.classList.add('active');
                    const tabId = this.getAttribute('data-tab');
                    document.getElementById(tabId).classList.add('active');
                });
            });
            
            // POI搜索按钮事件
            document.getElementById('poi-search-button').addEventListener('click', () => {
                this.handlePoiSearch();
            });
            
            // POI搜索输入框回车事件
            document.getElementById('poi-search-keyword').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handlePoiSearch();
                }
            });
            
            // 监听地图弹窗打开事件
            map.on('popupopen', (e) => {
                this.handlePopupOpen(e);
            });
            
            // 清除路线按钮事件
            const clearRouteBtn = document.getElementById('clear-route-btn');
            if (clearRouteBtn) {
                clearRouteBtn.addEventListener('click', () => {
                    if (confirm('确定要清除当前路线和所有路线点吗？')) {
                        this.clearRoutePoints();
                    }
                });
            }
            
            // 导出路线按钮事件
            const exportRouteBtn = document.getElementById('export-route-btn');
            if (exportRouteBtn) {
                exportRouteBtn.addEventListener('click', () => {
                    this.exportRouteInfo();
                });
            }
            
            // 窗口大小改变时更新地图大小
            window.addEventListener('resize', function() {
                map.invalidateSize();
            });
        },
        
        /**
         * 处理POI搜索
         */
        handlePoiSearch: function() {
            if (!this.currentLocationStringForPoiSearch) {
                alert('请先点击一个地图上的蓝色景点标记以确定搜索中心。');
                return;
            }
            const keyword = document.getElementById('poi-search-keyword').value.trim();
            if (!keyword) {
                this.fetchPOIs(this.currentLocationStringForPoiSearch);
            } else {
                this.fetchPOIsByKeyword(this.currentLocationStringForPoiSearch, keyword);
            }
        },
        
        /**
         * 处理弹窗打开
         */
        handlePopupOpen: function(e) {
            const popupNode = e.popup.getElement();
            const addButton = popupNode.querySelector('.add-to-route-btn');
            if (addButton) {
                const newButton = addButton.cloneNode(true);
                addButton.parentNode.replaceChild(newButton, addButton);
                newButton.addEventListener('click', () => {
                    const name = newButton.dataset.name;
                    const lat = parseFloat(newButton.dataset.lat);
                    const lng = parseFloat(newButton.dataset.lng);
                    if (name && !isNaN(lat) && !isNaN(lng)) {
                        this.addPointToRoute({ name, lat, lng });
                    } else {
                        console.error("无法从按钮获取地点数据:", newButton.dataset);
                    }
                });
            }
        },
        
        /**
         * 加载景点数据
         */
        loadScenicSpots: function() {
            const spotId = window.spotId; // 在HTML中设置的全局变量
            if (spotId) {
                this.showLoading('正在加载景点信息...');
                fetch(`/map/${spotId}/api/scenicSpots`)
                    .then(response => {
                        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        console.log("加载景点数据:", data);
                        this.displayScenicSpots(data);
                    })
                    .catch(error => {
                        console.error('加载景点失败:', error);
                        this.showError('加载景点信息失败: ' + error.message);
                    });
            } else {
                this.showError('无法加载景点信息，缺少景点ID。');
            }
        },
        
        /**
         * 显示景点标记
         */
        displayScenicSpots: function(spots) {
            this.scenicSpotLayer.clearLayers();
            if (Array.isArray(spots) && spots.length > 0) {
                const bounds = [];
                spots.forEach(spot => {
                    if (spot.location && typeof spot.location.lat === 'number' && typeof spot.location.lng === 'number') {
                        const lat = spot.location.lat;
                        const lng = spot.location.lng;
                        if (!isNaN(lat) && !isNaN(lng)) {
                            // 创建标记
                            const marker = L.marker([lat, lng], {
                                icon: L.icon({
                                    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
                                    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
                                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                                    iconSize: [25, 41],
                                    iconAnchor: [12, 41],
                                    popupAnchor: [1, -34],
                                    shadowSize: [41, 41],
                                })
                            }).addTo(this.scenicSpotLayer);
                            
                            // 创建弹窗内容
                            const popupContent = `
                                <div class="popup-content">
                                    <h4>${spot.name}</h4>
                                    <p>${spot.address || '无地址信息'}</p>
                                    <button class="btn add-to-route-btn" data-name="${spot.name}" data-lat="${lat}" data-lng="${lng}">
                                        <i class="fas fa-plus-circle"></i> 添加到路线
                                    </button>
                                </div>
                            `;
                            marker.bindPopup(popupContent);
                            marker.spotData = spot;
                            
                            // 添加点击事件
                            marker.on('click', () => {
                                const clickedLatLng = marker.getLatLng();
                                const locationString = `${clickedLatLng.lat},${clickedLatLng.lng}`;
                                
                                // 更新信息面板
                                document.getElementById('spot-details').innerHTML = `
                                    <h4>${spot.name}</h4>
                                    <p><i class="fas fa-map-marker-alt"></i> ${spot.address || '无地址信息'}</p>
                                    <p><i class="fas fa-map-pin"></i> 坐标: ${clickedLatLng.lat.toFixed(6)}, ${clickedLatLng.lng.toFixed(6)}</p>
                                `;
                                
                                // 加载POI数据
                                this.showLoading('正在加载周边POI...');
                                document.querySelector('.tab-button[data-tab="poi-list"]').click();
                                document.getElementById('poi-ul').innerHTML = '<li class="loading-indicator"><i class="fas fa-spinner fa-spin"></i> 正在加载...</li>';
                                
                                this.currentLocationStringForPoiSearch = locationString;
                                this.fetchPOIs(locationString);
                            });
                            
                            bounds.push([lat, lng]);
                        }
                    }
                });
                
                // 调整地图视图
                if (bounds.length > 0) {
                    map.fitBounds(bounds, { padding: [50, 50] });
                }
                
                this.showMessage(`已加载 ${spots.length} 个景点`);
            } else {
                this.showError('未找到景点数据');
            }
        },
        
        /**
         * 获取POI信息
         */
        fetchPOIs: function(locationString) {
            this.poiLayer.clearLayers();
            this.currentPois = [];
            document.getElementById('poi-ul').innerHTML = '<li class="loading-indicator"><i class="fas fa-spinner fa-spin"></i> 正在加载POI...</li>';
            
            fetch(`/map/api/poi/${locationString}`)
                .then(response => {
                    if (!response.ok) {
                        return response.json()
                            .then(errData => { throw new Error(errData.message || `HTTP error! status: ${response.status}`); })
                            .catch(() => { throw new Error(`HTTP error! status: ${response.status}`); });
                    }
                    return response.json();
                })
                .then(pois => {
                    console.log("获取POI数据:", pois);
                    this.displayPOIs(pois, "周边");
                })
                .catch(error => {
                    console.error('获取POI失败:', error);
                    this.showError('加载POI失败: ' + error.message);
                });
        },
        
        /**
         * 按关键词搜索POI
         */
        fetchPOIsByKeyword: function(locationString, keyword) {
            this.poiLayer.clearLayers();
            this.currentPois = [];
            document.getElementById('poi-ul').innerHTML = `<li class="loading-indicator"><i class="fas fa-spinner fa-spin"></i> 正在搜索 "${keyword}"...</li>`;
            
            const encodedKeyword = encodeURIComponent(keyword);
            fetch(`/map/api/poi/${locationString}/${encodedKeyword}`)
                .then(response => {
                    if (!response.ok) {
                        return response.json()
                            .then(errData => { throw new Error(errData.message || `HTTP error! status: ${response.status}`); })
                            .catch(() => { throw new Error(`HTTP error! status: ${response.status}`); });
                    }
                    return response.json();
                })
                .then(pois => {
                    console.log(`获取关键词 "${keyword}" 的POI:`, pois);
                    this.displayPOIs(pois, `关于 "${keyword}" 的`);
                })
                .catch(error => {
                    console.error('搜索POI失败:', error);
                    this.showError('搜索POI失败: ' + error.message);
                });
        },
        
        /**
         * 显示POI数据
         */
        displayPOIs: function(pois, sourceDescription = "周边") {
            this.poiLayer.clearLayers();
            const poiListUl = document.getElementById('poi-ul');
            poiListUl.innerHTML = '';
            this.currentPois = [];
            
            if (Array.isArray(pois) && pois.length > 0) {
                this.currentPois = pois;
                pois.forEach((poi, index) => {
                    if (poi.location && typeof poi.location.lat === 'number' && typeof poi.location.lng === 'number') {
                        const lat = poi.location.lat;
                        const lng = poi.location.lng;
                        if (!isNaN(lat) && !isNaN(lng)) {
                            // 创建POI标记
                            const poiMarker = L.marker([lat, lng], {
                                icon: L.icon({
                                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                                    iconSize: [25, 41],
                                    iconAnchor: [12, 41],
                                    popupAnchor: [1, -34],
                                    shadowSize: [41, 41]
                                })
                            }).addTo(this.poiLayer);
                            
                            // 弹窗内容
                            const popupContent = `
                                <div class="popup-content">
                                    <h4>${poi.name}</h4>
                                    <p>${poi.address || '无地址信息'}</p>
                                    <p>距离: ${poi.value1 ? poi.value1 + '米' : '未知'}</p>
                                    <button class="btn add-to-route-btn" data-name="${poi.name}" data-lat="${lat}" data-lng="${lng}">
                                        <i class="fas fa-plus-circle"></i> 添加到路线
                                    </button>
                                </div>
                            `;
                            poiMarker.bindPopup(popupContent);
                            poiMarker.poiData = poi;
                            
                            // 点击事件
                            poiMarker.on('click', () => {
                                this.updatePoiDetails(poi);
                            });
                            
                            // 创建列表项
                            const li = document.createElement('li');
                            li.className = 'poi-item';
                            const poiId = poi.id || `poi-${index}`;
                            
                            li.innerHTML = `
                                <span>${poi.name}</span>
                                <span class="distance-badge">${poi.value1 ? poi.value1 + '米' : '未知'}</span>
                            `;
                            
                            li.dataset.poiId = poiId;
                            li.addEventListener('click', () => {
                                const targetPoi = this.currentPois.find(p => (p.id || `poi-${this.currentPois.indexOf(p)}`) === poiId);
                                
                                let targetMarker = null;
                                this.poiLayer.eachLayer(layer => {
                                    const layerPoiId = layer.poiData.id || `poi-${this.currentPois.indexOf(layer.poiData)}`;
                                    if (layer.poiData && layerPoiId === poiId) {
                                        targetMarker = layer;
                                    }
                                });
                                
                                if (targetPoi && targetPoi.location && targetMarker) {
                                    const targetLatLng = [targetPoi.location.lat, targetPoi.location.lng];
                                    map.setView(targetLatLng, 17);
                                    targetMarker.openPopup();
                                    this.updatePoiDetails(targetPoi);
                                }
                            });
                            
                            poiListUl.appendChild(li);
                        }
                    }
                });
                
                this.showMessage(`已加载 ${pois.length} 个${sourceDescription}POI。点击标记或列表项查看详情。`);
            } else {
                poiListUl.innerHTML = `<li class="no-data">未找到${sourceDescription}POI。</li>`;
                this.showMessage(`未找到${sourceDescription}POI。`);
            }
        },
        
        /**
         * 更新POI详情
         */
        updatePoiDetails: function(poi) {
            document.getElementById('details-content').innerHTML = `
                <div class="poi-detail">
                    <h4>${poi.name}</h4>
                    <p><i class="fas fa-map-marker-alt"></i> ${poi.address || '无地址信息'}</p>
                    <p><i class="fas fa-tag"></i> 类型: ${poi.type || '未知'}</p>
                    <p><i class="fas fa-ruler"></i> 距离中心点: ${poi.value1 ? poi.value1 + '米' : '未知'}</p>
                    <p><i class="fas fa-map-pin"></i> 坐标: ${poi.location.lat.toFixed(6)}, ${poi.location.lng.toFixed(6)}</p>
                </div>
            `;
        },
        
        /**
         * 添加点到路线
         */
        addPointToRoute: function(point) {
            const pointKey = `${point.lat},${point.lng}`;
            const exists = this.routePoints.some(p => p.lat === point.lat && p.lng === point.lng);
            
            if (!exists) {
                // 添加到路线点数组
                this.routePoints.push(point);
                
                // 在地图上创建固定标记
                const routeMarker = L.marker([point.lat, point.lng], {
                    icon: L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                    })
                }).addTo(this.routeMarkersLayer);
                
                // 设置弹出窗口
                const popupContent = `
                    <div class="popup-content">
                        <h4>${point.name}</h4>
                        <p><i class="fas fa-map-pin"></i> 路线点 #${this.routePoints.length}</p>
                        <button class="btn btn-danger remove-route-point-btn" data-index="${this.routePoints.length - 1}">
                            <i class="fas fa-trash-alt"></i> 从路线中移除
                        </button>
                    </div>
                `;
                routeMarker.bindPopup(popupContent);
                
                // 存储标记到路线标记对象
                this.routeMarkers[pointKey] = routeMarker;
                
                // 添加点击事件处理弹窗中的删除按钮
                routeMarker.on('popupopen', (e) => {
                    const popup = e.popup;
                    const container = popup.getElement();
                    const removeBtn = container.querySelector('.remove-route-point-btn');
                    
                    if (removeBtn) {
                        const newBtn = removeBtn.cloneNode(true);
                        removeBtn.parentNode.replaceChild(newBtn, removeBtn);
                        
                        newBtn.addEventListener('click', () => {
                            const index = parseInt(newBtn.dataset.index);
                            if (!isNaN(index)) {
                                this.removePointFromRoute(index);
                                popup.close();
                            }
                        });
                    }
                });
                
                // 更新路线列表显示
                this.updateRouteListDisplay();
                this.showMessage(`"${point.name}" 已添加到路线规划列表！`);
            } else {
                // 如果已存在，只是显示消息
                this.showMessage(`"${point.name}" 已在列表中。`, 'warning');
                
                // 找到对应的标记并显示弹窗
                if (this.routeMarkers[pointKey]) {
                    this.routeMarkers[pointKey].openPopup();
                }
            }
        },
        
        /**
         * 从路线中移除点
         */
        removePointFromRoute: function(index) {
            if (index >= 0 && index < this.routePoints.length) {
                const removed = this.routePoints[index];
                const pointKey = `${removed.lat},${removed.lng}`;
                
                // 移除对应的地图标记
                if (this.routeMarkers[pointKey]) {
                    this.routeMarkersLayer.removeLayer(this.routeMarkers[pointKey]);
                    delete this.routeMarkers[pointKey];
                }
                
                // 从数组中移除点
                this.routePoints.splice(index, 1);
                
                // 更新剩余标记的索引
                this.updateRouteMarkerIndices();
                
                // 更新路线列表显示
                this.updateRouteListDisplay();
                this.showMessage(`已从路线中移除 "${removed.name}"`);
            }
        },
        
        /**
         * 清除所有路线点
         */
        clearRoutePoints: function() {
            // 清空数组
            this.routePoints = [];
            
            // 清除地图上的路线点标记
            this.routeMarkersLayer.clearLayers();
            this.routeMarkers = {};
            
            // 清除路线
            if (this.currentRouteLayer) {
                map.removeLayer(this.currentRouteLayer);
                this.currentRouteLayer = null;
            }
            
            // 更新显示
            this.updateRouteListDisplay();
            this.showMessage('已清除所有路线点和路线');
        },
        
        /**
         * 导出路线信息
         */
        exportRouteInfo: function() {
            if (this.routePoints.length === 0) {
                this.showMessage('没有路线点可以导出', 'warning');
                return;
            }
            
            // 准备导出数据
            const exportData = {
                routeName: '自定义路线',
                date: new Date().toLocaleDateString(),
                points: this.routePoints.map((point, index) => ({
                    index: index + 1,
                    name: point.name,
                    latitude: point.lat,
                    longitude: point.lng
                })),
                totalPoints: this.routePoints.length
            };
            
            // 转换为JSON字符串
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
            
            // 创建下载链接
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "旅游路线_" + new Date().toISOString().slice(0,10) + ".json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
            
            this.showMessage('路线信息已导出');
        },
        
        /**
         * 更新路线点标记的索引
         */
        updateRouteMarkerIndices: function() {
            this.routePoints.forEach((point, index) => {
                const pointKey = `${point.lat},${point.lng}`;
                const marker = this.routeMarkers[pointKey];
                
                if (marker) {
                    const popupContent = `
                        <div class="popup-content">
                            <h4>${point.name}</h4>
                            <p><i class="fas fa-map-pin"></i> 路线点 #${index + 1}</p>
                            <button class="btn btn-danger remove-route-point-btn" data-index="${index}">
                                <i class="fas fa-trash-alt"></i> 从路线中移除
                            </button>
                        </div>
                    `;
                    marker.setPopupContent(popupContent);
                }
            });
        },
        
        /**
         * 更新路线列表显示
         */
        updateRouteListDisplay: function() {
            const routeListContainer = document.getElementById('selected-route-points');
            if (!routeListContainer) return;
            
            routeListContainer.innerHTML = '';
            
            if (this.routePoints.length === 0) {
                routeListContainer.innerHTML = '<p>尚未选择任何地点。请点击地图标记上的"添加到路线"按钮。</p>';
                return;
            }
            
            const ol = document.createElement('ol');
            ol.className = 'route-points-list';
            
            this.routePoints.forEach((point, index) => {
                const li = document.createElement('li');
                li.className = 'route-point-item';
                
                li.innerHTML = `
                    <div class="route-point-info">
                        <span class="route-point-number">${index + 1}</span>
                        <span>${point.name}</span>
                    </div>
                    <div class="route-point-actions">
                        <button class="btn btn-sm btn-primary view-point" title="在地图上查看">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger remove-point" title="移除该地点">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
                
                // 查看按钮点击事件
                const viewBtn = li.querySelector('.view-point');
                viewBtn.addEventListener('click', () => {
                    map.setView([point.lat, point.lng], 17);
                    const pointKey = `${point.lat},${point.lng}`;
                    if (this.routeMarkers[pointKey]) {
                        this.routeMarkers[pointKey].openPopup();
                    }
                });
                
                // 删除按钮点击事件
                const removeBtn = li.querySelector('.remove-point');
                removeBtn.addEventListener('click', () => {
                    this.removePointFromRoute(index);
                });
                
                ol.appendChild(li);
            });
            
            routeListContainer.appendChild(ol);
            this.updateRouteFormInputs();
        },
        
        /**
         * 更新路线表单输入
         */
        updateRouteFormInputs: function() {
            const inputs = document.querySelectorAll('.route-form .route-input');
            if (inputs.length >= 2) {
                inputs[0].value = this.routePoints.length > 0 ? this.routePoints[0].name : '';
                inputs[1].value = this.routePoints.length > 1 ? this.routePoints[this.routePoints.length - 1].name : '';
            }
        },
          /**
         * 规划路线
         */
        planRoute: function() {
            if (this.routePoints.length < 2) {
                alert("请至少选择两个地点（起点和终点）来规划路线。");
                return;
            }
            
            const coordinates = this.routePoints.map(point => ({ lat: point.lat, lng: point.lng }));
            
            // 获取选择的路线规划方式
            const methodRadios = document.getElementsByName('route-method');
            let selectedMethod = 'distance'; // 默认为最短路径
            
            for (const radio of methodRadios) {
                if (radio.checked) {
                    selectedMethod = radio.value;
                    break;
                }
            }
            
            console.log(`准备规划路线，方式: ${selectedMethod}，发送坐标:`, coordinates);
            const planButton = document.querySelector('.route-form .btn');
            if (planButton) planButton.disabled = true;
            
            // 根据选择的方式显示不同的加载提示
            const methodName = selectedMethod === 'distance' ? '最短路径' : '最短时间';
            this.showLoading(`正在规划${methodName}路线...`);
            
            fetch('/map/api/navigation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ 
                    points: coordinates,
                    method: selectedMethod 
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.message || `HTTP error! status: ${response.status}`);
                    }).catch(() => {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {                    if (data.success && data.route && data.route.length > 0) {
                    console.log("收到路线数据:", data);
                    
                    if (this.currentRouteLayer) {
                        map.removeLayer(this.currentRouteLayer);
                    }
                    
                    // 根据规划方式选择不同的路线颜色
                    const routeColor = document.querySelector('input[value="distance"]:checked') ? '#3498db' : '#e67e22';
                    
                    this.currentRouteLayer = L.polyline(data.route, { 
                        color: routeColor, 
                        weight: 5,
                        opacity: 0.7,
                        lineJoin: 'round'
                    }).addTo(map);
                    
                    // 确保路线在最底层显示，标记在最上层
                    this.currentRouteLayer.bringToBack();
                    // this.routeMarkersLayer.bringToFront(); // 旧的错误代码

                    // 新方法：遍历 routeMarkersLayer 中的每个图层并将其置顶
                    if (this.routeMarkersLayer && typeof this.routeMarkersLayer.eachLayer === 'function') {
                        this.routeMarkersLayer.eachLayer(function(layer) {
                            if (layer && typeof layer.bringToFront === 'function') {
                                layer.bringToFront();
                            }
                        });
                    } else {
                        console.warn('MapApp.routeMarkersLayer is not available or not a LayerGroup for bringToFront logic.');
                    }
                    
                    map.fitBounds(this.currentRouteLayer.getBounds(), { padding: [50, 50] });
                    
                    // 获取选择的规划方式
                    const isDistanceMethod = document.querySelector('input[value="distance"]:checked') !== null;
                    
                    let detailsHtml = `
                        <div class="route-details">
                            <h4><i class="fas fa-check-circle"></i> 路线规划成功！</h4>
                            <p><i class="fas fa-info-circle"></i> 规划方式: ${isDistanceMethod ? '最短路径' : '最短时间'}</p>
                    `;
                    
                    if (isDistanceMethod && data.distance) {
                        // 对于最短路径方式，显示距离
                        detailsHtml += `<p><i class="fas fa-road"></i> 总距离: ${(data.distance / 1000).toFixed(2)} 公里</p>`;
                    }
                    
                    if (!isDistanceMethod && data.duration) {
                        // 对于最短时间方式，显示时间
                        const hours = Math.floor(data.duration / 3600);
                        const minutes = Math.round((data.duration % 3600) / 60);
                        let timeStr = '';
                        
                        if (hours > 0) {
                            timeStr += `${hours} 小时 `;
                        }
                        timeStr += `${minutes} 分钟`;
                        
                        detailsHtml += `<p><i class="fas fa-clock"></i> 预计时间: ${timeStr}</p>`;
                    }
                    
                    detailsHtml += '</div>';
                    document.getElementById('details-content').innerHTML = detailsHtml;
                    
                } else {
                    throw new Error(data.message || '无法规划路线或返回数据无效');
                }
            })
            .catch(error => {
                console.error('路线规划失败:', error);
                this.showError('路线规划失败: ' + error.message);
            })
            .finally(() => {
                if (planButton) planButton.disabled = false;
            });
        },
        
        /**
         * 显示加载中状态
         */
        showLoading: function(message) {
            document.getElementById('details-content').innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i> ${message}
                </div>
            `;
        },
        
        /**
         * 显示错误消息
         */
        showError: function(message) {
            document.getElementById('details-content').innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i> ${message}
                </div>
            `;
            console.error(message);
        },
        
        /**
         * 显示普通消息
         */
        showMessage: function(message, type = 'info') {
            document.getElementById('details-content').innerHTML = `
                <div class="message ${type}">
                    <i class="fas fa-info-circle"></i> ${message}
                </div>
            `;
        }
    };
    
    // 规划路线全局函数
    window.planRoute = function() {
        MapApp.planRoute();
    };
    
    // 设置全局变量用于 MapApp 访问
    window.MapApp = MapApp;
    
    // 初始化应用
    MapApp.init();
});
