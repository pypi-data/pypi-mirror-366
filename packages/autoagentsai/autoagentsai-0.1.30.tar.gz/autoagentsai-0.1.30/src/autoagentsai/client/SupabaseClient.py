from typing import Optional
from supabase import create_client
from sqlalchemy import create_engine, text

class SupabaseClient:
    def __init__(self, supabase_url: str, supabase_anon_key: str, supabase_service_key: Optional[str] = None, 
                 user: str = "", password: str = "", host: str = "", port: int = 0, dbname: str = ""):
        self.supabase_url = supabase_url
        self.supabase_anon_key = supabase_anon_key
        self.supabase_service_key = supabase_service_key

        # 存储数据库连接参数
        self.db_config = {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'dbname': dbname
        }

        # 创建Supabase客户端
        self.supabase_client = create_client(self.supabase_url, self.supabase_anon_key)

        # 创建SQLAlchemy引擎
        self.engine = self._create_engine()

    def get_client(self):
        """获取Supabase客户端"""
        return self.supabase_client

    def _create_engine(self):
        """创建SQLAlchemy引擎"""
        DATABASE_URL = f"postgresql+psycopg2://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']}?sslmode=require"

        try:
            engine = create_engine(DATABASE_URL)
            print("✅ SQLAlchemy引擎创建成功!")
            return engine
        except Exception as e:
            print(f"❌ SQLAlchemy引擎创建失败: {e}")
            raise e

    def create_table(self, sql_ddl: str):
        """
        先连接到Supabase，然后执行SQL DDL语句创建表
        """
        print("🔗 正在连接到Supabase数据库...")

        try:
            with self.engine.connect() as connection:
                print("✅ 数据库连接成功!")

                print("🛠️ 正在执行SQL DDL语句...")
                # 执行SQL语句
                connection.execute(text(sql_ddl))
                connection.commit()

                print("✅ 表创建成功!")
                print("🔐 数据库连接已关闭")

                return True

        except Exception as e:
            print(f"❌ 创建表时发生错误: {e}")
            return False

    def execute_query(self, sql: str, params = None):
        """
        执行SQL查询语句
        支持tuple和dict两种参数格式
        """
        print("🔗 正在连接到Supabase数据库...")

        try:
            with self.engine.connect() as connection:
                print("✅ 数据库连接成功!")

                print("🔍 正在执行SQL查询...")

                # 处理参数格式
                if params:
                    if isinstance(params, tuple):
                        # 如果是tuple，转换SQL语句中的%s为:param0, :param1等格式
                        param_dict = {f'param{i}': val for i, val in enumerate(params)}
                        # 将%s替换为:param0, :param1等
                        formatted_sql = sql
                        for i in range(len(params)):
                            formatted_sql = formatted_sql.replace('%s', f':param{i}', 1)
                        result = connection.execute(text(formatted_sql), param_dict)
                    elif isinstance(params, dict):
                        # 如果是dict，直接使用
                        result = connection.execute(text(sql), params)
                    else:
                        raise ValueError("参数必须是tuple或dict类型")
                else:
                    result = connection.execute(text(sql))

                # 如果是SELECT语句，返回结果
                if sql.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    column_names = list(result.keys())
                    print(f"✅ 查询成功! 返回 {len(rows)} 行数据")
                    return {'columns': column_names, 'data': [list(row) for row in rows]}
                else:
                    # 对于INSERT/UPDATE/DELETE等语句
                    connection.commit()
                    affected_rows = result.rowcount
                    print(f"✅ 操作成功! 影响 {affected_rows} 行")
                    return {'affected_rows': affected_rows}

        except Exception as e:
            print(f"❌ 执行SQL时发生错误: {e}")
            return None

    def close(self):
        """关闭数据库引擎"""
        if self.engine:
            self.engine.dispose()
            print("🔐 数据库引擎已关闭")