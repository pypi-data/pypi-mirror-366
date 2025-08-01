# PgSQL Utils

一个用于简化 PostgreSQL 数据库操作的 Python 工具包。

## 功能特点

- 单例模式数据库连接管理，支持全局实例 `db` 直接使用
- 支持多种配置方式（环境变量、配置文件、直接传参、模块设置）
- 自动主键序列重置，避免主键冲突（每个表仅首次插入/更新时自动重置）
- 支持字典类型字段自动转换为 JSON 字符串
- 提供多种便捷的数据操作方法：
  - `find`: 查询数据
  - `add`: 插入单条数据
  - `add_batch`: 批量插入数据，支持 upsert
  - `add_smart`: 智能插入（冲突时更新/upsert，支持多字段唯一约束）
  - `update`: 更新数据
  - `delete`: 删除数据
  - `execute`: 执行 SQL 语句
  - `execute_query`: 执行查询语句
  - `execute_update`: 执行更新语句
  - `reset_table_sequence`: 重置表主键序列
  - `disconnect`: 关闭数据库连接

## 安装

```bash
pip install pgsql-utils
```

如果安装失败，可以尝试使用以下方式安装：

```bash
pip install --index-url https://pypi.org/simple pgsql-utils -U
```

## 使用方法

1. ### 基本使用

   ```python
   from pgsql_utils import PostgreSQLUtils, db

   # 方式1: 直接传参
   db1 = PostgreSQLUtils("localhost", "mydb", "user", "password", 5432)

   # 方式2: 从环境变量读取配置
   # 需要设置环境变量: PGSQL_IP, PGSQL_DB, PGSQL_USER_NAME, PGSQL_USER_PASS, PGSQL_PORT
   db2 = PostgreSQLUtils()

   # 方式3: 从配置文件读取
   db3 = PostgreSQLUtils.from_config_file("config.json")

   # 方式4: 从设置模块读取
   import your_setting_module
   db4 = PostgreSQLUtils.from_settings(your_setting_module)

   # 方式5: 直接使用预定义的全局实例（推荐，需先配置环境变量或配置文件）
   from pgsql_utils import db
   ```

2. ### 查询数据

   ```python
   # 查询数据并以字典形式返回
   results = db.find("SELECT * FROM news_table WHERE category_id = %s", True, 1)
   for result in results:
       print(result)
   ```

3. ### 插入数据

   ```python
   # 插入单条数据
   data = {
       "title": "新闻标题",
       "content": "新闻内容",
       "publish_time": "2023-01-01 12:00:00",
   }
   db.add("news_table", data)
   
   # 批量插入数据
   data_list = [
       {"title": "新闻1", "content": "内容1"},
       {"title": "新闻2", "content": "内容2"},
   ]
   db.add_batch("news_table", data_list)
   
   # 批量 upsert（冲突时更新，conflict_key 支持单字段或多字段唯一约束）
   db.add_batch("news_table", data_list, conflict_key="title")
   db.add_batch("news_table", data_list, conflict_key=["title", "publish_time"])
   ```


4. ### 智能插入（重复则更新/upsert）

   - 支持主键或任意唯一索引冲突时自动更新。
   - `conflict_key` 支持字符串或字符串列表。
   - 可通过 `primary_key` 指定主键字段（默认 `id`）。

   ```python
   # 唯一索引是主键 id（默认）
   data = {"id": 1, "title": "更新的标题", "content": "更新的内容"}
   db.add_smart("news_table", data)

   # 唯一索引不是 id，是单个字段
   data = {"id": 1, "title": "更新的标题", "content": "更新的内容", "title_id": "248237"}
   db.add_smart("news_table", data, conflict_key="title_id")

   # 唯一索引是多个字段
   data = {
       "event_id": 248237,
       "event_time": "2025-07-30 21:45:00",
       "country": "CAD",
       "importance": 0,
       "event_content": "BoC货币政策报告",
       "data_source": "mql5",
       "locale": "zh_CN",
   }
   conflict_key = ["event_id", "data_source", "locale"]
   db.add_smart("event_table", data, conflict_key=conflict_key)
   ```

5. ### 更新和删除数据

   ```python
   # 更新数据
   db.update("news_table", {"title": "新标题"}, "id = %s", (1,))
   
   # 删除数据
   db.delete("news_table", "id = %s", (1,))
   ```

6. ### 重置表主键序列

   ```python
   # 重置表的主键序列（如有自增主键，建议在手动插入/删除后调用）
   db.reset_table_sequence("news_table")
   # 指定主键名
   db.reset_table_sequence("news_table", primary_key="custom_id")
   ```

7. ### 关闭数据库连接

   ```python
   db.disconnect()
   ```

## 配置

- ### 环境变量配置

  ```powershell
  # Windows 下设置环境变量（命令行窗口输入）
  set PGSQL_IP=localhost
  set PGSQL_DB=your_database
  set PGSQL_USER_NAME=your_username
  set PGSQL_USER_PASS=your_password
  set PGSQL_PORT=5432
  ```

  ```bash
  # Linux/macOS 下设置环境变量（终端输入）
  export PGSQL_IP=localhost
  export PGSQL_DB=your_database
  export PGSQL_USER_NAME=your_username
  export PGSQL_USER_PASS=your_password
  export PGSQL_PORT=5432
  ```

- ### JSON 配置文件示例

  ```json
  {
      "host": "localhost",
      "database": "your_database",
      "user": "your_username",
      "password": "your_password",
      "port": 5432
  }
  ```

- ### 设置模块文件示例

  ```python
  # PostgreSQL
  PGSQL_IP = "localhost"
  PGSQL_PORT = 5432
  PGSQL_DB = "your_database"
  PGSQL_USER_NAME = "your_username"
  PGSQL_USER_PASS = "your_password"
  ```

## 依赖

- psycopg2>=2.9.10
- colorPrintConsole>=1.0.7

## 许可证

Apache-2.0 License

