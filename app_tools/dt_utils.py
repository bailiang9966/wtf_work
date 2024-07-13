from  datetime import datetime
import time
import pytz

tz_cn = pytz.timezone('Asia/Shanghai')
current_tz = datetime.now(pytz.timezone('UTC')).astimezone().tzinfo
def get_ts(time_str,is_ms = True,str_type = 0):
    '''
    str_type
    0:  2024-05-04 15:51:02
    1:  2024-05-04 15:51
    2:  2024-05-04
    3:  2024-05-03T14:36:10Z
        2024-05-03T14:36:10+09:00

    返回 时间戳数值
    '''
    if   str_type == 3:
        time_obj = datetime.fromisoformat(time_str)
        time_obj = time_obj.astimezone(tz_cn)
        
    else:
        if str_type == 0:
            ttype = "%Y-%m-%d %H:%M:%S"
        elif str_type == 1:
            ttype = "%Y-%m-%d %H:%M"
        elif str_type == 2:
            ttype = "%Y-%m-%d"

        time_obj = datetime.strptime(time_str, ttype)

    tstamp = time_obj.timestamp()
    ts = int(tstamp*1000) if is_ms else int(tstamp)
    return ts

def fmt_time(ts,is_ms = True,showms=False):
    '''
    传入一个时间戳数值
    返回 XXXX-XX-XX XX:XX:XX格式字符串
    '''
    timestamp = ts/1000 if is_ms else ts
    dt = datetime.fromtimestamp(timestamp).astimezone(tz_cn)
    # 使用strftime()函数将datetime对象格式化为指定的字符串格式
    
    if showms:
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    else:
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time


def get_period_ts(period = 1,ts=None):
    if not  ts :
        ts = get_now_ts()
    period_ms= 60000*period
    start_ts = (ts // period_ms) *period_ms
    end_ts =start_ts+period_ms-1
    return start_ts,end_ts


def get_now_ts():
    now_cn = datetime.now(tz_cn)
    timestamp_cn_ms = now_cn.timestamp() * 1000
    return round(timestamp_cn_ms)
        

def fmt_now(showms=False):
    d = fmt_time(get_now_ts(),showms=showms )
    return d

