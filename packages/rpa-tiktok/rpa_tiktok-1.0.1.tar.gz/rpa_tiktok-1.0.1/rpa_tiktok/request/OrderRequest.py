import json
from rpa_common import env
from rpa_common.library.request import request

class OrderRequest():
    def __init__(self):
        super().__init__()

    def saveOrderList(self, data):
        '''
        @Desc    : 保存订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v1/post?c=order&a=saveOrderList'
        res = request.post(url, data)
        return res