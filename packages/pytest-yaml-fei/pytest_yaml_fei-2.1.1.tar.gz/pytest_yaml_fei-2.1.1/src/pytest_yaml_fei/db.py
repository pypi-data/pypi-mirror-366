import pymysql
from .log import log


class ConnectMysql(object):
    # 使用类变量存储连接池
    _connection_pool = {}

    def __init__(self, host, user, password, port, database):
        # 生成连接的唯一标识
        conn_key = f"{host}:{port}:{database}"

        try:
            # 检查连接池中是否已有此连接
            if conn_key in self._connection_pool:
                existing_conn = self._connection_pool[conn_key]
                try:
                    # 测试现有连接是否有效
                    existing_conn.ping(reconnect=True)
                    self.db = existing_conn
                    self.cursor = self.db.cursor()
                    return
                except:
                    # 连接失效，从连接池中移除
                    log.debug(f"Existing connection to {host}:{port}/{database} is dead, creating new one")
                    del self._connection_pool[conn_key]

            # 创建新连接
            new_connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port,
                database=database,
                cursorclass=pymysql.cursors.DictCursor,
            )
            # 测试新连接
            new_connection.ping()

            # 存入连接池并赋值给实例
            self._connection_pool[conn_key] = new_connection
            self.db = new_connection
            self.cursor = self.db.cursor()
            log.debug(f"mysql connect success to {host}:{port}/{database}!")
        except Exception as msg:
            self.cursor = None
            self.db = None
            log.error(f"mysql connect error to {host}:{port}/{database}: {msg}")

    def query_sql(self, sql, params=None, size=None):
        """
        执行查询SQL，支持参数化查询
        :param sql: SQL语句，可以包含 %s 占位符
        :param params: 要替换占位符的参数，可以是列表、元组或字典
        :param size: 返回的结果集大小，None表示返回全部，1表示返回一条，大于1表示返回指定数量
        :return: 查询结果
        """
        if not self.cursor:
            log.error("Database cursor is not initialized")
            return None

        try:
            # 记录SQL和参数
            if params:
                log.debug(f"Query SQL: {sql}, Parameters: {params}")
                self.cursor.execute(sql, params)
            else:
                log.debug(f"Query SQL: {sql}")
                self.cursor.execute(sql)

            # 根据size参数获取结果
            if size is None:
                result = self.cursor.fetchall()
                if len(result) == 1:
                    result = result[0]
                elif len(result) == 0:
                    result = None
            elif size == 1:
                result = self.cursor.fetchone()
            else:
                result = self.cursor.fetchmany(size)
                if not result:
                    result = None

            log.info(f"Query result: {result}")
            return result

        except Exception as msg:
            log.error(f"Query error: {msg}")
            return None

    def execute_sql(self, sql, params=None, commit=True):
        """
        执行更新SQL，支持参数化执行
        :param sql: SQL语句，可以包含 %s 占位符
        :param params: 要替换占位符的参数，可以是列表、元组或字典
        :param commit: 是否自动提交事务，默认为True
        :return: 影响的行数
        """
        if not self.cursor:
            log.error("Database cursor is not initialized")
            return 0

        try:
            # 记录SQL和参数
            if params:
                log.debug(f"Execute SQL: {sql}, Parameters: {params}")
                affected_rows = self.cursor.execute(sql, params)
            else:
                log.debug(f"Execute SQL: {sql}")
                affected_rows = self.cursor.execute(sql)

            if commit:
                self.db.commit()
                log.debug(f"Transaction committed, affected rows: {affected_rows}")

            return affected_rows

        except Exception as msg:
            log.error(f"Execute error: {msg}")
            if commit:
                log.info("Rolling back transaction")
                self.db.rollback()
            return 0

    def executemany_sql(self, sql, params_list):
        """
        批量执行SQL，支持参数化执行
        :param sql: SQL语句，可以包含 %s 占位符
        :param params_list: 参数列表，每个元素都是一组要替换的参数
        :return: 影响的行数
        """
        if not self.cursor:
            log.error("Database cursor is not initialized")
            return 0

        try:
            log.debug(f"Execute many SQL: {sql}, Parameters count: {len(params_list)}")
            affected_rows = self.cursor.executemany(sql, params_list)
            self.db.commit()
            log.debug(f"Batch execution completed, affected rows: {affected_rows}")
            return affected_rows

        except Exception as msg:
            log.error(f"Execute many error: {msg}")
            self.db.rollback()
            return 0

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.db.close()
            log.debug(f"close db!")

    @classmethod
    def close_all_connections(cls):
        for conn in cls._connection_pool.values():
            conn.close()
        cls._connection_pool.clear()
        log.debug("Closed all mysql connections in the pool")
