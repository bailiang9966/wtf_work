from .maincfg import *
from datetime import datetime
import pytz

import urllib3
urllib3.disable_warnings()

import logging

# 使用所需的时区创建一个格式化器
timezone = pytz.timezone('Asia/Shanghai')  # 将时区设置为东八区


def convert_time(record, datefmt):
    '''
    设置默认的datefmt没有用
    '''
    time = datetime.fromtimestamp(record.created).astimezone(timezone)
    return time.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

def setup_logger():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter.formatTime = convert_time

    #在colab上执行不做这个设置还会有一个默认的输出
    logging.getLogger().handlers = []

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    # logging.basicConfig(handlers=[stream_handler], force=True) 
# 初始化logger
setup_logger()