"""
工具调用格式详解演示

这个文件展示了AutoAgents系统中各种工具调用的格式和流程
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
from datetime import datetime
from src.autoagentsai.tools import ToolManager, ToolWrapper, tool

print("=" * 80)
print("🛠️  AutoAgents 工具调用格式详解")
print("=" * 80)

# ============= 1. 工具定义的格式 =============
print("\n📋 1. 工具定义的格式")
print("-" * 50)

print("🔹 方式一：使用 @tool 装饰器")
print("```python")
print("""@tool(name="加法计算器", description="计算两个数字的和")
def add(a: int, b: int) -> int:
    '''计算两个整数的和'''
    return a + b""")
print("```")

print("\n🔹 方式二：使用 ToolWrapper 包装")
print("```python")
print("""def multiply(x: float, y: float) -> float:
    '''计算两个数的乘积'''
    return x * y

wrapped_tool = ToolWrapper(multiply, "乘法计算器", "执行乘法运算")""")
print("```")

print("\n🔹 方式三：普通函数（自动推断）")
print("```python")
print("""def get_current_time() -> str:
    '''获取当前时间'''
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")""")
print("```")

print("\n🔹 方式四：MCP工具（字典格式）")
print("```python")
print("""{
    "name": "web_search",
    "description": "搜索网页内容",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer"}
        }
    },
    "tool_type": "mcp",
    "server_name": "search_server",
    "server_config": {...}
}""")
print("```")

# ============= 2. 标准化后的工具格式 =============
print("\n\n📐 2. 标准化后的工具格式（内部使用）")
print("-" * 50)

# 创建示例工具
@tool(name="加法计算器", description="计算两个数字的和")
def add(a: int, b: int) -> int:
    return a + b

def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 模拟ToolManager标准化过程
tools = [add, get_time]
dummy_chat_client = None  # 占位符

tool_manager = ToolManager(dummy_chat_client, tools)

print("标准化后的工具格式示例：")
for i, tool in enumerate(tool_manager.tools, 1):
    # 移除function对象以便展示
    display_tool = {k: v for k, v in tool.items() if k != 'function'}
    print(f"\n工具 {i}:")
    print(json.dumps(display_tool, ensure_ascii=False, indent=2))

# ============= 3. AI工具选择格式 =============
print("\n\n🤖 3. AI工具选择的JSON格式")
print("-" * 50)

print("当AI选择工具时，返回的JSON格式：")
selection_example = {
    "selected_tools": [
        {
            "tool_name": "加法计算器",
            "arguments": {"a": 15, "b": 25},
            "reason": "用户需要计算两个数字的和"
        },
        {
            "tool_name": "get_time",
            "arguments": {},
            "reason": "用户询问当前时间"
        }
    ]
}

print(json.dumps(selection_example, ensure_ascii=False, indent=2))

# ============= 4. 工具执行结果格式 =============
print("\n\n⚙️ 4. 工具执行结果格式")
print("-" * 50)

print("🔹 执行成功的结果格式：")
success_result = {
    "tool": "加法计算器",
    "tool_type": "function",
    "reason": "用户需要计算两个数字的和",
    "arguments": {"a": 15, "b": 25},
    "result": 40,
    "status": "success"
}
print(json.dumps(success_result, ensure_ascii=False, indent=2))

print("\n🔹 执行失败的结果格式：")
error_result = {
    "tool": "除法计算器",
    "error": "除数不能为零",
    "status": "error"
}
print(json.dumps(error_result, ensure_ascii=False, indent=2))

# ============= 5. 工具调用流程 =============
print("\n\n🔄 5. 完整的工具调用流程")
print("-" * 50)

workflow = """
1. 用户提出问题
   └─ "计算 15 + 25 的结果"

2. ToolManager.select_tools() - 智能选择工具
   ├─ 发送工具列表给ChatClient
   ├─ ChatClient返回JSON格式的工具选择
   └─ 解析得到: [{"tool_name": "加法计算器", "arguments": {"a": 15, "b": 25}, ...}]

3. ToolManager.execute_tools() - 执行选中的工具
   ├─ 根据tool_type分发到不同的执行器
   ├─ function类型 → _call_custom_function()
   ├─ mcp类型 → _call_mcp_tool()
   └─ 返回结果: [{"tool": "加法计算器", "result": 40, "status": "success"}]

4. create_react_agent.invoke() - 生成最终回答
   ├─ 将工具执行结果与原始问题组合
   ├─ 发送给ChatClient生成自然语言回答
   └─ 返回: "根据计算，15 + 25 = 40"
"""

print(workflow)

# ============= 6. 控制台输出格式 =============
print("\n\n📺 6. 控制台输出格式")
print("-" * 50)

console_output = """
🎯 AI选择了 1 个工具:
   1. 加法计算器
      理由: 用户需要计算两个数字的和
      参数: {'a': 15, 'b': 25}

✅ 工具执行成功: 加法计算器
   工具类型: function
   调用参数: {'a': 15, 'b': 25}
   执行结果: 40

🤖 基于工具结果生成最终回答...
"""

print("实际运行时的控制台输出格式：")
print(console_output)

# ============= 7. 参数类型映射 =============
print("\n\n🏷️ 7. Python类型到JSON Schema的映射")
print("-" * 50)

type_mapping = {
    "int": "integer",
    "float": "number", 
    "str": "string",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
    "其他": "string (默认)"
}

print("Python类型注解 → JSON Schema类型:")
for py_type, json_type in type_mapping.items():
    print(f"  {py_type:<10} → {json_type}")

print("\n" + "=" * 80)
print("✨ 总结：工具调用的核心格式")
print("=" * 80)

summary = """
📌 核心格式要点：

1. 工具定义：支持@tool装饰器、ToolWrapper、普通函数、MCP工具字典
2. 标准化格式：所有工具转换为统一的字典格式，包含name、description、inputSchema等
3. 选择格式：AI返回JSON，包含tool_name、arguments、reason
4. 执行格式：返回tool、result/error、status等字段
5. 类型系统：自动从Python类型注解推导JSON Schema类型
6. 错误处理：统一的错误格式和状态标识
7. 可视化：丰富的控制台输出，便于调试和监控

🎯 设计理念：统一接口，灵活扩展，智能选择，详细反馈
"""

print(summary)