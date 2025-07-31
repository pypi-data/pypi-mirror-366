import json
from rpa_common import env
from rpa_common.library.request import request

class shopRequest():
    def __init__(self):
        super().__init__()

    @staticmethod
    def getDetail(data):
        '''
        @Desc    : 获取店铺详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=shop&a=getShopInfo&zsit=debug'
        res = request.post(url, data)
        return res

    @staticmethod
    def saveStorage(data):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存店铺缓存 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=shop&a=setShopStorage&zsit=debug'
        res = request.post(url, data)
        print("保存店铺缓存 end", res)
        return res

    @staticmethod
    def saveFingerprintLog(data):
        '''
        @Desc    : 保存店铺指纹记录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存店铺指纹记录 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=shop&a=saveFingerprint&zsit=debug'
        res = request.post(url, data)
        print("保存店铺指纹记录 end", res)
        return res