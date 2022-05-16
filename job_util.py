import time

from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


class Job(object):
    def __init__(self):
        # BlockingScheduler：适用于调度程序是进程中唯一运行的进程，调用start函数会阻塞当前线程，不能立即返回。
        # BackgroundScheduler：适用于调度程序在应用程序的后台运行，调用start后主线程不会阻塞。
        # AsyncIOScheduler：适用于使用了asyncio模块的应用程序。
        # GeventScheduler：适用于使用gevent模块的应用程序。
        # TwistedScheduler：适用于构建Twisted的应用程序。
        # QtScheduler：适用于构建Qt的应用程序。
        self.scheduler = BackgroundScheduler()

    def addJob(self, job_func, id=None, args=(), **kwargs):
        self.scheduler.add_job(job_func, 'cron', id=id, args=args, **kwargs)
        self.scheduler.start()
        logger.info('添加任务成功: {}', id)
        return id

    def removeJob(self, id):
        return self.scheduler.remove_job(id)

    def pauseJob(self, id):
        self.scheduler.pause_job(id)

    def resumeJob(self, id):
        self.scheduler.resume_job(id())

    def shutdown(self):
        self.scheduler.shutdown()


JobUtil = Job()


def test_args(x):
    print(f'{datetime.now():%H:%M:%S} Test cron job', x)


if __name__ == '__main__':
    JobUtil.addJob(test_args, 'AA', ('hello',), second='*/5')
    time.sleep(6)
    JobUtil.shutdown()
