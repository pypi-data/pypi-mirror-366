import json
from rpa_common import env
from rpa_common.library.request import request

class taskRequest():
    def __init__(self):
        super().__init__()

    @staticmethod
    def getTask(data):
        '''
        @Desc    : 获取任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("获取任务 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=task&a=getTaskInfo&zsit=debug'
        res = request.post(url, data)
        print("获取任务 end", res)
        return res

    @staticmethod
    def save(data):
        '''
        @Desc    : 保存数据
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("保存数据 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=data&a=storage&zsit=debug'
        res = request.post(url, data)
        print("保存数据 end", res)
        return res

    @staticmethod
    def end(data):
        '''
        @Desc    : 完成任务
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("完成任务 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=task&a=completeTask&zsit=debug'
        res = request.post(url, data)
        print("完成任务 end", res)
        return res

    @staticmethod
    def error(data):
        '''
        @Desc    : 任务失败
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("任务失败 strat")
        env_data = env.get()
        host = env_data['api']

        url = host + '/api/v2/index/post?c=task&a=failedTask&zsit=debug'
        res = request.post(url, data)
        print("任务失败 end", res)
        return res