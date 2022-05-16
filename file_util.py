import os
import asyncio
import tempfile
import linecache

from loguru import logger
from requests import Request
from urllib.request import urlopen


class FileUtil(object):
    def __init__(self):
        self.path = ''

    @staticmethod
    def mkdir(path):
        """判断文件夹是否存在，不存在就创建"""
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def is_file(path: str, extension: list):
        """
        判断路径是否是文件，且该文件格式是否存在于集合中
        :param path: 文件路径
        :param extension: 文件后缀集合
        :return: boolean
        """
        return os.path.isfile(path) and path.rsplit('.', 1)[1] in extension

    @staticmethod
    def get_path():
        """获取当前文件所处的路径"""
        path = os.getcwd()
        return path

    @staticmethod
    def load_setting_from_obj(obj: object):
        """
        读取对象中所有自定义的属性，保存在一个字典中并返回
        :param obj:对象
        :return: attrs,保存了对象所有自定义属性的字典
        """
        attrs = {key: values for key, values in obj.__dict__.items() if not key.startswith('__')}
        return attrs

    @staticmethod
    def write_file(file_name, data):
        with open(file_name, 'wt') as f:
            f.write(data)
        return file_name


    @staticmethod
    def read_lines(file_name):
        with open(file_name, 'r') as f:
            return f.readlines()

    @staticmethod
    def make_tempfile(data):
        fd, temp_file_name = tempfile.mkstemp()
        os.close(fd)
        with open(temp_file_name, 'wt') as f:
            f.write(data)
        return temp_file_name

    @staticmethod
    def get_line(file_name, line_no):
        return linecache.getline(file_name, line_no)

    @staticmethod
    def get_lines(file_name):
        return linecache.getlines(file_name)

    @staticmethod
    def cleanup(filename):
        os.unlink(filename)
        linecache.clearcache()

    @staticmethod
    def read_step(self, future, n, total):
        res = self.fd.read(n)
        if res is None:
            self.loop.call_soon(self.read_step, future, n, total)
            return
        if not res:  # EOF
            future.set_result(bytes(self.rbuffer))
            return
        self.rbuffer.extend(res)
        self.loop.call_soon(self.read_step, future, self.BLOCK_SIZE, total)

    @staticmethod
    def read(self, n=-1):
        future = asyncio.Future(loop=self.loop)

        self.rbuffer.clear()
        self.loop.call_soon(self.read_step, future, min(self.BLOCK_SIZE, n), n)

        return future

    @staticmethod
    def get_file(url, file_name, folder):
        """
        下载文件
        :param url:
        :param file_name:
        :param folder:
        :return:
        """
        path = folder+file_name
        req = Request(
            url=url, headers={
                'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 '
                              'Firefox/3.5.5'
            }
        )
        u = urlopen(req)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if os.path.exists(path):
            logger.info('file exist')
            return
        with open(path, 'wb') as f:
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
        logger.info(file_name+' file download success')



if __name__ == '__main__':
    fu = FileUtil()
    line = fu.read_lines('F:\_WORKSPACE\Python_WorkSpace\Learn\SuperModel\yidaili\ip_file.txt')
    line2 = fu.get_lines('F:\_WORKSPACE\Python_WorkSpace\Learn\SuperModel\yidaili\ip_file.txt')
    print(line)
    print(line2)