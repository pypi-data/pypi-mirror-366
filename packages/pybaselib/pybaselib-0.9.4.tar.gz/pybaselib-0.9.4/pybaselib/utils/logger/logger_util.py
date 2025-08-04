# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/4/9 09:12
import logging
import os
import shutil
from pybaselib.utils.time_utils.datetime_change import get_timestamp

# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# LOG_DIR = os.path.join(BASE_DIR, "logs")
# FAILED_DIR = os.path.join(LOG_DIR, "failed_cases")
# os.makedirs(LOG_DIR, exist_ok=True)


# os.makedirs(FAILED_DIR, exist_ok=True)

def setup_case_logger(log_dir: str, level=logging.INFO) -> str:
    """
    设置日志输出，返回当前 case 独立日志路径
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # 清空旧 handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    timestamp = get_timestamp()
    # case_log_name = f"{case_name}_{timestamp}.log"
    all_log_name = f"all_case_{timestamp}.log"

    single_case_log = os.path.join(log_dir, "single_case.log")
    # per_case_log = os.path.join(LOG_DIR, case_log_name)
    all_cases_log = os.path.join(log_dir, all_log_name)

    handlers = [
        logging.FileHandler(single_case_log, mode="w", encoding="utf-8"),
        # logging.FileHandler(per_case_log, mode="w", encoding="utf-8"),
        logging.FileHandler(all_cases_log, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    for h in handlers:
        h.setFormatter(formatter)
        logger.addHandler(h)

    return single_case_log

# def copy_failed_log(src_log_path: str, case_name: str):
#     """
#     失败用例复制日志到 failed_cases 目录下
#     """
#     if os.path.exists(src_log_path):
#         dst_path = os.path.join(FAILED_DIR, os.path.basename(src_log_path))
#         shutil.copyfile(src_log_path, dst_path)
