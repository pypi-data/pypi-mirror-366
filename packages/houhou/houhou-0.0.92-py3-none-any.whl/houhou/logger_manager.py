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
            env_prefix: str = "EASYLOG"
    ) -> None:
        """
        配置全局日志系统

        :param log_file: 日志文件路径，None表示不记录到文件
        :param log_level: 日志级别(整数或字符串: 'DEBUG', 'INFO'等)
        :param max_bytes: 日志文件最大字节数
        :param backup_count: 备份文件数量
        :param format_str: 日志格式
        :param console_output: 是否输出到控制台
        :param env_prefix: 环境变量前缀
        """
        global _LOGGING_CONFIGURED

        if _LOGGING_CONFIGURED:
            logging.warning("日志系统已配置，忽略重复配置")
            return

        # 从环境变量获取配置（如果存在）
        env_log_file = os.environ.get(f"{env_prefix}_FILE")
        env_log_level = os.environ.get(f"{env_prefix}_LEVEL")
        env_console = os.environ.get(f"{env_prefix}_CONSOLE")

        # 使用环境变量覆盖参数
        final_log_file = env_log_file if env_log_file else log_file
        final_log_level = env_log_level.upper() if env_log_level else log_level
        final_console = env_console.lower() == 'true' if env_console else console_output

        # 转换日志级别
        if isinstance(final_log_level, str):
            level_name = final_log_level.upper()
            level_mapping = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            if level_name not in level_mapping:
                raise ValueError(f"无效的日志级别: {level_name}")
            final_log_level = level_mapping[level_name]

        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(final_log_level)

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # 创建格式化器
        formatter = logging.Formatter(format_str)

        # 控制台处理器
        if final_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(final_log_level)
            root_logger.addHandler(console_handler)

        # 文件处理器（如果提供日志文件路径）
        if final_log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(final_log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # 使用回滚文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                final_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(final_log_level)
            root_logger.addHandler(file_handler)

        _LOGGING_CONFIGURED = True
        root_logger.info(f"EasyLogger已配置完成，日志级别: {logging.getLevelName(final_log_level)}")
        if final_log_file:
            root_logger.info(f"日志文件: {final_log_file}")
        if final_console:
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


# 应用程序启动时自动配置基本日志
if not _LOGGING_CONFIGURED and os.environ.get("EASYLOG_AUTO_CONFIGURE", "true").lower() == "true":
    EasyLogger.configure()