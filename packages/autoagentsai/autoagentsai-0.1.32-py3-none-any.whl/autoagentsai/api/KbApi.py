from typing import Optional, List, Dict
import requests
from ..types.KbTypes import KbQueryRequest, KbExtConfig


def create_kb_api(
    jwt_token: str,
    base_url: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    parent_id: Optional[int] = 0,
    avatar_url: Optional[str] = None,
    vector_model: Optional[str] = None,
    kb_type: Optional[str] = "kb",
    tags: Optional[List[str]] = None,
    ext_config: Optional[Dict] = None
) -> Dict[str, str]:
    """
    创建知识库 API

    Args:
        jwt_token (str): JWT 认证令牌
        base_url (str): API 服务基础地址
        name (str, optional): 知识库名称
        description (str, optional): 知识库描述
        parent_id (int, optional): 父文件夹ID，默认为0
        avatar_url (str, optional): 知识库头像URL
        vector_model (str, optional): 向量模型
        kb_type (str, optional): 知识库类型，"folder" 或 "kb"，默认为 "kb"
        tags (List[str], optional): 知识库标签列表
        ext_config (Dict, optional): 扩展配置

    Returns:
        Dict[str, str]: 包含知识库ID等信息的响应数据
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # 构建请求数据
    req_data = {
        "parentId": parent_id or 0,
        "name": name or "",
        "description": description or "",
        "avatarUrl": avatar_url or "",
        "vectorModel": vector_model or "",
        "type": kb_type or "kb",
        "tags": tags or [],
    }

    # 添加扩展配置
    if ext_config:
        req_data["ext"] = ext_config

    url = f"{base_url}/api/kb/create"
    response = requests.post(url, headers=headers, json=req_data, timeout=30)

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            # 直接返回响应数据，data字段包含知识库ID
            return response_data
        else:
            raise Exception(f"创建知识库失败: {response_data.get('msg', 'Unknown error')}")
    else:
        raise Exception(f"创建知识库失败: {response.status_code} - {response.text}")

def query_kb_list_api(
    jwt_token: str,
    base_url: str,
    page_num: int = 1,
    page_size: int = 10,
    count: bool = True,
    keywords: str = "",
    parent_id: int = 0,
    scope: int = 0,
    external_params: Optional[Dict] = None
) -> Dict[str, str]:
    """
    查询知识库列表 API

    Args:
        jwt_token (str): JWT 认证令牌
        base_url (str): API 服务基础地址
        page_num (int, optional): 页码，默认1
        page_size (int, optional): 每页大小，默认10
        count (bool, optional): 是否统计总数，默认True
        keywords (str, optional): 模糊查询关键词，默认为空
        parent_id (int, optional): 父文件夹ID，默认0
        scope (int, optional): 查询范围，默认0（全部）
        external_params (Dict, optional): 扩展查询条件

    Returns:
        Dict[str, str]: 分页查询结果
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    req = KbQueryRequest(
        pageNum=page_num,
        pageSize=page_size,
        count=count,
        keywords=keywords,
        parentId=parent_id,
        scope=scope,
        externalParams=external_params or {}
    )

    url = f"{base_url}/api/kb/query"
    response = requests.post(url, headers=headers, json=req.model_dump(), timeout=30)

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            return response_data
        else:
            raise Exception(f"查询知识库列表失败: {response_data.get('msg', 'Unknown error')}")
    else:
        raise Exception(f"查询知识库列表失败: {response.status_code} - {response.text}")


def modify_kb_api(
    jwt_token: str,
    base_url: str,
    kb_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    avatar_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    ext_config: Optional[Dict] = None
) -> Dict[str, str]:
    """
    修改知识库 API

    Args:
        jwt_token (str): JWT 认证令牌
        base_url (str): API 服务基础地址
        kb_id (int): 知识库ID
        name (str, optional): 新的知识库名称
        description (str, optional): 新的知识库描述
        avatar_url (str, optional): 新的头像URL
        tags (List[str], optional): 新的标签列表
        ext_config (Dict, optional): 新的扩展配置

    Returns:
        Dict[str, str]: 修改结果响应
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }


    # 构建请求数据，包含所有字段（即使是None或默认值）
    req_data = {
        "id": int(kb_id),
        "name": name,
        "description": description,
        "avatarUrl": avatar_url,
        "tags": tags if tags is not None else [],
        "ext": ext_config or KbExtConfig().model_dump()
    }

    url = f"{base_url}/api/kb/modify"

    # 添加调试信息
    print(f"🔍 调试信息:")
    print(f"   URL: {url}")
    print(f"   请求数据: {req_data}")

    response = requests.post(url, headers=headers, json=req_data, timeout=30)

    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.text}")

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            return response_data
        else:
            # 详细的错误信息
            error_msg = response_data.get('msg', 'Unknown error')
            error_code = response_data.get('code', 'Unknown code')
            raise Exception(f"修改知识库失败 - 错误码: {error_code}, 消息: {error_msg}, 完整响应: {response_data}")
    else:
        raise Exception(f"修改知识库失败: {response.status_code} - {response.text}")


def delete_kb_api(
    jwt_token: str,
    base_url: str,
    kb_id: int
) -> Dict[str, str]:
    """
    删除知识库 API

    Args:
        jwt_token (str): JWT 认证令牌
        base_url (str): API 服务基础地址
        kb_id (int): 知识库ID

    Returns:
        Dict[str, str]: 删除结果响应
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 确保ID是整数类型
    kb_id = int(kb_id)

    url = f"{base_url}/api/kb/{kb_id}"

    # 添加调试信息
    print(f"🔍 删除知识库调试信息:")
    print(f"   URL: {url}")
    print(f"   知识库ID: {kb_id} (类型: {type(kb_id)})")

    response = requests.delete(url, headers=headers, timeout=30)

    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.text}")

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            return response_data
        else:
            # 详细的错误信息
            error_msg = response_data.get('msg', 'Unknown error')
            error_code = response_data.get('code', 'Unknown code')
            raise Exception(f"删除知识库失败 - 错误码: {error_code}, 消息: {error_msg}, 完整响应: {response_data}")
    else:
        raise Exception(f"删除知识库失败: {response.status_code} - {response.text}")


def get_kb_detail_api(
    jwt_token: str,
    base_url: str,
    kb_id: int
) -> Dict[str, str]:
    """
    查询知识库详情 API

    Args:
        jwt_token (str): JWT 认证令牌
        base_url (str): API 服务基础地址
        kb_id (int): 知识库ID

    Returns:
        Dict[str, str]: 知识库详细信息
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 确保ID是整数类型
    kb_id = int(kb_id)

    url = f"{base_url}/api/kb/{kb_id}"

    # 添加调试信息
    print(f"🔍 查询知识库详情调试信息:")
    print(f"   URL: {url}")
    print(f"   知识库ID: {kb_id} (类型: {type(kb_id)})")

    response = requests.get(url, headers=headers, timeout=30)

    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.text}")

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("code") == 1:
            return response_data
        else:
            # 详细的错误信息
            error_msg = response_data.get('msg', 'Unknown error')
            error_code = response_data.get('code', 'Unknown code')
            raise Exception(f"查询知识库详情失败 - 错误码: {error_code}, 消息: {error_msg}, 完整响应: {response_data}")
    else:
        raise Exception(f"查询知识库详情失败: {response.status_code} - {response.text}")
