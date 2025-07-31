from typing import Optional, List, Dict
from ..api.ChatApi import get_jwt_token_api
from ..api.KbApi import (
    create_kb_api, query_kb_list_api, modify_kb_api, delete_kb_api, get_kb_detail_api
)


class KbClient:
    def __init__(self, personal_auth_key: str, personal_auth_secret: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 知识库客户端

        用于与 AutoAgents AI 平台进行知识库管理的主要客户端类。
        支持知识库的创建、更新、删除，以及文档的上传、查询等功能。

        Args:
            personal_auth_key (str): 认证密钥
                - 获取方式：右上角 - 个人密钥

            personal_auth_secret (str): 认证密钥
                - 获取方式：右上角 - 个人密钥

            base_url (str, optional): API 服务基础地址
                - 默认值: "https://uat.agentspro.cn"
                - 测试环境: "https://uat.agentspro.cn"
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
        """
        self.jwt_token = get_jwt_token_api(personal_auth_key, personal_auth_secret, base_url)
        self.base_url = base_url

    def create_kb(
        self,
        name: str,
        description: str = "",
        parent_id: int = 0,
        avatar_url: Optional[str] = None,
        vector_model: Optional[str] = None,
        kb_type: str = "kb",
        tags: Optional[List[str]] = None,
        ext_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        创建知识库

        创建一个新的知识库，用于存储和管理文档、问答等知识内容。

        Args:
            name (str): 知识库名称
                - 必填参数，知识库的显示名称
                - 建议使用有意义的名称，便于管理和识别

            description (str, optional): 知识库描述
                - 可选参数，默认为空字符串
                - 用于描述知识库的用途、内容范围等
                - 有助于团队协作和知识库管理

            parent_id (int, optional): 父文件夹ID
                - 可选参数，默认为0（根目录）
                - 用于组织知识库的层级结构

            avatar_url (str, optional): 知识库头像URL
                - 可选参数，知识库的图标地址
                - 用于个性化显示

            vector_model (str, optional): 向量模型
                - 可选参数，指定使用的向量化模型
                - 影响文档的向量化和搜索效果

            kb_type (str, optional): 知识库类型
                - 可选参数，默认为 "kb"
                - 支持类型：
                  - "kb": 知识库类型
                  - "folder": 文件夹类型

            tags (List[str], optional): 知识库标签
                - 可选参数，用于分类和检索
                - 示例: ["技术文档", "产品手册"]

            ext_config (Dict, optional): 扩展配置
                - 可选参数，高级配置选项
                - 包含分块、搜索、重排序等配置

        Returns:
            Dict[str, str]: 创建结果信息
                - 包含新创建的知识库ID、状态等信息
                - 示例: {"kbId": "123456", "status": "success"}

        示例:
            Example 1: 创建基础知识库
            .. code-block:: python

                from autoagentsai.client import KbClient
                kb_client = KbClient(
                    personal_auth_key="your_personal_auth_key",
                    personal_auth_secret="your_personal_auth_secret"
                )
                result = kb_client.create_kb(
                    name="产品文档库",
                    description="存储产品相关的技术文档和用户手册"
                )
                print(f"知识库ID: {result['kbId']}")

            Example 2: 创建带标签的知识库
            .. code-block:: python

                result = kb_client.create_kb(
                    name="技术支持库",
                    description="技术支持相关文档",
                    tags=["技术支持", "FAQ"],
                    vector_model="text-embedding-ada-002"
                )

            Example 3: 创建高级配置的知识库
            .. code-block:: python

                ext_config = {
                    "chunkSize": 500,
                    "similarity": 0.75,
                    "search": {
                        "topK": 5,
                        "enableRerank": True
                    }
                }

                result = kb_client.create_kb(
                    name="高级知识库",
                    description="带有自定义配置的知识库",
                    ext_config=ext_config
                )

        注意:
            - 知识库名称在同一账户下应保持唯一性
            - 创建后可通过 update_kb() 方法修改名称和描述
            - 删除知识库会同时删除其中的所有文档，请谨慎操作
            - 扩展配置会影响文档处理和搜索效果
        """
        return create_kb_api(
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            name=name,
            description=description,
            parent_id=parent_id,
            avatar_url=avatar_url,
            vector_model=vector_model,
            kb_type=kb_type,
            tags=tags,
            ext_config=ext_config
        )

    def query_kb_list(
        self,
        page_num: int = 1,
        page_size: int = 10,
        count: bool = True,
        keywords: str = "",
        parent_id: int = 0,
        scope: int = 0,
        external_params: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        查询知识库列表

        分页查询知识库列表，支持关键词搜索、范围过滤等功能。

        Args:
            page_num (int, optional): 页码
                - 可选参数，默认为1
                - 从1开始计数

            page_size (int, optional): 每页大小
                - 可选参数，默认为10
                - 取值范围：1-100

            count (bool, optional): 是否统计总数
                - 可选参数，默认为True
                - 设置为False可提高查询性能

            keywords (str, optional): 模糊查询关键词
                - 可选参数，默认为空
                - 支持知识库名称和描述的模糊匹配

            parent_id (int, optional): 父文件夹ID
                - 可选参数，默认为0（根目录）
                - 用于查询特定文件夹下的知识库

            scope (int, optional): 查询范围
                - 可选参数，默认为0
                - 0=全部，1=自己创建，2=别人共享，3=自己创建待审核，4=别人共享待审核

            external_params (Dict, optional): 扩展查询条件
                - 可选参数，用于自定义查询条件

        Returns:
            Dict[str, str]: 分页查询结果
                - 包含完整的分页信息和知识库列表
                - 示例: {
                    "code": 0,
                    "msg": "",
                    "data": {
                        "pageNum": 1,
                        "pageSize": 10,
                        "total": 25,
                        "totalPage": 3,
                        "list": [...]
                    }
                  }

        示例:
            Example 1: 基础查询
            .. code-block:: python

                from autoagentsai.client import KbClient
                kb_client = KbClient(
                    personal_auth_key="your_personal_auth_key",
                    personal_auth_secret="your_personal_auth_secret"
                )
                result = kb_client.query_kb_list()
                kb_list = result['data']['list']
                for kb in kb_list:
                    print(f"知识库: {kb['name']} (ID: {kb['id']})")

            Example 2: 关键词搜索
            .. code-block:: python

                result = kb_client.query_kb_list(
                    keywords="产品",
                    page_size=20
                )

            Example 3: 查询特定文件夹
            .. code-block:: python

                result = kb_client.query_kb_list(
                    parent_id=123,
                    scope=1  # 只查询自己创建的
                )

        注意:
            - 返回结果按创建时间倒序排列
            - scope参数可以过滤不同权限的知识库
            - 支持多种查询条件组合使用
        """
        return query_kb_list_api(
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            page_num=page_num,
            page_size=page_size,
            count=count,
            keywords=keywords,
            parent_id=parent_id,
            scope=scope,
            external_params=external_params
        )

    def modify_kb(
        self,
        kb_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ext_config: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        修改知识库

        修改已存在的知识库信息，包括名称、描述、头像、标签和扩展配置等。

        Args:
            kb_id (int): 知识库ID
                - 必填参数，要修改的知识库唯一标识符

            name (str, optional): 新的知识库名称
                - 可选参数，如果提供则更新名称
                - 建议使用有意义的名称

            description (str, optional): 新的知识库描述
                - 可选参数，如果提供则更新描述
                - 可以设置为空字符串来清空描述

            avatar_url (str, optional): 新的头像URL
                - 可选参数，知识库的图标地址
                - 用于个性化显示

            tags (List[str], optional): 新的标签列表
                - 可选参数，用于分类和检索
                - 会完全替换现有标签

            ext_config (Dict, optional): 新的扩展配置
                - 可选参数，高级配置选项
                - 包含分块、搜索、重排序等配置
                - 会合并或替换现有配置

        Returns:
            Dict[str, str]: 修改结果信息
                - 包含修改操作的响应信息
                - 示例: {"code": 1, "msg": "修改成功", "data": ""}

        示例:
            Example 1: 修改知识库名称和描述
            .. code-block:: python

                from autoagentsai.client import KbClient
                kb_client = KbClient(
                    personal_auth_key="your_personal_auth_key",
                    personal_auth_secret="your_personal_auth_secret"
                )
                result = kb_client.modify_kb(
                    kb_id=123456,
                    name="新的知识库名称",
                    description="更新后的描述信息"
                )
                print(f"修改结果: {result['msg']}")

            Example 2: 更新标签
            .. code-block:: python

                result = kb_client.modify_kb(
                    kb_id=123456,
                    tags=["新标签1", "新标签2", "技术文档"]
                )

            Example 3: 修改扩展配置
            .. code-block:: python

                new_ext_config = {
                    "chunkSize": 600,
                    "similarity": 0.8,
                    "search": {
                        "topK": 10,
                        "enableRerank": True,
                        "rerankModelType": "bge-rerank"
                    }
                }

                result = kb_client.modify_kb(
                    kb_id=123456,
                    ext_config=new_ext_config
                )

        注意:
            - 至少需要提供一个要修改的参数
            - 只有提供的参数会被更新，其他参数保持不变
            - 修改操作不会影响知识库中的文档内容
            - 扩展配置的修改可能影响后续的文档处理和搜索效果
        """
        if all(param is None for param in [name, description, avatar_url, tags, ext_config]):
            raise ValueError("至少需要提供一个要修改的参数")

        return modify_kb_api(
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            kb_id=kb_id,
            name=name,
            description=description,
            avatar_url=avatar_url,
            tags=tags,
            ext_config=ext_config
        )

    def delete_kb(self, kb_id: int) -> Dict[str, str]:
        """
        删除知识库

        删除指定的知识库及其包含的所有文档。此操作不可逆，请谨慎使用。

        Args:
            kb_id (int): 知识库ID
                - 必填参数，要删除的知识库唯一标识符
                - 必须是整数类型

        Returns:
            Dict[str, str]: 删除结果信息
                - 包含删除操作的响应信息
                - 示例: {"code": 1, "msg": "删除成功", "data": ""}

        示例:
            Example 1: 删除知识库
            .. code-block:: python

                from autoagentsai.client import KbClient
                kb_client = KbClient(
                    personal_auth_key="your_personal_auth_key",
                    personal_auth_secret="your_personal_auth_secret"
                )
                result = kb_client.delete_kb(kb_id=123456)
                if result.get("code") == 1:
                    print("知识库删除成功")
                else:
                    print(f"删除失败: {result.get('msg')}")

            Example 2: 带错误处理的删除
            .. code-block:: python

                try:
                    result = kb_client.delete_kb(kb_id=123456)
                    print(f"删除成功: {result.get('msg')}")
                except Exception as e:
                    print(f"删除失败: {str(e)}")

        注意:
            - 删除知识库会同时删除其中的所有文档和数据
            - 此操作不可逆，删除后无法恢复
            - 只有具有删除权限的用户才能删除知识库
            - 建议在删除前先备份重要数据
            - 如果知识库正在被使用，可能无法删除
        """
        return delete_kb_api(
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            kb_id=kb_id
        )

    def get_kb_detail(self, kb_id: int) -> Dict[str, str]:
        """
        查询知识库详情

        通过知识库ID获取知识库的详细信息，包括完整的配置、权限、统计信息等。

        Args:
            kb_id (int): 知识库ID
                - 必填参数，知识库的唯一标识符
                - 必须是整数类型

        Returns:
            Dict[str, str]: 知识库详细信息
                - 包含知识库的完整信息
                - 示例: {
                    "code": 1,
                    "msg": "",
                    "data": {
                        "id": 123456,
                        "name": "产品文档库",
                        "description": "存储产品相关文档",
                        "type": "kb",
                        "state": 1,
                        "dataAmount": 150,
                        "tags": ["产品", "文档"],
                        "ext": {...},
                        "kbBtnPermission": ["edit", "delete"],
                        ...
                    }
                  }

        示例:
            Example 1: 获取知识库详情
            .. code-block:: python

                from autoagentsai.client import KbClient
                kb_client = KbClient(
                    personal_auth_key="your_personal_auth_key",
                    personal_auth_secret="your_personal_auth_secret"
                )
                result = kb_client.get_kb_detail(kb_id=123456)

                if result.get("code") == 1:
                    kb_info = result["data"]
                    print(f"知识库名称: {kb_info['name']}")
                    print(f"数据量: {kb_info['dataAmount']}")
                    print(f"权限: {kb_info['kbBtnPermission']}")
                else:
                    print(f"查询失败: {result.get('msg')}")

            Example 2: 检查知识库配置
            .. code-block:: python

                result = kb_client.get_kb_detail(kb_id=123456)

                if result.get("code") == 1:
                    kb_info = result["data"]
                    ext_config = kb_info.get("ext", {})

                    print(f"分块大小: {ext_config.get('chunkSize', 'N/A')}")
                    print(f"相似度阈值: {ext_config.get('similarity', 'N/A')}")

                    search_config = ext_config.get("search", {})
                    print(f"搜索TopK: {search_config.get('topK', 'N/A')}")
                    print(f"重排序: {search_config.get('enableRerank', False)}")

            Example 3: 检查权限
            .. code-block:: python

                result = kb_client.get_kb_detail(kb_id=123456)

                if result.get("code") == 1:
                    kb_info = result["data"]
                    permissions = kb_info.get("kbBtnPermission", [])

                    can_edit = "edit" in permissions
                    can_delete = "delete" in permissions

                    print(f"可编辑: {can_edit}")
                    print(f"可删除: {can_delete}")
                    print(f"作者: {kb_info.get('authorName', 'Unknown')}")

        注意:
            - 只能查询有访问权限的知识库
            - 返回的信息包含完整的配置和权限信息
            - 可用于权限检查和配置验证
            - 如果知识库不存在或无权限访问，会抛出异常
        """
        return get_kb_detail_api(
            jwt_token=self.jwt_token,
            base_url=self.base_url,
            kb_id=kb_id
        )