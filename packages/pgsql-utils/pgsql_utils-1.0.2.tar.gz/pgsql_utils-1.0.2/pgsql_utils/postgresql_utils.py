import os
import json
import logging
from typing import List, Dict, Any, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor
from colorPrintConsole import ColorPrint


class PostgreSQLUtils:
    """
    PostgreSQL数据库工具类

    提供简化的PostgreSQL数据库操作接口，包括连接管理、
    CRUD操作、批量操作等功能。
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        单例模式，确保全局只有一个数据库连接实例
        """
        if cls._instance is None:
            cls._instance = super(PostgreSQLUtils, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        host: str = None,
        database: str = None,
        user: str = None,
        password: str = None,
        port: int = None,
    ):
        """
        初始化PostgreSQL连接参数

        Args:
            host (str, optional): 数据库主机地址
            database (str, optional): 数据库名称
            user (str, optional): 用户名
            password (str, optional): 密码
            port (int, optional): 端口号
        """
        # 防止重复初始化
        if PostgreSQLUtils._initialized and not (
            host or database or user or password or port
        ):
            return

        # 如果提供了参数，则使用这些参数
        if host and database and user and password:
            self.host = host
            self.database = database
            self.user = user
            self.password = password
            self.port = port or 5432
        else:
            # 否则尝试从环境变量或配置文件读取
            self._load_config_from_env()

        self.connection = None
        self.cp = ColorPrint()  # 添加彩色打印实例
        self._sequence_cache = {}  # 序列缓存，避免重复检查
        self._sequence_cache_timeout = 60  # 缓存超时时间（秒）
        PostgreSQLUtils._initialized = True

    def _load_config_from_env(self):
        """
        从环境变量加载配置
        """
        self.host = os.getenv("PGSQL_IP", "localhost")
        self.database = os.getenv("PGSQL_DB", "postgres")
        self.user = os.getenv("PGSQL_USER_NAME", "postgres")
        self.password = os.getenv("PGSQL_USER_PASS", "")
        self.port = int(os.getenv("PGSQL_PORT", "5432"))

    def _load_config_from_file(self, config_file: str):
        """
        从配置文件加载配置

        Args:
            config_file (str): 配置文件路径
        """
        if config_file.endswith(".json"):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.host = config.get("host", "localhost")
                self.database = config.get("database", "postgres")
                self.user = config.get("user", "postgres")
                self.password = config.get("password", "")
                self.port = config.get("port", 5432)

    @classmethod
    def from_config_file(cls, config_file: str):
        """
        从配置文件创建实例

        Args:
            config_file (str): 配置文件路径

        Returns:
            PostgreSQLUtils: 数据库工具实例
        """
        instance = cls()
        instance._load_config_from_file(config_file)
        return instance

    @classmethod
    def from_settings(cls, settings_module):
        """
        从设置模块创建实例

        Args:
            settings_module: 设置模块对象

        Returns:
            PostgreSQLUtils: 数据库工具实例
        """
        instance = cls()
        instance.host = getattr(settings_module, "PGSQL_IP", "localhost")
        instance.database = getattr(settings_module, "PGSQL_DB", "postgres")
        instance.user = getattr(settings_module, "PGSQL_USER_NAME", "postgres")
        instance.password = getattr(settings_module, "PGSQL_USER_PASS", "")
        instance.port = getattr(settings_module, "PGSQL_PORT", 5432)
        return instance

    def connect(self) -> bool:
        """
        建立数据库连接

        Returns:
            bool: 连接是否成功
        """
        try:
            if self.connection and not self.connection.closed:
                return True

            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
            )

            return True
        except Exception as e:
            logging.error(f"数据库连接失败: {e}")
            return False

    def _reset_sequence_for_table(self, table_name: str, primary_key: str = "id"):
        """
        重置指定表的ID序列，确保序列值等于表中最大ID值（或0），防止主键冲突或ID跳跃

        Args:
            table_name (str): 表名
            primary_key (str, optional): 主键字段名，默认为"id"
        """
        try:
            cursor = self.connection.cursor()
            # 构造序列名（PostgreSQL默认序列命名规则）
            sequence_name = f"{table_name}_{primary_key}_seq"

            # 检查序列是否存在
            check_sequence_query = """
                                   SELECT EXISTS (SELECT 1
                                                  FROM information_schema.sequences
                                                  WHERE sequence_name = %s
                                                    AND sequence_schema = 'public') \
                                   """
            cursor.execute(check_sequence_query, (sequence_name,))
            sequence_exists = cursor.fetchone()[0]

            if sequence_exists:
                # 获取表最大ID值
                check_query = (
                    f"SELECT COALESCE(MAX({primary_key}), 0) FROM public.{table_name}"
                )
                cursor.execute(check_query)
                max_value = cursor.fetchone()[0]
                # 空表时，序列应设置为1且is_called=False，否则为max_value且is_called=True
                if max_value == 0:
                    setval_value = 1
                    is_called = False
                else:
                    setval_value = max_value
                    is_called = True
                query = f"SELECT setval(%s, %s, %s)"
                cursor.execute(query, (sequence_name, setval_value, is_called))
                self.connection.commit()
                # self.cp.green(f"{table_name}表{primary_key}序列已重置为{setval_value}")
            else:
                # 尝试使用更通用的序列名查找方式
                find_sequence_query = """
                    SELECT pg_get_serial_sequence(%s, %s)
                """
                cursor.execute(find_sequence_query, (table_name, primary_key))
                result = cursor.fetchone()
                if result and result[0]:
                    sequence_name = result[0].split(".")[-1]
                    check_query = f"SELECT COALESCE(MAX({primary_key}), 0) FROM public.{table_name}"
                    cursor.execute(check_query)
                    max_value = cursor.fetchone()[0]
                    if max_value == 0:
                        setval_value = 1
                        is_called = False
                    else:
                        setval_value = max_value
                        is_called = True
                    query = f"SELECT setval(%s, %s, %s)"
                    cursor.execute(query, (sequence_name, setval_value, is_called))
                    self.connection.commit()
                    # self.cp.green(f"{table_name}表{primary_key}序列已重置为{setval_value}")
            cursor.close()
        except Exception as e:
            self.cp.red(f"重置{table_name}表{primary_key}序列时出错: {e}")

    def reset_table_sequence(self, table_name: str, primary_key: str = "id"):
        """
        公共方法：重置指定表的序列

        Args:
            table_name (str): 表名
            primary_key (str, optional): 主键字段名，默认为"id"
        """
        if self.connect():
            self._reset_sequence_for_table(table_name, primary_key)

    def disconnect(self):
        """
        关闭数据库连接
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None

    def find(
        self, sql: str, to_json: bool = False, *args, **kwargs
    ) -> Union[List[Dict[str, Any]], List[tuple]]:
        """
        执行查询语句，类似于feapder中MysqlDB的find方法

        Args:
            sql (str): SQL查询语句
            to_json (bool, optional): 是否以JSON格式返回结果（字典列表）
            *args: 查询参数
            **kwargs: 查询参数

        Returns:
            Union[List[Dict[str, Any]], List[tuple]]: 查询结果列表
        """
        if not self.connect():
            return []

        try:
            if to_json:
                # 使用RealDictCursor返回字典格式结果
                cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            else:
                # 使用默认的Tuple格式结果
                cursor = self.connection.cursor()

            cursor.execute(sql, args or kwargs.get("params"))
            result = cursor.fetchall()
            cursor.close()

            if to_json and result:
                # 将RealDictRow对象转换为普通字典
                return [dict(row) for row in result]
            return result
        except Exception as e:
            logging.error(f"查询执行失败: {e}")
            return []

    def _process_data_for_insertion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理要插入的数据，将字典类型转换为JSON字符串

        Args:
            data (Dict[str, Any]): 原始数据字典

        Returns:
            Dict[str, Any]: 处理后的数据字典
        """
        processed_data = data.copy()
        for key, value in processed_data.items():
            if isinstance(value, dict):
                processed_data[key] = json.dumps(value, ensure_ascii=False)
        return processed_data

    def add(self, table: str, data: Dict[str, Any], **kwargs) -> bool:
        """
        插入数据，类似于feapder中MysqlDB的add方法

        Args:
            table (str): 表名
            data (Dict[str, Any]): 要插入的数据字典
            **kwargs: 其他参数

        Returns:
            bool: 插入是否成功
        """
        if not self.connect():
            return False

        # 重置表序列以防止主键冲突
        self._reset_sequence_for_table(table)

        # 处理字典类型的数据
        processed_data = self._process_data_for_insertion(data)

        try:
            cursor = self.connection.cursor()
            columns = ", ".join(processed_data.keys())
            placeholders = ", ".join(["%s"] * len(processed_data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(processed_data.values()))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(f"数据插入失败: {e}")
            self.connection.rollback()
            return False

    def add_batch(
        self,
        table: str,
        data_list: List[Dict[str, Any]],
        conflict_key: Union[str, List[str], None] = None,
        **kwargs,
    ) -> bool:
        """
        批量插入数据，支持冲突时更新（upsert），类似于feapder中MysqlDB的add_batch方法

        Args:
            table (str): 表名
            data_list (List[Dict[str, Any]]): 要插入的数据字典列表
            conflict_key (str|List[str]|None): 冲突键（唯一索引），遇到重复时更新
            **kwargs: 其他参数

        Returns:
            bool: 插入是否成功
        """
        if not data_list:
            return True

        if not self.connect():
            return False

        # 重置表序列以防止主键冲突
        self._reset_sequence_for_table(table)

        # 处理所有数据中的字典类型
        processed_data_list = [
            self._process_data_for_insertion(data) for data in data_list
        ]

        try:
            cursor = self.connection.cursor()
            columns = list(processed_data_list[0].keys())
            column_names = ", ".join([f'"{col}"' for col in columns])
            placeholders = ", ".join(["%s"] * len(columns))

            if conflict_key:
                # 构建ON CONFLICT更新部分
                if isinstance(conflict_key, list):
                    conflict_keys_str = ", ".join([f'"{key}"' for key in conflict_key])
                else:
                    conflict_keys_str = f'"{conflict_key}"'
                # 更新除冲突键外的所有字段
                update_parts = []
                for col in columns:
                    if (isinstance(conflict_key, list) and col not in conflict_key) or (
                        isinstance(conflict_key, str) and col != conflict_key
                    ):
                        update_parts.append(f'"{col}" = EXCLUDED."{col}"')
                update_clause = ", ".join(update_parts)
                query = f'INSERT INTO "{table}" ({column_names}) VALUES ({placeholders}) ON CONFLICT ({conflict_keys_str}) DO UPDATE SET {update_clause}'
            else:
                query = (
                    f'INSERT INTO "{table}" ({column_names}) VALUES ({placeholders})'
                )

            # 批量执行
            values_list = [list(data.values()) for data in processed_data_list]
            cursor.executemany(query, values_list)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(f"批量数据插入失败: {e}")
            self.connection.rollback()
            return False

    def add_smart(self, table: str, data: Dict[str, Any], **kwargs) -> bool:
        """
        智能插入数据，支持冲突时更新（upsert），类似于feapder中MysqlDB的add_smart方法

        Args:
            table (str): 表名
            data (Dict[str, Any]): 要插入或更新的数据字典
            primary_key (str, optional): 主键字段名，默认为"id"
            conflict_key (str|List[str]|None, optional): 冲突键（唯一索引），遇到重复时更新，默认为主键
            **kwargs: 其他参数

        Returns:
            bool: 操作是否成功
        """
        primary_key = kwargs.get("primary_key", "id")  # 默认主键为'id'
        conflict_key = kwargs.get("conflict_key", primary_key)  # 冲突键，默认为主键

        if not self.connect():
            return False

        # 重置表序列以防止主键冲突
        self._reset_sequence_for_table(table)

        # 处理字典类型的数据
        processed_data = self._process_data_for_insertion(data)

        try:
            cursor = self.connection.cursor()

            # 获取表的所有列名
            columns = list(processed_data.keys())

            # 构建INSERT语句
            column_names = ", ".join(['"{}"'.format(col) for col in columns])
            placeholders = ", ".join(["%s"] * len(columns))

            # 构建ON CONFLICT更新部分
            update_parts = []
            for column in columns:
                if column != primary_key:  # 主键不更新
                    update_parts.append('"{}" = EXCLUDED."{}"'.format(column, column))
            update_clause = ", ".join(update_parts)

            # 构建完整SQL语句，支持多个冲突键
            if isinstance(conflict_key, list):
                conflict_keys_str = ", ".join(
                    ['"{}"'.format(key) for key in conflict_key]
                )
                query = f"""
                    INSERT INTO "{table}" ({column_names}) 
                    VALUES ({placeholders}) 
                    ON CONFLICT ({conflict_keys_str}) 
                    DO UPDATE SET {update_clause}
                """
            else:
                query = f"""
                    INSERT INTO "{table}" ({column_names}) 
                    VALUES ({placeholders}) 
                    ON CONFLICT ("{conflict_key}") 
                    DO UPDATE SET {update_clause}
                """

            cursor.execute(query, list(processed_data.values()))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            # 使用彩色打印显示错误信息
            self.cp.red(f"数据插入或更新失败: {e}")
            self.cp.yellow(f"错误数据: {processed_data}")
            # logging.error(f"数据插入或更新失败: {e}")
            # logging.warning(f"错误数据: {processed_data}")
            self.connection.rollback()
            return False

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        condition_params: Optional[tuple] = None,
    ) -> int:
        """
        更新数据，类似于feapder中MysqlDB的update方法

        Args:
            table (str): 表名
            data (Dict[str, Any]): 要更新的数据字典
            condition (str): WHERE条件语句
            condition_params (Optional[tuple], optional): 条件参数

        Returns:
            int: 影响的行数
        """
        if not self.connect():
            return 0

        # 处理字典类型的数据
        processed_data = self._process_data_for_insertion(data)

        try:
            cursor = self.connection.cursor()

            # 构建SET子句
            set_parts = []
            values = []
            for key, value in processed_data.items():
                set_parts.append(f'"{key}" = %s')
                values.append(value)

            set_clause = ", ".join(set_parts)

            # 构建完整SQL语句
            query = f'UPDATE "{table}" SET {set_clause} WHERE {condition}'

            # 合并参数
            if condition_params:
                values.extend(condition_params)

            cursor.execute(query, values)
            rowcount = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return rowcount
        except Exception as e:
            logging.error(f"数据更新失败: {e}")
            self.connection.rollback()
            return 0

    def delete(
        self, table: str, condition: str, condition_params: Optional[tuple] = None
    ) -> int:
        """
        删除数据

        Args:
            table (str): 表名
            condition (str): WHERE条件语句
            condition_params (Optional[tuple], optional): 条件参数

        Returns:
            int: 影响的行数
        """
        if not self.connect():
            return 0

        try:
            cursor = self.connection.cursor()
            query = f'DELETE FROM "{table}" WHERE {condition}'
            cursor.execute(query, condition_params)
            rowcount = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return rowcount
        except Exception as e:
            logging.error(f"数据删除失败: {e}")
            self.connection.rollback()
            return 0

    def execute(self, sql: str, params: Optional[tuple] = None) -> bool:
        """
        执行SQL语句

        Args:
            sql (str): SQL语句
            params (Optional[tuple], optional): 参数

        Returns:
            bool: 执行是否成功
        """
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(f"SQL执行失败: {e}")
            self.connection.rollback()
            return False

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        执行查询语句

        Args:
            query (str): SQL查询语句
            params (Optional[tuple], optional): 查询参数

        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"查询执行失败: {e}")
            return []

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句

        Args:
            query (str): SQL更新语句
            params (Optional[tuple], optional): 更新参数

        Returns:
            int: 影响的行数
        """
        if not self.connect():
            return 0

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rowcount = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return rowcount
        except Exception as e:
            logging.error(f"更新执行失败: {e}")
            self.connection.rollback()
            return 0


# 全局实例，方便直接使用
db = PostgreSQLUtils()

# 使用示例
if __name__ == "__main__":
    pass
    # 方式1: 直接传参
    # db = PostgreSQLUtils("localhost", "shuchao", "postgres", "password", 5432)

    # 方式2: 从环境变量读取配置
    # db = PostgreSQLUtils()

    # 方式3: 从配置文件读取
    # db = PostgreSQLUtils.from_config_file("config.json")

    # 方式4: 从设置模块读取
    # import tradingview.setting as setting
    # db = PostgreSQLUtils.from_settings(setting)

    # 使用示例
    # 1. 查询数据
    # results = db.find("SELECT * FROM news_table WHERE category_id = %s", True, 1)
    # for result in results:
    #     print(result)

    # 2. 插入单条数据
    # data = {
    #     "title": "新闻标题",
    #     "content": "新闻内容",
    #     "publish_time": "2023-01-01 12:00:00"
    # }
    # db.add("news_table", data)

    # 3. 批量插入数据
    # data_list = [
    #     {"title": "新闻1", "content": "内容1"},
    #     {"title": "新闻2", "content": "内容2"}
    # ]
    # db.add_batch("news_table", data_list)

    # 4. 智能插入（冲突时更新）
    # data = {
    #     "id": 1,
    #     "title": "更新的标题",
    #     "content": "更新的内容"
    # }
    # db.add_smart("news_table", data)

    # 5. 更新数据
    # db.update("news_table", {"title": "新标题"}, "id = %s", (1,))

    # 6. 删除数据
    # db.delete("news_table", "id = %s", (1,))
