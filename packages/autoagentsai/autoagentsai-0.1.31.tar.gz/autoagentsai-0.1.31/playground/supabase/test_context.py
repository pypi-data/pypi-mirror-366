import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client import SupabaseClient

def main():
    supabase_client = SupabaseClient(
        supabase_url="your_url",
        supabase_anon_key="your_anon_key",
        supabase_service_key="your_service_key",
        user="your_user",
        password="your_password",
        host="your_host",
        port="your_port",
        dbname="your_dbname"
    )

    print("\n📋 测试create_table方法（使用with上下文管理器）...")
    # 测试创建表
    result = supabase_client.create_table("""
        CREATE TABLE IF NOT EXISTS test_agents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(200),
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    if result:
        print("✅ 表创建测试成功!")
    else:
        print("❌ 表创建测试失败!")

    print("\n📋 测试execute_query方法（插入数据）...")
    # 测试插入数据
    insert_result = supabase_client.execute_query(
        "INSERT INTO test_agents (name, description) VALUES (%s, %s)",
        ("测试Agent", "这是一个测试用的AI代理")
    )
    
    if insert_result:
        print("✅ 数据插入测试成功!")
        print(f"📊 影响行数: {insert_result.get('affected_rows', 0)}")
    else:
        print("❌ 数据插入测试失败!")

    print("\n📋 测试execute_query方法（查询数据）...")
    # 测试查询数据
    query_result = supabase_client.execute_query(
        "SELECT * FROM test_agents LIMIT 5"
    )
    
    if query_result:
        print("✅ 数据查询测试成功!")
        print(f"📊 列名: {query_result.get('columns', [])}")
        print(f"📊 数据行数: {len(query_result.get('data', []))}")
        for row in query_result.get('data', []):
            print(f"   {row}")
    else:
        print("❌ 数据查询测试失败!")

    print("\n🎉 所有测试完成!")

if __name__ == "__main__":
    main() 