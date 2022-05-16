import time

import msgacomm.log_util
from msgacomm.rest_agent import RestAgent
from msgacomm.queue_util import MQCenter
from msgacomm.file_util import FileUtil

import json
from loguru import logger


class YiDaiLi(RestAgent):
    def __init__(self, ip_num=10, filepath='F:\_WORKSPACE\Python_WorkSpace\Learn\SuperModel\yidaili\ip_file.txt'):
        RestAgent.__init__(self)
        self.fu = FileUtil()
        self.uri = 'http://api1.ydaili.cn/tools/MeasureApi.ashx'
        self.topic_name = 'IP_POOL'
        self.mq = MQCenter([self.topic_name], mq_type='consumer')
        self.mq.create_topic(['SAVE_QUEUE'])
        self.mq.subscriber(self.save_file, 'SAVE_QUEUE')
        self.ip_num = ip_num
        self.sf = open(filepath, 'a')

    def close(self):
        time.sleep(2)
        self.mq.close()
        try:
            self.sf.flush()
            self.sf.close()
        except Exception as e:
            logger.error(e)
        logger.debug('关闭资源')

    def save_file(self, topic, msg):
        line = ''
        for d in msg:
            if d is None:
                d = ''
            line += str(d) + ','

        self.sf.write(line[:-1] + '\n')
        self.sf.flush()

    def join_url(self, num, fStr='json'):
        return self.uri + '?action=EAPI&secret=B2838A3030F8C14884D254F83DDA65E59EECE6512F8FA52109FCD5119A5EBC2561E0C62D4BBF2F8E&number=' + str(
            num) + '&orderId=SH20220515012801005_test&format=' + fStr

    def load_ips(self, ip_num=None, from_file=False, file_path=None):
        if from_file and file_path is not None:
            return self.load_ips_from_file(file_path, ip_num)
        else:
            return self.load_ips_from_request(ip_num)

    def load_ips_from_file(self, path, ip_num):
        lines = self.fu.get_lines(path)
        ips = []
        for line in lines:
            ip_str = line.split(',')
            address = ip_str[0]
            port = ip_str[1]
            isp = ip_str[2]
            if address is None:
                address = ''
            if port is None:
                port = ''
            if isp is None:
                isp = ''
            ips.append((address, port, isp))
            self.mq.producer((address, port, isp), self.topic_name)

        if len(ips) <= 0:
            return self.load_ips_from_request(ip_num)

        return ips

    def load_ips_from_request(self, ip_num):
        if ip_num is None:
            ip_num = self.ip_num
        resp = json.loads(self.do_request(self.join_url(ip_num), param=None, method='GET', type='text'))

        if 'status' in resp and resp['status'] == 'success':
            num = resp['number']
            logger.info('获取 {}, 剩余代理数量：{}', ip_num, num)
            ip_data = resp['data']
            logger.debug('IP_DATA: {}', ip_data)
            ips = []
            for data in ip_data:
                i = data['IP'].split(':')
                ip = (i[0], i[1], data['ISP'])
                ips.append(ip)
                self.mq.producer(ip, self.topic_name)
                self.mq.producer(ip, 'SAVE_QUEUE')

            return num, ips

        return None

    def get_one_ip(self):
        # if self.mq.get_queue_size(self.topic_name) <= 0:
            # self.load_ips(self.ip_num)

        oIP = self.mq.consumer(self.topic_name)
        return oIP


if __name__ == '__main__':
    msgacomm.log_util.LogUtil.logger_load()
    yidali = YiDaiLi()
    yidali.load_ips(from_file=True, file_path='F:\\_WORKSPACE\\Python_WorkSpace\\Learn\\SuperModel\\yidaili\\ip_file.txt')
    ip = yidali.get_one_ip()
    ip1 = yidali.get_one_ip()
    # yidali.load_ips(10)
    logger.info('GET ONE {}', ip)
    time.sleep(1)
    yidali.close()
