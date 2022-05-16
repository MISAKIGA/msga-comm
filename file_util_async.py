import aiohttp
import aiofiles

from loguru import logger


class FileUtilAsync(object):
    def __init__(self, file_name=None):
        self.filename = file_name

    async def write(self, data):
        """
        写数据
        :param data:
        :return:
        """
        async with aiofiles.open(self.filename, 'w', encoding='utf-8')as fp:
            await fp.write(data)

    async def read(self):
        """
        异步读取数据
        :return:
        """
        async with aiofiles.open(self.filename, 'r', encoding='utf-8') as fp:
            content = await fp.read()
            return content

    @staticmethod
    async def get_file_async(self, url, folder, file_name):
        """
        Python3.5+
        安装 aiohttp aiofile
        异步下载文件
        :param self:
        :param url:
        :param folder:
        :param file_name:
        :return:
        """
        path = folder + file_name
        headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 '
                                 'Firefox/3.5.5'}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as r:
                async with aiofiles.open(path, 'wb') as afp:
                    result = await r.read()
                    await afp.write(result)
                    await afp.flush()
