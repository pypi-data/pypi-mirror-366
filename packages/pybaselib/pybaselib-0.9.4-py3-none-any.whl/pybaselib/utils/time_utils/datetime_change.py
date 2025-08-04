# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/2/28 23:05

import datetime
from datetime import timezone
import time

def get_utc_seconds():
    """
    获取的是标准的 UTC 时间戳
    :return:
    """
    return int(datetime.datetime.now(timezone.utc).timestamp())

def get_strftime():
    """
		获取当前格式化时间
	"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_localTime():
    return datetime.datetime.now()


def get_str_day():
    '''
		获取当天日期string
	'''
    return datetime.datetime.now().strftime('%Y-%m-%d')


def strUtcTime_localTime(utcTime):
    '''
		前端时间选择器给的时间是utctime,需要转为本地时间
		2023-02-27T00:35:15.802000
	'''
    # UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
    utcTime = datetime.datetime.strptime(utcTime, UTC_FORMAT)
    # localTime = utcTime + datetime.timedelta(hours=8)
    return utcTime


def strDayTime_localTime(strTime):
    """
		把字符串时间转为本地时间格式
	"""
    dateTime_p = datetime.datetime.strptime(strTime, '%Y-%m-%d')
    return dateTime_p  # <class 'datetime.datetime'>


def strTime_localTime(strTime):
    """
		把字符串时间转为本地时间格式
	"""
    dateTime_p = datetime.datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S')
    return dateTime_p  # <class 'datetime.datetime'>


def strTime_f_localTime(strTime):
    """
		精确到毫秒  把字符串时间转为本地时间格式
	"""
    dateTime_p = datetime.datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S.%f')
    return dateTime_p  # <class 'datetime.datetime'>


def rebootTime_visualTime(weekTime):
    """
		把 Wed Jan 11 13:56 转为 '2019-12-09 18:48:27'这种时间
	"""
    return time.strftime("{year}-%m-%d %H:%M:%S".format(year=datetime.datetime.today().year),
                         time.strptime(weekTime, "%a %b %d %H:%M"))


def cal_datetime(cal_type, date_time, minutes=0, seconds=0):
    """
		向指定时间增加或减少分钟及秒数
	"""
    if isinstance(date_time, str):
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    if cal_type == "+":
        return date_time + datetime.timedelta(minutes=minutes, seconds=seconds)
    elif cal_type == "-":
        return date_time - datetime.timedelta(minutes=minutes, seconds=seconds)
    else:
        raise Exception("计算类型错误")


def get_grep_mdHM(cal_type, date_time, minutes=3):
    '''
	return (02-08 11:37|02-08 11:36|02-08 11:35|02-08 11:34)
	'''
    if isinstance(date_time, str):
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    # temp = cal_datetime('+',date_time,minutes=1).strftime('%m-%d %H:%M') + '|'
    temp = date_time.strftime('%m-%d %H:%M') + '|'

    for loop in range(minutes):
        result_date = cal_datetime(cal_type, date_time, minutes=1)
        if loop == minutes - 1:
            temp += result_date.strftime('%m-%d %H:%M')
        else:
            temp += result_date.strftime('%m-%d %H:%M') + '|'
        date_time = result_date
    return "({timelimit})".format(timelimit=temp)


def get_grep_c_dmesg(cal_type, date_time, minutes=3):
    """
	%c 返回这种时间格式输出 Mon Feb  6 13:14:00 2023

	return : (Wed Feb  8 11:37|Wed Feb  8 11:36|Wed Feb  8 11:35|Wed Feb  8 11:34)
	"""
    if isinstance(date_time, str):
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    # temp = cal_datetime('+',date_time,minutes=1).strftime('%m-%d %H:%M') + '|'
    temp = '{c_time}'.format(c_time=date_time.strftime('%c')[:-8]) + '|'

    for loop in range(minutes):
        result_date = cal_datetime(cal_type, date_time, minutes=1)
        if loop == minutes - 1:
            temp += '{c_time}'.format(c_time=result_date.strftime('%c')[:-8])
        else:
            temp += '{c_time}'.format(c_time=result_date.strftime('%c')[:-8]) + '|'
        date_time = result_date
    return "({timelimit})".format(timelimit=temp)


def get_grep_c_syslog(cal_type, date_time, minutes=3):
    """
	%c 返回这种时间格式输出 Mon Feb  6 13:14:00 2023

	return : (Wed Feb  8 11:37|Wed Feb  8 11:36|Wed Feb  8 11:35|Wed Feb  8 11:34)
	"""
    if isinstance(date_time, str):
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    # temp = cal_datetime('+',date_time,minutes=1).strftime('%m-%d %H:%M') + '|'
    temp = '{c_time}'.format(c_time=date_time.strftime('%c')[:-8][4:]) + '|'

    for loop in range(minutes):
        result_date = cal_datetime(cal_type, date_time, minutes=1)
        if loop == minutes - 1:
            temp += '{c_time}'.format(c_time=result_date.strftime('%c')[:-8][4:])
        else:
            temp += '{c_time}'.format(c_time=result_date.strftime('%c')[:-8][4:]) + '|'
        date_time = result_date
    return "({timelimit})".format(timelimit=temp)


def get_grep_YmdHM(cal_type, date_time, minutes=3):
    '''
	return (2023-02-19 02-08 11:37|2023-02-19 02-08 11:36|2023-02-19 02-08 11:35|2023-02-19 02-08 11:34)
	'''
    if isinstance(date_time, str):
        date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    # temp = cal_datetime('+',date_time,minutes=1).strftime('%m-%d %H:%M') + '|'
    temp = date_time.strftime('%Y-%m-%d %H:%M') + '|'

    for loop in range(minutes):
        result_date = cal_datetime(cal_type, date_time, minutes=1)
        if loop == minutes - 1:
            temp += result_date.strftime('%Y-%m-%d %H:%M')
        else:
            temp += result_date.strftime('%Y-%m-%d %H:%M') + '|'
        date_time = result_date
    return "({timelimit})".format(timelimit=temp)


def timeDifference_seconds(startTime, endTime, return_type: str):
    """
		按秒为单位计算两个时间差
		startTime 开始时间 str
		endTime 结束时间 str
		total_seconds 为 int
	"""
    if isinstance(startTime, str):
        startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    if isinstance(endTime, str):
        endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
    seconds = (endTime - startTime).seconds
    # 来获取时间差中的秒数。注意，seconds获得的秒只是时间差中的小时、分钟和秒部分的和，并没有包含时间差的天数（既是两个时间点不是同一天，失效）
    total_seconds = (endTime - startTime).total_seconds()
    # mins = total_seconds / 60
    if return_type == "seconds":
        return total_seconds
    elif return_type == "minutes":
        return int(total_seconds / 60)
    elif return_type == "hours":
        return int(total_seconds / 60 / 60)
    else:
        return int(total_seconds / 60 / 60 / 24)
