from .receive_code_yeziyun_agent import YeZiYunReceiveCode

ENUM = {
    'loop': {
        'filter': '1',
        'no_filter': '2'  # default
    }
    , 'operator': {
        'default': '0',
        'china_mobile': '1',
        'china_unicom': '2',
        'china_telecom': '3',
        'entity_card': '4',
        'virtual_card': '5',
    }
    , 'phone_num': {
        'phone_num': None
    }
    , 'scope_black': {
        'scope_black': None
    }
    , 'creat_time': {
        'creat_time': None
    }
}

yeziyun = YeZiYunReceiveCode()
