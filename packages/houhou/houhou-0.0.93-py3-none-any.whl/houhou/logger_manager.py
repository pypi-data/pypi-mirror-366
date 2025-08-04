# easylogger/core.py
import logging
import logging.handlers
import os
import sys
from typing import Optional, Union, Dict, Any

# 全局状态
_LOGGING_CONFIGURED = False
_DEFAULT_LOG_LEVEL = logging.INFO
_DEFAULT_FORMAT = '%(asctime)s - [line:%(lineno)d] - %(name)s - %(levelname)s - %(message)s'


class EasyLogger:
    """EasyLogger核心类，提供日志配置和获取功能"""

    @staticmethod
    def configure(
            log_file: Optional[str] = None,
            log_level: Union[int, str] = _DEFAULT_LOG_LEVEL,
            max_bytes: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5,
            format_str: str = _DEFAULT_FORMAT,
            console_output: bool = True,
            file_mode: str = 'a',
            when: str = 'midnight',
            interval: int = 1,
            encoding: str = 'utf-8'
    ) -> None:
        """
        配置全局日志系统

        :param log_file: 日志文件路径，None表示不记录到文件
        :param log_level: 日志级别(整数或字符串: 'DEBUG', 'INFO'等)
        :param max_bytes: 日志文件最大字节数（用于RotatingFileHandler）
        :param backup_count: 备份文件数量
        :param format_str: 日志格式
        :param console_output: 是否输出到控制台
        :param file_mode: 文件打开模式 ('a' 追加, 'w' 覆盖)
        :param when: 日志滚动时间 (S-秒, M-分, H-小时, D-天, midnight-午夜)
        :param interval: 滚动间隔
        :param encoding: 文件编码
        """
        global _LOGGING_CONFIGURED

        if _LOGGING_CONFIGURED:
            logging.warning("日志系统已配置，忽略重复配置")
            return

        # 转换日志级别
        if isinstance(log_level, str):
            level_name = log_level.upper()
            level_mapping = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            if level_name not in level_mapping:
                raise ValueError(f"无效的日志级别: {level_name}")
            log_level = level_mapping[level_name]

        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # 创建格式化器
        formatter = logging.Formatter(format_str)

        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(log_level)
            root_logger.addHandler(console_handler)

        # 文件处理器（如果提供日志文件路径）
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # 根据参数选择文件处理器类型
            if when:
                # 使用TimedRotatingFileHandler按时间滚动
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    log_file,
                    when=when,
                    interval=interval,
                    backupCount=backup_count,
                    encoding=encoding
                )
            else:
                # 使用RotatingFileHandler按大小滚动
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding=encoding,
                    mode=file_mode
                )

            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)

        _LOGGING_CONFIGURED = True
        root_logger.info(f"EasyLogger已配置完成，日志级别: {logging.getLevelName(log_level)}")
        if log_file:
            root_logger.info(f"日志文件: {log_file} (模式: {file_mode})")
        if console_output:
            root_logger.info("控制台输出已启用")

    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """
        获取日志记录器

        :param name: 日志器名称，通常使用 __name__
        :return: 配置好的日志记录器
        """
        global _LOGGING_CONFIGURED

        if not _LOGGING_CONFIGURED:
            # 自动配置默认日志系统（只输出到控制台）
            EasyLogger.configure()

        # 获取指定名称的日志器
        logger = logging.getLogger(name)
        return logger

    @staticmethod
    def set_log_level(level: Union[int, str]) -> None:
        """
        设置全局日志级别

        :param level: 日志级别 (整数或字符串: 'DEBUG', 'INFO'等)
        """
        global _LOGGING_CONFIGURED

        if not _LOGGING_CONFIGURED:
            EasyLogger.configure()

        # 转换日志级别
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # 更新所有处理器的级别
        for handler in root_logger.handlers:
            handler.setLevel(level)

        root_logger.info(f"全局日志级别已设置为: {logging.getLevelName(level)}")

    @staticmethod
    def add_file_handler(
            log_file: str,
            logger_name: Optional[str] = None,
            level: Union[int, str] = logging.NOTSET,
            format_str: Optional[str] = None,
            max_bytes: int = 10 * 1024 * 1024,
            backup_count: int = 5,
            when: Optional[str] = None,
            interval: int = 1,
            file_mode: str = 'a',
            encoding: str = 'utf-8'
    ) -> None:
        """
        为特定日志器添加额外的文件处理器

        :param log_file: 日志文件路径
        :param logger_name: 日志器名称（None表示根日志器）
        :param level: 日志级别
        :param format_str: 日志格式
        :param max_bytes: 最大文件大小
        :param backup_count: 备份数量
        :param when: 滚动时间单位
        :param interval: 滚动间隔
        :param file_mode: 文件模式
        :param encoding: 文件编码
        """
        # 获取日志器
        logger = logging.getLogger(logger_name)

        # 转换日志级别
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.NOTSET)

        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 创建文件处理器
        if when:
            handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding=encoding
            )
        else:
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding,
                mode=file_mode
            )

        # 设置级别
        if level != logging.NOTSET:
            handler.setLevel(level)

        # 设置格式
        if format_str:
            handler.setFormatter(logging.Formatter(format_str))
        elif logger.handlers:
            # 使用第一个处理器的格式
            handler.setFormatter(logger.handlers[0].formatter)
        else:
            # 默认格式
            handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))

        # 添加到日志器
        logger.addHandler(handler)
        logger.info(f"添加文件日志处理器: {log_file}")

    @staticmethod
    def is_configured() -> bool:
        """检查日志系统是否已配置"""
        return _LOGGING_CONFIGURED


# 关闭自动配置（通过环境变量）
if not _LOGGING_CONFIGURED and os.environ.get("EASYLOG_AUTO_CONFIGURE", "false").lower() == "true":
    EasyLogger.configure()