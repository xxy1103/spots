// 图片懒加载修复补丁
// 在页面加载完成后执行

document.addEventListener('DOMContentLoaded', function() {
    // 延迟执行，确保主脚本已加载
    setTimeout(function() {
        // 创建全局的图片懒加载观察器
        window.globalImageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src;
                    
                    if (src && !img.classList.contains('loaded') && !img.classList.contains('loading')) {
                        img.classList.add('loading');
                        
                        // 显示加载状态
                        const wrapper = img.closest('.image-wrapper');
                        if (wrapper) {
                            const skeleton = wrapper.querySelector('.image-skeleton');
                            const loadingIndicator = wrapper.querySelector('.image-loading-indicator');
                            if (skeleton) skeleton.style.display = 'block';
                            if (loadingIndicator) loadingIndicator.style.display = 'flex';
                        }
                        
                        // 加载图片
                        const newImg = new Image();
                        newImg.onload = function() {
                            img.src = src;
                            img.classList.remove('loading');
                            img.classList.add('loaded');
                            img.style.opacity = '1';
                            
                            // 隐藏加载状态
                            if (wrapper) {
                                const skeleton = wrapper.querySelector('.image-skeleton');
                                const loadingIndicator = wrapper.querySelector('.image-loading-indicator');
                                if (skeleton) skeleton.style.display = 'none';
                                if (loadingIndicator) loadingIndicator.style.display = 'none';
                            }
                        };
                        newImg.onerror = function() {
                            img.classList.remove('loading');
                            img.classList.add('error');
                            console.warn('图片加载失败:', src);
                        };
                        newImg.src = src;
                        
                        // 取消观察这个图片
                        window.globalImageObserver.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.01
        });
        
        // 观察所有现有的懒加载图片
        function observeAllLazyImages() {
            const lazyImages = document.querySelectorAll('img.lazy-load:not(.observed)');
            lazyImages.forEach(function(img) {
                window.globalImageObserver.observe(img);
                img.classList.add('observed');
            });
        }
        
        // 初始观察
        observeAllLazyImages();
        
        // 监听DOM变化，处理动态添加的内容
        const observer = new MutationObserver(function(mutations) {
            let hasNewImages = false;
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // 元素节点
                            const newLazyImages = node.querySelectorAll ? 
                                node.querySelectorAll('img.lazy-load:not(.observed)') : [];
                            if (newLazyImages.length > 0) {
                                hasNewImages = true;
                            }
                        }
                    });
                }
            });
            
            if (hasNewImages) {
                // 延迟重新观察，确保DOM更新完成
                setTimeout(observeAllLazyImages, 100);
            }
        });
        
        // 开始观察文档变化
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('图片懒加载修复补丁已加载');
    }, 500);
});
