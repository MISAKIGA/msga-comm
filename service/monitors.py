import os
import signal

import loguru
from loguru import logger

import msgacomm.log_util
from msgacomm import cache_property
from msgacomm.singleton import Singleton

__all__ = ["ParallelMonitor"]


class ParallelMonitor(object, metaclass=Singleton):
    """
    支持多线程多进程统一管理
    """
    alive = True
    name = "parallel_monitor"
    children = []
    int_signal_count = 1

    def __init__(self):
        self.open()
        super().__init__()

    @cache_property
    def logger(self) -> loguru.logger:
        return msgacomm.log_util.LogUtil.logger_load()

    def stop(self, sig=None, frame=None):
        if self.int_signal_count > 1:
            self.logger.info("Force to terminate...")
            for th in self.children[:]:
                self.stop_child(th)
            pid = os.getpid()
            os.kill(pid, 9)

        else:
            self.alive = False
            self.logger.info("Close process %s..." % self.name)
            self.int_signal_count += 1

    def open(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop_child(self, child):
        pass

