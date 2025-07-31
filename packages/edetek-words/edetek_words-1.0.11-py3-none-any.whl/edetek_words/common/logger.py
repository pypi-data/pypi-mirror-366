"""
Created on Mar 17, 2020

@author: xiaodong.li
"""
import os
import sys

from loguru import logger

from edetek_words.common.path import root


def init_logger(log_filename="app.log", level="DEBUG", write_file=False):
    logger.remove()
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>"
    )
    if write_file:
        log_dir = get_writable_log_path()
        logger.add(
            os.path.join(log_dir, log_filename),
            level=level,
            rotation="00:00",  # 每天午夜切分
            retention="7 days",  # 最多保留7天
            compression="zip",  # 自动压缩旧日志
            encoding="utf-8",
            enqueue=True  # 支持多进程
        )


def get_writable_log_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = root()
    logs_dir = os.path.join(base_path, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


init_logger()
