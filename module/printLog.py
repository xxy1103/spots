# 用此类安全的打印调试信息


def writeLog(logInfo,debug=True):
    """
    写入日志
    :param logInfo: 日志信息
    """
    if debug:
        # 如果是debug模式，直接打印日志信息
        print(logInfo)
        return
    with open("index/log/log.txt", "a", encoding="utf-8") as f:
        f.write(logInfo + "\n")


if __name__ == "__main__":
    writeLog("开始打印日志")
