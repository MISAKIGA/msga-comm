import loguru

from .yidaili_network_agent import YiDaiLi

na_pool = YiDaiLi()


def load_ip(path, num=10):
    try:
        return na_pool.load_ips(num, from_file=True, file_path=path)
    except Exception as e:
        loguru.logger.error(e)
        return na_pool.load_ips(num)


def get_one_ip(type=0):
    if type == 0:
        data = na_pool.get_one_ip()
        ip = data[0] + ':' + data[1]
        return ip
    elif type == 1:
        data = na_pool.get_one_ip()
        return data[0], data[1]

    return na_pool.get_one_ip()


def close():
    na_pool.close()