# 用此类安全的打印调试信息

import os
import json
import datetime


def writeLog(logInfo):
    """
    写入日志
    :param logInfo: 日志信息
    """
    with open("index/log/log.txt", "a", encoding="utf-8") as f:
        f.write(logInfo + "\n")


if __name__ == "__main__":
    writeLog("开始打印日志")
