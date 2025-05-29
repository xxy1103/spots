// 测试图片模态框功能
console.log('test_modal.js loaded');

// 图片导航功能
let currentImageIndex = 0;
let imageElements = [];

// 全局定义 openImageModal 和 closeImageModal 函数
window.openImageModal = function(imgElement, event) {
    console.log('openImageModal called');
    console.log('imgElement:', imgElement);
    console.log('event:', event);
    
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    
    console.log('modal:', modal);
    console.log('modalImg:', modalImg);
    
    if (modal && modalImg) {
        // 获取所有图片元素
        imageElements = Array.from(document.querySelectorAll('.gallery-image'));
        currentImageIndex = imageElements.indexOf(imgElement);
        
        console.log('imageElements count:', imageElements.length);
        console.log('currentImageIndex:', currentImageIndex);
        
        // 设置模态框中的图片源
        modalImg.src = imgElement.src;
        modalImg.dataset.imagePath = imgElement.src;
        
        // 显示模态框
        modal.style.display = 'block';
        
        // 阻止事件冒泡
        if (event) {
            event.stopPropagation();
        }
        
        // 禁止背景滚动
        document.body.style.overflow = 'hidden';
        
        console.log('Modal should be visible now');
        return true;
    } else {
        console.error('Modal elements not found!');
        return false;
    }
};

window.closeImageModal = function() {
    console.log('closeImageModal called');
    const modal = document.getElementById('imageModal');
    
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        console.log('Modal closed');
    }
};

// 简单的键盘事件处理
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeImageModal();
    }
});

// 添加导航功能
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
    
    // 更新图片
    modalImg.src = imageElements[currentImageIndex].src;
    modalImg.dataset.imagePath = imageElements[currentImageIndex].src;
    
    console.log('Navigated to image:', currentImageIndex);
};

// AIGC 视频生成功能
window.generateVideo = function() {
    console.log('generateVideo called');
    
    const modalImg = document.getElementById('modalImage');
    const imagePath = modalImg.dataset.imagePath;
    
    if (!imagePath) {
        alert('未能获取图片路径');
        return;
    }
    
    if (!window.DIARY_ID) {
        alert('未能获取日记ID');
        return;
    }
    
    console.log('Generating video for image:', imagePath);
    console.log('Diary ID:', window.DIARY_ID);
    
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
        console.log('Response received:', response);
        if (response.redirected) {
            // 如果后端返回重定向，直接跳转
            window.location.href = response.url;
            return;
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        hideLoadingSpinner();
        
        if (data && data.success === false) {
            alert(data.message || 'AI视频生成失败');
        } else {
            alert('AI视频生成成功！页面即将刷新...');
            // 延迟刷新页面以显示成功消息
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        console.error('AI视频生成错误:', error);
        hideLoadingSpinner();
        alert('AI视频生成过程中出现错误: ' + error.message);
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

console.log('test_modal.js with all functions loaded successfully');
