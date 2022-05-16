from queue import Queue

from concurrent.futures import ThreadPoolExecutor
from loguru import logger

import msgacomm.log_util


class MQCenter(object):
    def __init__(self, topics=None, mq_type='subscriber', max_thread=None, queue_size=0):
        if topics is None:
            topics = ['default']

        self.topics = {}
        self.executer_thread = ThreadPoolExecutor(max_thread, thread_name_prefix='MSGA_MQ')
        self.create_topic(topics, queue_size, mq_type)
        self.group = {}
        self.state = 0

    def close(self):
        try:
            for topic in self.topics:
                self.topics[topic].put('CLOSE_QUEUE')

            self.topics.clear()
            self.group.clear()
            self.topics = None
            self.group = None
        except Exception as e:
            logger.error(e)
        try:
            self.executer_thread.shutdown()
        except Exception as e:
            logger.error(e)

    def create_topic(self, topics, queue_size=0, mq_type='subscriber'):
        for topic in topics:
            self.topics[str(topic)] = Queue(maxsize=queue_size)
            if mq_type == 'subscriber':
                self.executer_thread.submit(self._consumer, str(topic))

    def delete_topic(self, topic):
        if topic in self.topics:
            self.topics[topic].put('CLOSE_QUEUE')
            del self.topics[topic]

    def producer(self, data, topic='default'):
        if topic in self.topics:
            self.topics[topic].put(data)
        else:
            raise Exception('topic not find !')

    def subscriber(self, func, topic='default'):
        if topic in self.group:
            self.group[topic].append(func)
        else:
            self.group[topic] = [func]

    def consumer(self, topic):
        return self.topics[topic].get()

    def _consumer(self, topic=None):
        while self.state == 0:
            if topic in self.topics:
                try:
                    msg = self.topics[topic].get()
                    if msg == 'CLOSE_QUEUE':
                        return

                    for notify in self.group[topic]:
                        if notify is not None:
                            notify(topic, msg)
                except Exception as e:
                    logger.error(e)
            else:
                logger.error('topic not find !')

    def get_queue_size(self, topic):
        return self.topics[topic].qsize()


def get_msg(topic, msg):
    logger.info('aa' + msg)


def get_msg2(topic, msg):
    logger.info('bb' + msg)


if __name__ == '__main__':
    msgacomm.log_util.LogUtil.logger_load()

    mq = MQCenter(['DEMO'], mq_type='consumer')
    mq.producer('F1', 'DEMO')
    logger.info(mq.consumer('DEMO'))
    mq.producer('F1', 'DEMO')
    mq.producer('F1', 'DEMO')
    mq.producer('F1', 'DEMO')
    logger.info(mq.consumer('DEMO'))
    logger.info(mq.consumer('DEMO'))
    logger.info(mq.consumer('DEMO'))
    mq.create_topic(['DEMO1'])
    mq.subscriber(get_msg, 'DEMO1')
    mq.producer('F1', 'DEMO1')