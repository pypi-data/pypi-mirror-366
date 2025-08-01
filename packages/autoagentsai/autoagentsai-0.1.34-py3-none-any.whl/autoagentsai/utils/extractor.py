import re
import json

def extract_json(text: str | None = None):
    """从AI响应中提取JSON内容，处理各种格式情况"""
    if not text:
        return None

    # 1. 先尝试提取```json```代码块中的JSON
    json_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # 2. 尝试提取纯JSON代码块（无语言标识）
    code_block_pattern = r'```\s*([\s\S]*?)\s*```'
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        potential_json = match.group(1).strip()
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            pass
    
    # 3. 尝试直接查找JSON对象（以{开头，以}结尾）
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    if json_start != -1 and json_end > json_start:
        potential_json = text[json_start:json_end]
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            pass

    return None

def extract_python_code(text: str | None = None):
    """从AI响应中提取Python代码"""
    if not text:
        return None

    python_pattern = r'```python\s*(.*?)\s*```'
    match = re.search(python_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_html(text: str | None = None):
    """从AI响应中提取HTML代码"""
    if not text:
        return None

    html_pattern = r'```html\s*(.*?)\s*```'
    match = re.search(html_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_react_code(text: str | None = None):
    """从AI响应中提取React代码"""
    if not text:
        return None

    patterns = [
        r'```react\s*\n?([\s\S]*?)\n?```',
        r'```tsx\s*\n?([\s\S]*?)\n?```',
        r'```jsx\s*\n?([\s\S]*?)\n?```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
            return code
    return None