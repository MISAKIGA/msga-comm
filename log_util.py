import os
import sys
from loguru import logger


class Log(object):
    def __init__(self):
        self.log_file_max_size = '100MB'
        self.err_log_file_max_size = '100MB'
        self.debug_log_file_max_size = '100MB'
        self.log_path = 'Log/my.log'
        self.err_log_path = 'Log/err.log'
        self.debug_log_path = 'Log/debug.log'
        self.encoding = 'utf-8'
        self.logger = logger

    def add_config(self, sink, **kwargs):
        self.logger.add(sink, **kwargs)

    def logger_load(self, folder=None):
        if folder is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            BASE_DIR = folder

        log_file_path = os.path.join(BASE_DIR, self.log_path)
        err_log_file_path = os.path.join(BASE_DIR, self.err_log_path)
        debug_log_file_path = os.path.join(BASE_DIR, self.debug_log_path)
        print('LOG PATH: ' + BASE_DIR)
        print('LOG PATH: ' + log_file_path)
        print('LOG PATH: ' + err_log_file_path)
        print('LOG PATH: ' + debug_log_file_path)

        # logger.add("file_1.log", rotation="500 MB", enqueue=True)  # 文件过大就会重新生成一个文件
        # logger.add("file_2.log", rotation="12:00")  # 每天12点创建新文件
        # logger.add("file_3.log", rotation="1 week")  # 文件时间过长就会创建新文件
        # logger.add("file_X.log", retention="10 days")  # 一段时间后会清空
        # logger.add("file_Y.log", compression="zip")  # 保存zip格式
        # logger.add("file.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
        self.add_config(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
        self.add_config(log_file_path, rotation=self.log_file_max_size, encoding=self.encoding, level='INFO')
        self.add_config(debug_log_file_path, rotation=self.err_log_file_max_size, encoding=self.encoding, level='DEBUG')
        self.add_config(err_log_file_path, rotation=self.debug_log_file_max_size, encoding=self.encoding, level='ERROR')

        return self.logger


LogUtil = Log()
