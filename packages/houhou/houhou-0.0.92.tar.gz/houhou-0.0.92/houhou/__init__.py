"""
EasyLogger - 简单易用的Python日志管理库

使用示例：
    from easylogger import get_logger, configure

    # 配置日志系统（可选）
    configure(log_file="app.log", log_level="DEBUG")

    # 获取日志器
    logger = get_logger(__name__)
    logger.info("Hello from EasyLogger!")

特性：
1. 自动配置：无需显式配置即可使用
2. 环境变量支持：通过环境变量配置日志
3. 文件回滚：自动管理日志文件大小
4. 线程安全：内置锁机制
5. 简单API：只需两个主要函数

环境变量：
- EASYLOG_FILE: 日志文件路径
- EASYLOG_LEVEL: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- EASYLOG_CONSOLE: 是否输出到控制台 (true/false)
- EASYLOG_AUTO_CONFIGURE: 是否自动配置 (true/false)
"""

from .logger_manager import EasyLogger as _EasyLogger

# 暴露主要API
configure = _EasyLogger.configure
get_logger = _EasyLogger.get_logger
set_log_level = _EasyLogger.set_log_level

# 为方便使用，创建一个默认日志器
logger = get_logger("easylogger")

# 版本信息
__version__ = "0.0.92"
__author__ = "hhh"
__license__ = "MIT"
