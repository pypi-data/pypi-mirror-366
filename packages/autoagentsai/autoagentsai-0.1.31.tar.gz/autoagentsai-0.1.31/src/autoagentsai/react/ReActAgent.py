from typing import List, Dict, Any, Callable, Union
from ..tools.ToolManager import ToolManager, ToolWrapper


class ReActAgent:
    def __init__(self, chat_client, tools: List[Union[Dict[str, Any], Callable, 'ToolWrapper']]):
        self.chat_client = chat_client
        self.tool_manager = ToolManager(chat_client, tools)

    async def ainvoke(self, prompt: str) -> str:
        """
        react agent的调用函数，处理用户查询，智能选择工具并生成回答
        """
        try:
            # 1. 使用ToolManager智能选择工具
            selected_tools = await self.tool_manager.select_tools(prompt)
            
            if not selected_tools:
                response_generator = self.chat_client.invoke(prompt)
                    # 处理生成器响应
                full_response = ""
                for event in response_generator:
                    if event.get('type') == 'token':
                        full_response += event.get('content', '')
                return full_response
            
            # 2. 使用ToolManager执行选中的工具
            tool_results = await self.tool_manager.execute_tools(selected_tools)
            
            # 3. 生成最终回答 - 拼接工具结果和原始问题
            print("🤖 基于工具结果生成最终回答...")
            
            # 构建包含工具执行结果的上下文
            context = f"""用户原始问题：{prompt}

以下是工具执行结果：
"""
            for result in tool_results:
                if result.get('status') == 'success':
                    context += f"""
工具：{result.get('tool', 'unknown')}
执行结果：{result.get('result', 'No result')}
"""
                else:
                    context += f"""
工具：{result.get('tool', 'unknown')}
执行失败：{result.get('error', 'Unknown error')}
"""
            
            context += f"\n请基于上述工具执行结果，详细回答用户的问题：{prompt}"
            
            # 调用ChatClient生成最终回答
            try:
                final_answer = await self.chat_client.invoke_async(context)
            except AttributeError:
                # 如果没有async方法，使用同步方法
                response_generator = self.chat_client.invoke(context)
                # 处理生成器响应
                final_answer = ""
                for event in response_generator:
                    if event.get('type') == 'token':
                        final_answer += event.get('content', '')
                    elif event.get('type') == 'finish':
                        break
            
            return final_answer
            
        except Exception as e:
            return f"处理查询时发生错误: {str(e)}"