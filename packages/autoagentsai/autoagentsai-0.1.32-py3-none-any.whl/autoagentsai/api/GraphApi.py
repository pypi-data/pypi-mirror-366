from copy import deepcopy
from typing import Dict, List, Any, Tuple, Optional, Union

import requests
from ..api.ChatApi import get_jwt_token_api
from ..types import CreateAppParams

def create_app_api(data: CreateAppParams, personal_auth_key: str, personal_auth_secret: str, base_url: str) -> requests.Response:
    jwt_token = get_jwt_token_api(personal_auth_key, personal_auth_secret, base_url)

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    url=f"{base_url}/api/agent/create"
    response = requests.post(url, json=data.model_dump(), headers=headers)
    # 判断请求结果
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            # 成功，返回接口响应内容（包含知识库ID等信息）
            print(f"《{data.name}》智能体创建成功，请在灵搭平台查看")
            return response_data
        else:
            raise Exception(f"创建智能体失败: {response_data.get('msg', 'Unknown error')}")
    else:
        raise Exception(f"创建智能体失败: {response.status_code} - {response.text}")

def merge_template_io(template_io: List[Dict[str, Any]], custom_io: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    合并模块字段配置，保留模板结构，用用户字段覆盖部分字段。
    """
    if not custom_io:
        return deepcopy(template_io)

    template_map = {item["key"]: deepcopy(item) for item in template_io}
    for c in custom_io:
        key = c.get("key")
        if key and key in template_map:
            template_map[key].update(c)

    return list(template_map.values())


def process_add_memory_variable(template_input: Dict[str, Any], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将用户提供的字段转换为多个“记忆变量”，每个基于模板生成。

    Args:
        template_input: 模板字段结构（完整字段定义）
        data: 用户提供的字段列表，每项包含至少 key，可能包含 label/valueType

    Returns:
        List of memory variable dicts
    """
    if not data:
        return []

    return [
        {
            **deepcopy(template_input),
            "key": item["key"],
            "label": item["key"],
            "valueType": item.get("valueType", "string")
        }
        for item in data if "key" in item
    ]


