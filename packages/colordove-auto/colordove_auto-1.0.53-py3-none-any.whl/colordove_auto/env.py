import os

# 通过环境变量获取当前环境，默认为 'production'
ENV = os.getenv("COLOR_DOVE_ENV", "development")

# 只支持三种环境
if ENV == "development":
    from config.development.server import servers
    from config.development.rabbitmq import rabbitmq
elif ENV == "test":
    from config.test.server import servers
    from config.test.rabbitmq import rabbitmq
elif ENV == "production":
    from config.production.server import servers
    from config.production.rabbitmq import rabbitmq
else:
    raise ValueError(f"不支持的环境变量: {ENV}，请设置为 'development', 'test' 或 'production'。")

config = {
    "api": servers['api'],
    "cdn": servers['cdn'],
    "version": "1.0.0",
    "rabbitmq": rabbitmq,
}

print(f"当前环境: {ENV}")