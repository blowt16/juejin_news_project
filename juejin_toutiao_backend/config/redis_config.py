import redis.asyncio as redis


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST, # redis服务器主机地址
    port=REDIS_PORT, # redis端口号
    db=REDIS_DB, # redis数据库编号 0~15
    decode_responses=True # 将字节数据解码为字符串
)