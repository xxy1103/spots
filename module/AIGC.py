import os
import time
import base64
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests
from PIL import Image
from volcenginesdkarkruntime import Ark


# 加载 .env 文件中的环境变量
load_dotenv()


class AIGC:
    """
    AIGC类：用于图片生成视频的完整工作流
    1. 通过视觉模型分析图片生成动画提示词
    2. 使用生成的提示词创建图生视频任务
    """
    
    def __init__(self):
        """初始化AIGC客户端"""
        self.client = self._init_client()
        self.vision_model = "doubao-1.5-vision-pro-250328"
        self.i2v_model = "doubao-seedance-1-0-lite-i2v-250428"
    
    def _init_client(self):
        """初始化火山引擎客户端"""
        try:
            # 这里需要根据实际的火山引擎SDK初始化方式进行调整
            client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                api_key=os.environ.get("volcengine_api_key"),
            )
            return client
        except Exception as e:
            print(f"客户端初始化失败: {e}")
            raise
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将本地图片编码为base64格式，自动检测图片格式"""
        try:
            # 先验证图片
            self._validate_image(image_path)
            
            # 通过PIL检测图片格式
            with Image.open(image_path) as img:
                img_format = img.format.lower()
                
            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 根据实际格式设置MIME类型
            if img_format in ['jpeg', 'jpg']:
                mime_type = "image/jpeg"
            elif img_format == 'png':
                mime_type = "image/png"
            elif img_format == 'webp':
                mime_type = "image/webp"
            else:
                # 默认使用jpeg
                mime_type = "image/jpeg"
                
            return f"data:{mime_type};base64,{encoded_string}"
            
        except Exception as e:
            print(f"图片编码失败: {e}")
            raise
    
    def _validate_image(self, image_path: str) -> bool:
        """验证图片文件是否存在且格式正确"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                # 验证图片格式
                if img.format not in ['JPEG', 'PNG', 'JPG']:
                    raise ValueError(f"不支持的图片格式: {img.format}")
            return True
        except Exception as e:
            raise ValueError(f"图片文件无效: {e}")
    
    def generate_animation_prompt(self, image_path: str) -> str:
        """
        第一步：使用视觉模型分析图片，生成适合制作动画的提示词
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            生成的动画提示词
        """
        try:
            # 验证图片
            self._validate_image(image_path)
            
            # 编码图片
            image_base64 = self._encode_image_to_base64(image_path)
            
            # 构建视觉模型的提示词
            vision_prompt = """
            请仔细分析这张图片，为其生成一个适合制作动画视频的详细提示词。
            要求：
            1. 描述图片中的主要元素和场景
            2. 建议合适的动画效果，如：镜头运动、元素动作、光影变化等
            3. 考虑动画的节奏和时长
            4. 包含技术参数建议（分辨率、时长等）
            
            请直接返回可用于图生视频的提示词，格式如下：
            [详细的场景描述] [动画效果描述] --resolution 720p --dur 5 --camerafixed false
            """
            
            # 调用视觉模型
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_base64
                                },
                            },
                            {"type": "text", "text": vision_prompt},
                        ],
                    }
                ],
            )
            
            # 提取生成的提示词
            
            generated_prompt = response.choices[0].message.content.strip()
            print(f"生成的动画提示词: {generated_prompt}")
            return generated_prompt            
        except Exception as e:
            print(f"生成动画提示词失败: {e}")
            raise
    
    def create_video_from_image(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        第二步：根据图片和提示词创建视频生成任务
        
        Args:
            image_path: 本地图片路径
            custom_prompt: 自定义提示词，如果不提供则自动生成
            
        Returns:
            视频生成任务的详细信息
        """
        try:
            # 验证图片
            self._validate_image(image_path)
            
            # 如果没有提供自定义提示词，则自动生成
            if custom_prompt is None:
                prompt = self.generate_animation_prompt(image_path)
            else:
                prompt = custom_prompt
            
            # 直接将图片编码为base64，不需要上传
            image_base64 = self._encode_image_to_base64(image_path)
            
            # 创建图生视频任务
            create_result = self.client.content_generation.tasks.create(
                model=self.i2v_model,
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64  # 直接使用base64编码
                        }
                    }
                ]
            )
            
            print(f"视频生成任务已创建，任务ID: {create_result.id}")
            return {
                "task_id": create_result.id,
                "status": "created",
                "prompt": prompt,                "image_path": image_path
            }
            
        except Exception as e:
            print(f"创建视频生成任务失败: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取视频生成任务的状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        try:
            result = self.client.content_generation.tasks.get(task_id=task_id)
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result
            }
        except Exception as e:
            print(f"获取任务状态失败: {e}")
            raise
    def wait_for_completion(self, task_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """
        等待视频生成任务完成
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            完成后的任务结果
        """
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                status = self.get_task_status(task_id)
                if status["result"].status in ["succeeded", "failed", "cancelled"]:
                    return status
                
                print(f"任务状态: {status['result'].status}，继续等待...")
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                print(f"检查任务状态时出错: {e}")
                time.sleep(5)
        
        raise TimeoutError(f"任务在{max_wait_time}秒内未完成")
    
    def generate_video_complete_workflow(self, image_path: str, custom_prompt: Optional[str] = None, 
                                      save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        完整的图片生成视频工作流
        
        Args:
            image_path: 本地图片路径
            custom_prompt: 自定义提示词（可选）
            save_path: 视频保存路径（可选，默认为根目录）
            
        Returns:
            完整的处理结果
        """
        try:
            print(f"开始处理图片: {image_path}")
              # 设置默认保存路径
            if save_path is None:
                # 默认保存到当前工作目录，文件名基于时间戳
                timestamp = int(time.time())
                save_path = os.path.abspath(f"generated_video_{timestamp}.mp4")
            else:
                # 确保路径是绝对路径
                save_path = os.path.abspath(save_path)
            
            # 确保保存目录存在
            save_dir = os.path.dirname(save_path)
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
            
            print(f"视频将保存到: {save_path}")
            
            # 第一步：创建视频生成任务
            task_info = self.create_video_from_image(image_path, custom_prompt)
            # 第二步：等待任务完成
            print("等待视频生成完成...")
            result = self.wait_for_completion(task_info["task_id"])
            
            if result["result"].status == "succeeded":
                print("视频生成成功！")
                # 第三步：下载视频到指定路径
                # 正确获取 video_url
                video_url = None
                # result["result"].content 可能是 Content 对象
                if hasattr(result["result"], "content"):
                    content = result["result"].content
                    # content 可能是对象也可能是字典
                    if isinstance(content, dict):
                        video_url = content.get("video_url")
                    else:
                        video_url = getattr(content, "video_url", None)
                local_video_path = None
                
                if video_url:
                    try:
                        local_video_path = self._download_video(video_url, save_path)
                        print(f"视频已保存到: {local_video_path}")
                    except Exception as e:
                        print(f"视频下载失败: {e}")
                else:
                    print("视频生成成功，但未提供下载链接")
                
                return {
                    "success": True,
                    "task_id": task_info["task_id"],
                    "prompt": task_info["prompt"],
                    "video_url": video_url,
                    "local_video_path": local_video_path,
                    "save_path": save_path,
                    "result": result
                }
            else:
                print(f"视频生成失败，状态: {result['status']}")
                return {
                    "success": False,
                    "task_id": task_info["task_id"],                    "status": result["status"],
                    "error": "视频生成失败"
                }
                
        except Exception as e:
            print(f"完整工作流执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    def _download_video(self, video_url: str, save_path: str) -> str:
        """
        下载视频文件到本地路径
        
        Args:
            video_url: 视频URL
            save_path: 本地保存路径
            
        Returns:
            本地视频文件路径
        """
        try:
            import requests
            
            print(f"正在下载视频: {video_url}")
            
            # 规范化保存路径
            save_path = os.path.abspath(save_path)
            save_dir = os.path.dirname(save_path)
            
            # 确保保存目录存在
            if save_dir:  # 只有当目录不为空时才创建
                os.makedirs(save_dir, exist_ok=True)
            
            print(f"视频将保存到: {save_path}")
            
            # 发送GET请求下载视频
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            # 写入视频文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"视频下载完成: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"视频下载失败: {e}")
            raise


# 使用示例
if __name__ == "__main__":
    # 创建AIGC实例
    aigc = AIGC()
    
    # 示例图片路径（请替换为实际路径）
    image_path = "path/to/your/image.jpg"
    
    try:
        # 执行完整的图片生成视频工作流
        result = aigc.generate_video_complete_workflow(image_path)
        
        if result["success"]:
            print("视频生成成功！")
            print(f"任务ID: {result['task_id']}")
            print(f"使用的提示词: {result['prompt']}")
            if result.get("video_url"):
                print(f"视频URL: {result['video_url']}")
        else:
            print(f"视频生成失败: {result['error']}")
            
    except Exception as e:
        print(f"执行失败: {e}")