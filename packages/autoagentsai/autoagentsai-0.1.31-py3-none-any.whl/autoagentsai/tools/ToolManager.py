from typing import List, Dict, Any, Optional, Callable, Union
import json
import asyncio
import inspect
from ..utils.extractor import extract_json
from ..client.MCPClient import MCPClient


class ToolManager:
    """工具管理器，负责工具的标准化、选择和执行"""
    
    def __init__(self, chat_client, tools: List[Union[Dict[str, Any], Callable, 'ToolWrapper']]):
        self.chat_client = chat_client
        self.tools = self.normalize_tools(tools)
        
        # 初始化MCP客户端，从工具中提取服务器配置
        mcp_servers = {}
        for tool in self.tools:
            if tool.get('tool_type') == 'mcp' and 'server_config' in tool:
                server_name = tool.get('server_name', 'default')
                if server_name not in mcp_servers:
                    mcp_servers[server_name] = tool['server_config']
        
        self.mcp_client = MCPClient(mcp_servers) if mcp_servers else None
    
    def normalize_tools(self, tools: List[Union[Dict[str, Any], Callable, 'ToolWrapper']]) -> List[Dict[str, Any]]:
        """
        将混合的工具列表标准化为统一的字典格式
        支持：MCP工具字典、普通函数、ToolWrapper包装的函数
        """
        normalized_tools = []
        for tool in tools:
            if isinstance(tool, dict):
                # 已经是字典格式的工具（MCP工具）
                if 'server_name' in tool:
                    tool['tool_type'] = 'mcp'
                else:
                    tool['tool_type'] = 'unknown'
                normalized_tools.append(tool)
            elif callable(tool):
                # 普通的Python函数
                wrapped_tool = self.wrap_function(tool)
                normalized_tools.append(wrapped_tool)
            elif hasattr(tool, 'to_dict'):
                # ToolWrapper对象
                normalized_tools.append(tool.to_dict())
            else:
                print(f"⚠️ 跳过不支持的工具类型: {type(tool)}")
        
        return normalized_tools
    
    def wrap_function(self, func: Callable) -> Dict[str, Any]:
        """
        将Python函数包装为标准化的工具字典
        """
        # 检查是否有@tool装饰器的元数据
        tool_name = getattr(func, '_tool_name', None) or func.__name__
        tool_description = getattr(func, '_tool_description', None) or func.__doc__ or f"执行函数 {func.__name__}"
        
        # 获取函数签名
        try:
            sig = inspect.signature(func)
            parameters = {}
            
            for param_name, param in sig.parameters.items():
                param_info = {
                    "type": "string"  # 默认类型
                }
                
                # 尝试从类型注解获取类型信息
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_info["type"] = "integer"
                    elif param.annotation == float:
                        param_info["type"] = "number"
                    elif param.annotation == bool:
                        param_info["type"] = "boolean"
                    elif param.annotation == list:
                        param_info["type"] = "array"
                    # 其他保持默认的string
                
                parameters[param_name] = param_info
            
            input_schema = {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }
            
        except Exception as e:
            print(f"⚠️ 获取函数签名失败: {e}")
            input_schema = {"type": "object", "properties": {}}
        
        return {
            "name": tool_name,
            "description": tool_description,
            "inputSchema": input_schema,
            "tool_type": "function",
            "function": func  # 保存原始函数对象
        }
    
    async def select_tools(self, user_query: str) -> List[Dict[str, Any]]:
        """
        使用ChatClient智能选择相关的工具
        """
        if not self.tools:
            return []
        
        # 构建工具选择的提示
        tools_info = []
        for tool in self.tools:
            tool_info = {
                "name": tool["name"],
                "description": tool["description"],
                "tool_type": tool.get("tool_type", "unknown")
            }
            
            # 简化inputSchema显示
            if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                tool_info["parameters"] = list(tool["inputSchema"]["properties"].keys())
            
            tools_info.append(tool_info)
        
        system_prompt = f"""你是一个智能工具选择助手。用户会提出问题，你需要从可用工具中选择最相关的工具来帮助回答。

可用工具列表：
{json.dumps(tools_info, ensure_ascii=False, indent=2)}

请根据用户问题选择合适的工具，并为每个工具提供参数。如果不需要任何工具，返回空列表。

用户问题：{user_query}

请以JSON格式返回选择结果，格式如下：
{{
    "selected_tools": [
        {{
            "tool_name": "工具名称",
            "arguments": {{"参数名": "参数值"}},
            "reason": "选择这个工具的原因"
        }}
    ]
}}
"""
        
        response_generator = self.chat_client.invoke(system_prompt)
        # 处理生成器响应
        full_response = ""
        for event in response_generator:
            if event.get('type') == 'token':
                full_response += event.get('content', '')
            elif event.get('type') == 'finish':
                break
        
        # 解析ChatClient的响应
        try:
            # 使用工具方法提取JSON
            selection_result = extract_json(full_response)
            
            if selection_result:
                selected_tools = selection_result.get('selected_tools', [])
                
                # 打印工具选择结果
                if selected_tools:
                    print(f"🎯 AI选择了 {len(selected_tools)} 个工具:")
                    for i, tool_info in enumerate(selected_tools, 1):
                        print(f"   {i}. {tool_info.get('tool_name', 'unknown')}")
                        print(f"      理由: {tool_info.get('reason', '无')}")
                        print(f"      参数: {tool_info.get('arguments', {})}")
                    print()
                else:
                    print("🤷 AI未选择任何工具，将直接回答问题")
                    print()
                
                return selected_tools
            else:
                print("❌ 无法从ChatClient响应中提取有效的JSON")
                return []
        except Exception as e:
            print(f"❌ 解析ChatClient响应失败: {e}")
            return []
    
    async def execute_tools(self, selected_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行选定的工具
        """
        results = []
        
        for tool_info in selected_tools:
            try:
                tool_name = tool_info.get('tool_name')
                arguments = tool_info.get('arguments', {})
                reason = tool_info.get('reason', '')
                
                # 查找对应的工具配置
                tool_config = None
                for tool in self.tools:
                    if tool['name'] == tool_name:
                        tool_config = tool
                        break
                
                if not tool_config:
                    raise ValueError(f"未找到工具: {tool_name}")
                
                # 根据工具类型执行不同的调用逻辑
                tool_type = tool_config.get('tool_type', 'unknown')
                
                if tool_type == 'mcp':
                    # MCP工具调用
                    if not self.mcp_client:
                        raise ValueError("MCP客户端未初始化")
                    server_name = tool_config.get('server_name', 'default')
                    result = await self.mcp_client.call_tool(tool_name, server_name, arguments)
                elif tool_type == 'function':
                    # 自定义函数调用
                    result = await self.call_custom_function(tool_config, arguments)
                else:
                    raise ValueError(f"不支持的工具类型: {tool_type}")
                
                # 打印工具执行结果
                print(f"✅ 工具执行成功: {tool_name}")
                print(f"   工具类型: {tool_type}")
                print(f"   调用参数: {arguments}")
                print(f"   执行结果: {result}")
                print()
                
                results.append({
                    "tool": tool_name,
                    "tool_type": tool_type,
                    "reason": reason,
                    "arguments": arguments,
                    "result": result,
                    "status": "success"
                })
                
            except Exception as e:
                tool_name = tool_info.get('tool_name', 'unknown')
                print(f"❌ 工具执行失败: {tool_name}")
                print(f"   错误信息: {e}")
                print(f"   调用参数: {tool_info.get('arguments', {})}")
                print()
                
                results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "status": "error"
                })
        
        return results
    
    async def call_custom_function(self, tool_config: Dict[str, Any], arguments: Dict[str, Any]) -> Any:
        """
        调用自定义Python函数
        """
        func = tool_config.get('function')
        if not callable(func):
            raise ValueError("工具配置中没有可调用的函数")
        
        # 获取函数签名，匹配参数
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(**arguments)
            bound_args.apply_defaults()
            
            # 检查函数是否是异步的
            if asyncio.iscoroutinefunction(func):
                result = await func(**bound_args.arguments)
            else:
                result = func(**bound_args.arguments)
            
            return result
            
        except Exception as e:
            raise ValueError(f"调用函数失败: {e}")



# 工具包装器类，用于更灵活地定义自定义工具
class ToolWrapper:
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        """
        工具包装器
        
        Args:
            func: 要包装的函数
            name: 工具名称（如果不提供则使用函数名）
            description: 工具描述（如果不提供则使用函数文档）
        """
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or f"自定义工具: {self.name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为标准工具字典格式"""
        # 获取函数签名
        sig = inspect.signature(self.func)
        parameters = {}
        for param_name, param in sig.parameters.items():
            param_type = "string"  # 默认类型
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "number"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            parameters[param_name] = {
                "type": param_type,
                "description": f"参数 {param_name}"
            }
        
        return {
            "name": self.name,
            "description": self.description,
            "tool_type": "function",
            "function": self.func,
            "server_name": "local",
            "inputSchema": {
                "type": "object",
                "properties": parameters
            }
        }


# 便捷的装饰器函数
def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    装饰器，用于将函数标记为工具
    
    Args:
        name: 工具名称
        description: 工具描述
    
    Usage:
        @tool(name="加法计算器", description="计算两个数的和")
        def add(a: int, b: int) -> int:
            return a + b
    """
    def decorator(func: Callable) -> ToolWrapper:
        return ToolWrapper(func, name, description)
    return decorator
