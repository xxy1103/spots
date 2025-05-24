document.addEventListener('DOMContentLoaded', function() {
    // 标签数据
    const spotTypes = [
        "历史建筑", "赏花胜地", "萌萌动物", "城市漫步", "夜游观景",
        "遛娃宝藏地", "展馆展览", "地标观景", "登高爬山", "踏青必去",
        "自然山水", "游乐场", "演出"
    ];

    const tagsContainer = document.getElementById('tagsContainer');
    const tagLimitWarning = document.getElementById('tagLimitWarning');
    const selectedTagsInput = document.getElementById('selectedTags'); 
    const maxTags = 5;
    let selectedTags = [];

    if (tagsContainer) {
        spotTypes.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag-item';
            tagElement.textContent = tag;
            tagElement.addEventListener('click', () => {
                toggleTag(tagElement, tag);
            });
            tagsContainer.appendChild(tagElement);
        });
    }

    function toggleTag(element, tag) {
        if (element.classList.contains('selected')) {
            element.classList.remove('selected');
            selectedTags = selectedTags.filter(t => t !== tag);
            if(tagLimitWarning) tagLimitWarning.style.display = 'none';
        } else {
            if (selectedTags.length < maxTags) {
                element.classList.add('selected');
                selectedTags.push(tag);
                if(tagLimitWarning) tagLimitWarning.style.display = 'none'; // Hide warning if successfully selected
            } else {
                if(tagLimitWarning) {
                    tagLimitWarning.style.display = 'block';
                    setTimeout(() => {
                        tagLimitWarning.style.display = 'none';
                    }, 2000);
                }
                return;
            }
        }
        if (selectedTagsInput) selectedTagsInput.value = JSON.stringify(selectedTags);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            removeErrorMessage(); // 清除旧的错误信息

            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm-password');

            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();

            if (username === '') {
                displayErrorMessage('请输入用户名', usernameInput.parentElement);
                return;
            }
            if (password === '') {
                displayErrorMessage('请设置密码', passwordInput.parentElement);
                return;
            }
            if (password.length < 6) { // 示例：密码长度校验
                displayErrorMessage('密码长度至少为6位', passwordInput.parentElement);
                return;
            }
            if (password !== confirmPassword) {
                displayErrorMessage('两次输入的密码不一致', confirmPasswordInput.parentElement);
                return;
            }
            if (selectedTags.length === 0) {
                displayErrorMessage('请至少选择一个兴趣标签', tagsContainer.parentElement);
                return;
            }

            const formData = {
                username: username,
                password: password,
                selectedTags: selectedTags 
            };

            fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200 && body.success === true) {
                    // 注册成功，可以显示一个更友好的提示，然后跳转
                    displayGlobalMessage(body.message || '注册成功！即将跳转到登录页面...', 'success');
                    setTimeout(() => {
                        window.location.href = '/login'; 
                    }, 2000); // 延迟跳转，让用户看到提示
                } else {
                    displayErrorMessage(body.message || '注册失败，请检查输入信息', registerForm);
                }
            })
            .catch(error => {
                console.error('注册请求失败:', error);
                displayErrorMessage('注册过程中发生网络错误，请稍后再试。', registerForm);
            });
        });
    }

    // 辅助函数：显示错误信息
    function displayErrorMessage(message, parentElement) {
        removeErrorMessage();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        if (parentElement) {
            // 插入到父元素的最后一个子元素之前，或者直接appendChild
            parentElement.appendChild(errorDiv);
        } else {
            registerForm.insertBefore(errorDiv, registerForm.firstChild); // 默认添加到表单顶部
        }
    }

    // 辅助函数：移除错误信息
    function removeErrorMessage() {
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // 辅助函数：显示全局提示信息 (例如，在页面顶部)
    function displayGlobalMessage(message, type = 'info') {
        const globalMessageContainer = document.getElementById('globalMessageContainer') || createGlobalMessageContainer();
        globalMessageContainer.textContent = message;
        globalMessageContainer.className = `global-message global-message-${type}`;
        globalMessageContainer.style.display = 'block';

        // 可选：一段时间后自动隐藏
        // setTimeout(() => {
        //     globalMessageContainer.style.display = 'none';
        // }, 3000);
    }

    function createGlobalMessageContainer() {
        const container = document.createElement('div');
        container.id = 'globalMessageContainer';
        // 将其插入到 body 的最前面或 .register-container 的最前面
        const registerContainer = document.querySelector('.register-container');
        if (registerContainer) {
            registerContainer.parentNode.insertBefore(container, registerContainer);
        } else {
            document.body.insertBefore(container, document.body.firstChild);
        }
        return container;
    }

    // 输入框聚焦动画/效果 (可选, 与login.js类似)
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
});
