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
            print(f"{data.name} 智能体创建成功，请在灵搭平台查看")
            return response_data
        else:
            raise Exception(f"创建智能体失败: {response_data.get('msg', 'Unknown error')}")
    else:
        raise Exception(f"创建智能体失败: {response.status_code} - {response.text}")