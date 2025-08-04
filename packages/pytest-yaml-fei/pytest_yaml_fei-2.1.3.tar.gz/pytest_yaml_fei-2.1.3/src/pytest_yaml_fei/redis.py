import redis
from .log import log


class ConnectRedis(object):
    # 使用类变量存储连接池
    _connection_pool = {}

    def __init__(self, host, port=6379, db=0, password=None, decode_responses=True):
        # 生成连接的唯一标识
        conn_key = f"{host}:{port}:{db}"

        try:
            # 检查连接池中是否已有此连接
            if conn_key in self._connection_pool:
                existing_conn = self._connection_pool[conn_key]
                try:
                    # 测试现有连接是否有效
                    existing_conn.ping()
                    self.redis = existing_conn
                    return
                except:
                    # 连接失效，从连接池中移除
                    log.debug(f"Existing connection to {host}:{port}/{db} is dead, creating new one")
                    del self._connection_pool[conn_key]

            # 创建新连接
            new_connection = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses
            )
            # 测试新连接
            new_connection.ping()

            # 存入连接池并赋值给实例
            self._connection_pool[conn_key] = new_connection
            self.redis = new_connection
            log.debug(f"Redis connect success to {host}:{port}/{db}!")

        except Exception as msg:
            self.redis = None
            log.error(f"Redis connect error to {host}:{port}/{db}: {msg}")

    def get(self, key):
        """获取key的值"""
        if not self.redis:
            return None
        try:
            value = self.redis.get(key)
            log.debug(f"Redis get {key}: {value}")
            return value
        except Exception as msg:
            log.error(f"Redis get error: {msg}")
            return None

    def set(self, key, value, ex=None):
        """设置key的值"""
        if not self.redis:
            return False
        try:
            result = self.redis.set(key, value, ex=ex)
            log.debug(f"Redis set {key}: {value}, expire: {ex}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis set error: {msg}")
            return False

    def delete(self, key):
        """删除key"""
        if not self.redis:
            return False
        try:
            result = self.redis.delete(key)
            log.debug(f"Redis delete {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis delete error: {msg}")
            return False

    def exists(self, key):
        if not self.redis:
            return False
        try:
            result = self.redis.exists(key)
            log.debug(f"Redis exists {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis exists error: {msg}")
            return False

    def keys(self, pattern='*'):
        if not self.redis:
            return []
        try:
            result = self.redis.keys(pattern)
            log.debug(f"Redis keys {pattern}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis keys error: {msg}")
            return []

    def flushall(self):
        if not self.redis:
            return False
        try:
            result = self.redis.flushall()
            log.debug(f"Redis flushall, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis flushall error: {msg}")
            return False

    def ttl(self, key):
        if not self.redis:
            return -2
        try:
            result = self.redis.ttl(key)
            log.debug(f"Redis ttl {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis ttl error: {msg}")
            return -2

    def close(self):
        """关闭当前Redis连接"""
        if self.redis:
            try:
                self.redis.close()
            except Exception as e:
                log.error(f"Error closing current Redis connection: {e}")
            finally:
                self.redis = None

    @classmethod
    def close_all_connections(cls):
        for conn in cls._connection_pool.values():
            conn.close()
        cls._connection_pool.clear()
        log.debug("Closed all redis connections in the pool")
