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

    # create table
    supabase_client.create_table("""
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            description VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # insert data
    supabase_client.execute_query("""
        INSERT INTO agents (name, description) VALUES ('test', 'test');
    """)

    # select data
    result = supabase_client.execute_query("""
        SELECT * FROM agents;
    """)
    print(result)

if __name__ == "__main__":
    main()