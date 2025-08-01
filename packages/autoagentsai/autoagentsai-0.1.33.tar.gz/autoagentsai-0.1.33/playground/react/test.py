import asyncio
from src.autoagentsai.client import MCPClient, ChatClient
from src.autoagentsai.react import ReActAgent
from src.autoagentsai.tools import tool


async def main():
    # 1. 配置MCP服务器
    mcp_client = MCPClient({
        "your_mcp_server_name": {
            "transport": "streamable_http",
            "url": "your_url"
        }
    })

    @tool(name="计算器", description="数学计算")
    def calculate(a: int, b: int, op: str) -> float:
        if op == '+': return a + b
        elif op == '*': return a * b
        return 0

    mcp_tools = await mcp_client.get_tools() # 获取MCP工具

    # 2. 定义ChatClient
    chat_client = ChatClient(
        agent_id="your_agent_id",
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )

    # 3. 创建Agent
    agent = ReActAgent(
        chat_client=chat_client,
        tools=mcp_tools + [calculate]
    )

    result = await agent.invoke("计算 15 + 25, 并且搜索Python教程")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())