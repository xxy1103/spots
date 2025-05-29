from app.app import app
from module.fileIo import UserIo,SpotIo,DiaryIo
from module.user_class import userManager
from module.Spot_class import spotManager
from module.diary_class import diaryManager
import signal
import sys


def save_data_on_shutdown():
    """
    在应用关闭时保存数据的函数。
    """
    # 这里可以添加保存数据的逻辑
    print("正在保存数据...")
    try:
        UserIo.save_users(userManager.to_dict())
        SpotIo.save_spots(spotManager.to_dict())
        DiaryIo.save_diaries(diaryManager.to_dict())
        print("数据已保存。")
    except Exception as e:
        print(f"保存数据时发生错误: {str(e)}")



def shutdown_handler(signal, frame):
    """
    捕获到关闭信号后的处理函数。
    """
    print("接收到关闭信号，正在处理...")
    save_data_on_shutdown()


    print("Flask 应用正在关闭。")
    sys.exit(0) # 正常退出



# 注册信号处理器
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)




if __name__ == "__main__":
    app.run(debug=False)

# True 为调试模式，可以动态加载前端
# False 为生产模式，不能动态加载前端
