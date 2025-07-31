import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
import math
from datetime import datetime
from src.autoagentsai.client import MCPClient, ChatClient
from src.autoagentsai.react.ReActAgent import ReActAgent, tool, ToolWrapper

# MCP服务器配置
mcp_servers_config = {
    "exa": {
        "transport": "streamable_http",
        "url": "https://server.smithery.ai/exa/mcp?api_key=5527ddac-6c10-419c-997a-c311a0115831&profileId=unchanged-whitefish-itZWkW"
    },
    "duckduckgo": {
        "transport": "streamable_http",
        "url": "https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?api_key=5527ddac-6c10-419c-997a-c311a0115831&profileId=unchanged-whitefish-itZWkW"
    }
}

# ChatClient配置
CHAT_CONFIG = {
    "agent_id": "7e46d18945fc49379063e3057a143c58",
    "personal_auth_key": "339859fa69934ea8b2b0ebd19d94d7f1",
    "personal_auth_secret": "93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
    "base_url": "https://uat.agentspro.cn"
}

# ============= 自定义工具函数 =============

# 方式1: 使用装饰器定义工具
@tool(name="加法计算器", description="计算两个数字的和")
def add(a: int, b: int) -> int:
    """计算两个整数的和"""
    return a + b

@tool(name="乘法计算器", description="计算两个数字的乘积")
def multiply(x: float, y: float) -> float:
    """计算两个数的乘积"""
    return x * y

@tool(name="平方根计算器", description="计算一个数的平方根")
def sqrt(number: float) -> float:
    """计算数字的平方根"""
    if number < 0:
        return float('nan')
    return math.sqrt(number)

# 方式2: 直接定义函数（不使用装饰器）
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def string_length(text: str) -> int:
    """计算字符串长度"""
    return len(text)

# 方式3: 使用ToolWrapper手动包装
def fibonacci(n: int) -> int:
    """计算斐波那契数列的第n项"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

fibonacci_tool = ToolWrapper(
    func=fibonacci,
    name="斐波那契计算器",
    description="计算斐波那契数列的第n项（从0开始）"
)

# 异步函数示例
async def async_delay_greeting(name: str, delay_seconds: int = 1) -> str:
    """异步问候函数，可以设置延迟"""
    await asyncio.sleep(delay_seconds)
    return f"你好，{name}！这是一个延迟了{delay_seconds}秒的问候。"

async def test_mixed_tools_agent():    
    try:
        chat_client = ChatClient(
            agent_id="7e46d18945fc49379063e3057a143c58",
            personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
            personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
            base_url="https://uat.agentspro.cn"
        )
        
        mcp_client = MCPClient(mcp_servers_config)
        mcp_tools = await mcp_client.get_tools()
        print(f"✅ 获取到 {len(mcp_tools)} 个MCP工具")
        
        # 3. 创建混合工具列表
        mixed_tools = [
            # MCP工具（从服务器获取）
            *mcp_tools,
            
            # 自定义函数（使用装饰器）
            add,
            multiply, 
            sqrt,
            
            # 直接传入函数
            get_current_time,
            string_length,
            
            # 使用ToolWrapper包装的函数
            fibonacci_tool,
            
            # 异步函数
            ToolWrapper(async_delay_greeting, "异步问候", "发送延迟问候消息")
        ]
        
        print(f"✅ 创建混合工具列表，总共 {len(mixed_tools)} 个工具")
        print(f"   - MCP工具: {len(mcp_tools)} 个")
        print(f"   - 自定义函数: {len(mixed_tools) - len(mcp_tools)} 个")
        
        # 4. 创建React Agent
        react_agent = ReActAgent(chat_client=chat_client, tools=mixed_tools)
        
        # 5. 测试不同类型的查询
        test_queries = [
            # "帮我计算 15 + 27 的结果",
            # "求 8 的平方根是多少",
            # "计算斐波那契数列的第10项",
            "现在是几点？",
            "字符串'Hello World'有多少个字符？",
            "请搜索一下人工智能的最新发展",
            "给我一个延迟2秒的问候，我的名字是张三",
            "帮我计算 3.14 乘以 2.5"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 测试查询 {i}: {query}")
            print("-" * 50)
            
            try:
                # 调用React Agent
                response = await react_agent.ainvoke(query)
                
                print("🤖 React Agent回答:")
                print(response)
                
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                import traceback
                traceback.print_exc()
            
            print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()



async def main():    
    try:
        await test_mixed_tools_agent() 
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 