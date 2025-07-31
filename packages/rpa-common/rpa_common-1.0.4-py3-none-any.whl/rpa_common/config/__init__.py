# __init__.py
import os

# 获取当前环境，默认为 development
ENV = os.getenv("COLOR_DOVE_ENV", "development")

# 根据当前环境加载配置
if ENV == "development":
    from .development import rabbitmq, server
elif ENV == "test":
    from .test import rabbitmq, server
elif ENV == "production":
    from .production import rabbitmq, server
else:
    raise ValueError(f"❌ 不支持的环境变量: {ENV}，请设置为 'development', 'test' 或 'production'。")
