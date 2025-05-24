document.addEventListener('DOMContentLoaded', function() {
    // 检查会话
    fetch('/api/check-session', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok && response.status === 200) {
            return response.json();
        } else if (response.status === 401) {
            console.log('无有效会话，请登录。');
            return null;
        } else {
            throw new Error('检查会话时发生错误: ' + response.statusText);
        }
    })
    .then(data => {
        if (data && data.success === true) {
            console.log('检测到有效会话，用户:', data.user.username, '正在跳转...');
            window.location.href = '/spots';
        }
    })
    .catch(error => {
        console.error('检查会话请求失败:', error);
    });

    // 登录表单提交
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();
            
            // 清除之前的错误提示
            removeErrorMessage();

            if (username === '' || password === '') {
                displayErrorMessage('用户名和密码不能为空', usernameInput.parentElement);
                return;
            }
            
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    window.location.href = '/spots';
                } else {
                    displayErrorMessage(data.message || '用户名或密码错误', loginForm);
                }
            })
            .catch(error => {
                console.error('登录错误:', error);
                displayErrorMessage('登录过程中发生错误，请稍后再试', loginForm);
            });
        });
    }

    // 游客登录 (如果存在该按钮)
    const guestLoginButton = document.getElementById('guestLogin');
    if (guestLoginButton) {
        guestLoginButton.addEventListener('click', function() {
            fetch('/api/guest-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    window.location.href = '/spots';
                } else {
                    // 游客登录失败的提示可以显示在页面上，而不是alert
                    const loginContainer = document.querySelector('.login-container');
                    if (loginContainer) {
                        displayErrorMessage(data.message || '无法创建游客账号', loginContainer);
                    }
                }
            })
            .catch(error => {
                console.error('游客登录错误:', error);
                const loginContainer = document.querySelector('.login-container');
                if (loginContainer) {
                    displayErrorMessage('游客登录过程中发生错误，请稍后再试', loginContainer);
                }
            });
        });
    }

    // 辅助函数：显示错误信息
    function displayErrorMessage(message, parentElement) {
        removeErrorMessage(); // 先移除已有的错误信息
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message'; // 使用CSS定义的错误样式
        errorDiv.textContent = message;
        // 将错误信息插入到指定父元素的末尾，或者根据需要调整位置
        if (parentElement) {
            parentElement.appendChild(errorDiv);
        } else {
            // 如果没有指定父元素，可以考虑添加到body或某个固定的错误提示区域
            document.body.appendChild(errorDiv);
        }
    }

    // 辅助函数：移除错误信息
    function removeErrorMessage() {
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }

    // 输入框聚焦动画/效果 (可选)
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
