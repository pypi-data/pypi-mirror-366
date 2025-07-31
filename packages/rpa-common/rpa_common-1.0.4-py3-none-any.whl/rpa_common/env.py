# eny.py
import os

class env:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get():
        rabbitmq = {
            'connector':'Amqp',
            'expire':60,
            'default':'default',
            'host':'192.168.1.20',
            'username':'admin',
            'password':'admin',
            'port':5672,
            'vhost':'/',
            'select':0,
            'timeout':0,
            'persistent':False,
        }

        data = {
            "api": "http://admin.rpa.zs.com",
            "version": "1.0.0",
            "rabbitmq": rabbitmq,
        }

        return data