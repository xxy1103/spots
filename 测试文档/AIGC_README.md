# AIGC类使用说明

## 功能概述

AIGC类是一个完整的图片生成视频工作流实现，具有以下功能：

1. **智能提示词生成**：使用视觉模型分析输入图片，自动生成适合制作动画的详细提示词
2. **图片到视频转换**：基于生成的提示词和原图片，创建高质量的动画视频
3. **任务状态监控**：实时跟踪视频生成进度，自动等待任务完成

## 主要特性

- 🤖 **AI驱动**：使用豆包视觉模型和图生视频模型
- 🎨 **智能分析**：自动分析图片内容，生成最适合的动画效果
- ⚡ **异步处理**：支持后台任务处理和状态监控
- 🛡️ **错误处理**：完善的异常处理和状态验证
- 🔧 **灵活配置**：支持自定义提示词和参数调整

## 安装依赖

```bash
pip install -r requirement.txt
```

## 环境配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的API密钥：
```
ARK_API_KEY=your_ark_api_key_here
volcengine=your_volcengine_client_here
```

## 基本使用

### 快速开始

```python
from module.AIGC import AIGC

# 创建AIGC实例
aigc = AIGC()

# 执行完整的图片生成视频工作流
result = aigc.generate_video_complete_workflow("path/to/your/image.jpg")

if result["success"]:
    print(f"视频生成成功！任务ID: {result['task_id']}")
    print(f"视频URL: {result.get('video_url')}")
else:
    print(f"生成失败: {result['error']}")
```

### 高级使用

#### 1. 仅生成动画提示词

```python
aigc = AIGC()
prompt = aigc.generate_animation_prompt("image.jpg")
print(f"生成的提示词: {prompt}")
```

#### 2. 使用自定义提示词

```python
custom_prompt = "镜头缓慢推近，阳光洒在画面上 --resolution 720p --dur 5"
result = aigc.generate_video_complete_workflow(
    "image.jpg", 
    custom_prompt=custom_prompt
)
```

#### 3. 分步执行

```python
# 步骤1：创建任务
task_info = aigc.create_video_from_image("image.jpg")

# 步骤2：监控任务状态
status = aigc.get_task_status(task_info["task_id"])

# 步骤3：等待完成
result = aigc.wait_for_completion(task_info["task_id"])
```

## API参考

### AIGC类

#### 主要方法

- `generate_animation_prompt(image_path)` - 生成动画提示词
- `create_video_from_image(image_path, custom_prompt=None)` - 创建视频生成任务
- `get_task_status(task_id)` - 获取任务状态
- `wait_for_completion(task_id, max_wait_time=300)` - 等待任务完成
- `generate_video_complete_workflow(image_path, custom_prompt=None)` - 完整工作流

#### 参数说明

- `image_path`: 本地图片文件路径
- `custom_prompt`: 自定义动画提示词（可选）
- `task_id`: 视频生成任务ID
- `max_wait_time`: 最大等待时间（秒，默认300）

### 返回值格式

#### 成功响应
```python
{
    "success": True,
    "task_id": "task_12345",
    "prompt": "生成的或使用的提示词",
    "video_url": "https://...",  # 生成的视频URL
    "result": {...}  # 完整的API响应
}
```

#### 失败响应
```python
{
    "success": False,
    "error": "错误描述",
    "task_id": "task_12345"  # 如果任务已创建
}
```

## 测试

运行测试脚本：
```bash
python test_aigc.py
```

## 注意事项

1. **图片格式**：支持JPEG、PNG格式
2. **文件大小**：建议图片大小不超过10MB
3. **API限制**：请注意火山引擎API的调用频率限制
4. **网络要求**：需要稳定的网络连接进行API调用

## 错误处理

常见错误及解决方案：

- `FileNotFoundError`: 检查图片文件路径是否正确
- `ValueError`: 检查图片格式是否支持
- `TimeoutError`: 增加最大等待时间或检查网络连接
- `API Error`: 检查API密钥配置和网络连接

## 技术架构

```
图片输入 → 视觉模型分析 → 生成提示词 → 图生视频模型 → 视频输出
    ↓           ↓              ↓           ↓           ↓
  验证格式    AI内容理解     智能优化     GPU渲染     质量检查
```

## 更新日志

- v1.0.0: 初始版本，支持基本的图片生成视频功能
- 支持自动提示词生成
- 支持自定义提示词
- 完善的错误处理和状态监控

## 许可证

本项目仅供学习和研究使用。
