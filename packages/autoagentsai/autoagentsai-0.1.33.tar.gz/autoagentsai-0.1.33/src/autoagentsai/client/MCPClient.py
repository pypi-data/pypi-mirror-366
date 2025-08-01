import mcp
from mcp.client.streamable_http import streamablehttp_client
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class McpServerConfig:
    """MCP服务器配置"""
    transport: str  # "stdio" 或 "streamable_http"
    
    # streamable_http相关配置
    url: Optional[str] = None
    
    # stdio相关配置
    command: Optional[str] = None
    args: Optional[List[str]] = None
    


class MCPClient:
    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        """
        初始化MCP客户端
        
        Args:
            servers_config: 服务器配置字典，格式为:
            {
                "server_name": {
                    "transport": "streamable_http",
                    "url": "http://localhost:8000/mcp"
                },
                "another_server": {
                    "transport": "stdio", 
                    "command": "python",
                    "args": ["/path/to/server.py"]
                }
            }
        """
        self.servers_config = {}
        
        # 转换配置为McpServerConfig对象
        for name, config in servers_config.items():
            self.servers_config[name] = McpServerConfig(
                transport=config.get("transport"),
                command=config.get("command"),
                args=config.get("args"),
                url=config.get("url")
            )
    
    async def get_tools(self) -> List[Any]:
        """
        获取所有MCP服务器的工具列表
        
        Returns:
            List[Any]: 所有可用工具的列表
        """
        all_tools = []
        
        for server_name, config in self.servers_config.items():
            try:
                if config.transport == "streamable_http":
                    if not config.url:
                        raise ValueError(f"HTTP server {server_name} missing URL")
                    
                    print(f"连接到MCP服务器: {server_name} ({config.url})")

                    async with streamablehttp_client(config.url) as (read_stream, write_stream, _):
                        async with mcp.ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            tools_result = await session.list_tools()
                            
                            for tool in tools_result.tools:
                                tool_dict = {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "inputSchema": tool.inputSchema,
                                    "server_name": server_name,  # 添加服务器名称用于后续调用
                                    "server_config": config     # 添加服务器配置用于后续调用
                                }
                                all_tools.append(tool_dict)
                                
                elif config.transport == "stdio":
                    print(f"暂不支持stdio transport for server: {server_name}")
                    # TODO: 实现stdio连接
                    pass
                else:
                    print(f"不支持的transport类型: {config.transport} for server: {server_name}")
            except Exception as e:
                print(f"连接到服务器 {server_name} 失败: {e}")
                continue
        
        return all_tools

    async def call_tool(self, tool_name: str, server_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定服务器的工具
        
        Args:
            tool_name: 工具名称
            server_name: 服务器名称  
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        if server_name not in self.servers_config:
            raise ValueError(f"未找到服务器: {server_name}")
        
        config = self.servers_config[server_name]
        
        if config.transport == "streamable_http":
            if not config.url:
                raise ValueError("HTTP server missing URL")
            
            async with streamablehttp_client(config.url) as (read_stream, write_stream, _):
                async with mcp.ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result
                    
        elif config.transport == "stdio":
            raise NotImplementedError("stdio transport 暂未实现")
        else:
            raise ValueError(f"不支持的transport类型: {config.transport}")
