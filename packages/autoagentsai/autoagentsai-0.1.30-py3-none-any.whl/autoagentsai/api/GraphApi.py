import requests
from ..api.ChatApi import get_jwt_token_api
from ..types import CreateAppParams

def create_app_api(data: CreateAppParams) -> requests.Response:
    base_url: str = "https://uat.agentspro.cn"
    jwt_token = get_jwt_token_api("135c9b6f7660456ba14a2818a311a80e", "i34ia5UpBnjuW42huwr97xTiFlIyeXc7",base_url)

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
            print("创建成功")
            return response_data
        else:
            raise Exception(f"创建智能体失败: {response_data.get('msg', 'Unknown error')}")
    else:
        raise Exception(f"创建智能体失败: {response.status_code} - {response.text}")