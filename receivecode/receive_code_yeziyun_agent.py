from msgacomm.rest_agent import RestAgent
from loguru import logger
import json
import time


class YeZiYunReceiveCode(RestAgent):

    def __init__(self, username=None, password=None):
        RestAgent.__init__(self)
        # self.apiType = 'default'
        self.apiType = 'web'

        if self.apiType == 'web':
            self.apiUri = 'http://h5.do889.com:81'
        else:
            self.apiUri = 'http://api.sqhyw.net:81'
            # self.apiUri = 'http: // api.jinpaocun.net: 81 /'

        self.token = ''
        self.uriParam = {
            'loginUri': '/api/logins',
            'moneyUri': '/api/get_myinfo',
            'getMobile': '/api/get_mobile',
            'freeMobile': '/api/free_mobile',
            'addBlacklist': '/api/add_blacklist',
            'getJoin': '/api/get_join',
            'getProject': '/api/user_project_get',
            'getMessage': '/api/get_message',
            'getExpenditure': '/api/get_expenditure',
            'subJoin': '/api/sub_join'
        }
        self.residueCardNum = -1
        self.minResidueCardNum = 15

        if self.token is None:
            self.login(username, password)
        else:
            self.verifyToken(username, password)

    def get_message_loop(self, projectId, phone_num, timeout=300, **kwargs):
        r""" 轮询获取短信.

       :param
           projectId: 对接项目 ID
           **kwargs: 请求参数
       :returns
           成功: 响应信息; 失败: None
       """
        count = 0
        while True:
            if count >= timeout:
                return None

            try:
                ret = self.get_message(projectId, phone_num, **kwargs)
                if ret is not None:
                    return ret
            except Exception as e:
                if '手机卡被占用,请稍后再试' == str(e):
                    return None

            count += 1
            logger.debug('超时倒计时：{}', timeout - count)
            time.sleep(2)

    def get_expenditure(self, num, **kwargs):
        r""" 短信记录.

        :param
            num: 记录条数
        :returns 成功返回：记录
        失败：None
        """
        response = self.do_yeziyun_request('getExpenditure', 'POST', index=num, **kwargs)

        if self.is_succeess(response):
            return response
        return None

    def get_message(self, projectId, phone_num, **kwargs):
        r""" 获取短信.

        :param
            projectId: 对接项目 ID
            phone_num: 电话号码
            **kwargs: 请求参数
        :returns 成功返回：
        response 响应信息 {
            message:xx,
            code: 8888,
            data: [{ project_id:xxx, modle: xxx, phone: xxx, project_type: xxx }]
        }；
        失败：None
        """
        response = self.do_yeziyun_request('getMessage', 'POST', project_id=projectId, phone_num=phone_num, **kwargs)

        if self.is_succeess(response):
            # {'message': 'ok', 'code': '345899', '防止网络波动读不到短信多次提示次数': '4', 'data': [{
            # 'project_id': '157629',
            # 'modle': '【诺坊体】您的验证码为：345899，请勿泄露于他人！',
            # 'phone': '17151443218',
            # 'project_type': '1'
            # }]}
            return response
        elif self.ret_msg(response, '手机卡被占用,请稍后再试'):
            logger.debug('释放号码：{}, 状态：{}', phone_num, self.free_mobile(projectId, phone_num))
            logger.debug('手机卡被占用,请稍后再试')
            raise Exception('手机卡被占用,请稍后再试')

        return None

    def sub_join(self, key, **kwargs):
        r""" 重新对接.

        :param
            key: 对接码或专属 ID
            **kwargs: 请求参数
        :returns

        """
        response = self.do_yeziyun_request('subJoin', key_=key, **kwargs)
        return self.is_succeess(response)

    def get_project(self, **kwargs):
        response = self.do_yeziyun_request('getProject', 'POST', **kwargs)

        if self.is_succeess(response):
            return response['data']
        return None

    def get_join(self, **kwargs):
        r""" 获取对接.

        :param
            **kwargs: 请求参数
        :returns

        """

        if self.apiType == 'web':
            return self.get_project(**kwargs)

        response = self.do_yeziyun_request('getJoin', **kwargs)

        if self.is_succeess(response):
            return response['data']
        return None

    def add_blacklist(self, projectId, phone_num, **kwargs):
        r""" 添加号码黑名单.

        :param
            projectId: 对接项目 ID
            phone_num: 电话号码
            **kwargs: 请求参数
        :returns
            添加情况：True or False
        """
        response = self.do_yeziyun_request('addBlacklist', 'POST', project_id=projectId, phone_num=phone_num, **kwargs)
        return self.ret_msg(response, '拉黑成功')

    def free_mobile(self, projectId, phone_num, **kwargs):
        r""" 释放号码.

        :param
            projectId: 对接项目 ID
            phone_num: 电话号码
            **kwargs: 请求参数
        :returns
            添加情况：True or False
        """
        response = self.do_yeziyun_request('freeMobile', project_id=projectId, phone_num=phone_num, **kwargs)
        return self.is_succeess(response)

    def get_mobile(self, projectId, **kwargs):
        r""" 获取号码.

        :param
            projectId: 对接项目 ID
            **kwargs: 请求参数
        :returns
            成功: 手机号; 失败: None
        """
        if self.residueCardNum != -1 and self.minResidueCardNum >= self.residueCardNum:
            logger.error('超出取卡限制！')
            return None

        response = self.do_yeziyun_request('getMobile', 'POST', project_id=projectId, **kwargs)

        if self.is_succeess(response):
            self.residueCardNum = int(response['1分钟内剩余取卡数:'])
            logger.info('剩余取卡数：{}, 取卡限制：{}', self.residueCardNum, self.minResidueCardNum)

            return response['mobile']

        return None

    def get_money(self):
        r""" 获取号码.

        :returns
            成功: 余额; 失败: None
        """
        url = self.get_uri('moneyUri')
        if self.apiType == 'web':
            response = json.loads(self.do_request(url, self.get_uri_param(), method='GET', type='text'))
        else:
            response = json.loads(self.do_request(url, None, method='GET', type='text'))
        logger.debug('响应：{}', response)

        if self.is_succeess(response):
            return response['data'][0]['money']
        return None

    def login(self, username, password, **kwargs):
        r""" 获取号码.

        :returns
            成功: token; 失败: None
        """
        response = self.do_yeziyun_request('getMobile', 'POST', username=username, password=password, **kwargs)
        logger.info('登录信息：{}', response['message'])

        if self.is_succeess(response) and 'token' in response:
            self.token = response['token']
            logger.info('登录 token: {}', self.token)
            return self.token
        return None

    def get_uri(self, param):
        if self.apiType == 'web':
            return self.apiUri + self.uriParam[param]
        return self.apiUri + self.uriParam[param] + '?token=' + self.token

    def do_yeziyun_request(self, uriName, method='GET', **kwargs):
        url = self.get_uri(uriName)
        param = self.get_uri_param(**kwargs)
        logger.debug('请求参数：{}', str(param))

        response = json.loads(self.do_request(url, param=param, method=method, type='text'))
        logger.debug('响应：{}', response)

        return response

    def get_uri_param(self, removeSemicolon=False, **kwargs):
        param = {}
        if self.apiType == 'web':
            pStr = ''
            for key, value in kwargs.items():
                if value is None:
                    value = ''
                elif key is None:
                    key = ''
                pStr += str(key) + '=' + str(value) + ';'
            if removeSemicolon:
                pStr = pStr[:-1]
            return {
                'token': self.token + ';' + pStr
            }
        else:
            for key, value in kwargs.items():
                param[key] = value
            return param

    def is_succeess(self, response):
        if self.ret_msg(response, 'ok'):
            return True
        return False

    def ret_msg(self, response, msg):
        if 'message' in response and response['message'] == msg:
            return True
        return False

    def verifyToken(self, username, password):
        logger.debug('验证 Token')
        if self.get_money() is None:
            self.login(username, password)
