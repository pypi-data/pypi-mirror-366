import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client import KbClient


def example_basic_query():
    """基础查询示例"""
    print("📋 基础查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 查询所有知识库
    result = kb_client.query_kb_list()
    
    if result.get("code") == 1:
        data = result["data"]
        kb_list = data["list"]
        
        print(f"总共找到 {data['total']} 个知识库")
        print(f"当前第 {data['pageNum']} 页，共 {data['totalPage']} 页")
        
        for kb in kb_list:
            print(f"- {kb['name']} (ID: {kb['id']})")
            print(f"  类型: {kb['type']}, 数据量: {kb['dataAmount']}")


def example_keyword_search():
    """关键词搜索示例"""
    print("\n🔍 关键词搜索示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 搜索包含"产品"关键词的知识库
    result = kb_client.query_kb_list(
        keywords="产品",
        page_size=10
    )
    
    if result.get("code") == 0:
        kb_list = result["data"]["list"]
        print(f"找到 {len(kb_list)} 个包含'产品'的知识库:")
        
        for kb in kb_list:
            print(f"- {kb['name']}")
            print(f"  描述: {kb['description']}")


def example_scope_filter():
    """范围过滤示例"""
    print("\n🎯 范围过滤示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 只查询自己创建的知识库
    result = kb_client.query_kb_list(
        scope=1,  # 1=自己创建
        page_size=20
    )
    
    if result.get("code") == 0:
        kb_list = result["data"]["list"]
        print(f"我创建的知识库共 {len(kb_list)} 个:")
        
        for kb in kb_list:
            print(f"- {kb['name']} (作者: {kb['authorName']})")


def example_folder_query():
    """文件夹查询示例"""
    print("\n📁 文件夹查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 查询特定文件夹下的知识库
    folder_id = 123  # 替换为实际的文件夹ID
    
    result = kb_client.query_kb_list(
        parent_id=folder_id
    )
    
    if result.get("code") == 0:
        kb_list = result["data"]["list"]
        print(f"文件夹 {folder_id} 下有 {len(kb_list)} 个知识库:")
        
        for kb in kb_list:
            print(f"- {kb['name']} ({kb['type']})")


def example_pagination():
    """分页查询示例"""
    print("\n📄 分页查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    page_num = 1
    page_size = 5
    
    while True:
        result = kb_client.query_kb_list(
            page_num=page_num,
            page_size=page_size
        )
        
        if result.get("code") == 0:
            data = result["data"]
            kb_list = data["list"]
            
            if not kb_list:
                break
                
            print(f"第 {page_num} 页:")
            for kb in kb_list:
                print(f"  - {kb['name']}")
            
            # 检查是否还有下一页
            if page_num >= data["totalPage"]:
                break
                
            page_num += 1
        else:
            break


def example_content_search():
    """内容搜索示例"""
    print("\n🔍 内容搜索示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 首先获取一个知识库ID
    kb_list_result = kb_client.query_kb_list(page_size=1)
    
    if kb_list_result.get("code") == 0:
        kb_list = kb_list_result["data"]["list"]
        
        if kb_list:
            kb_id = str(kb_list[0]["id"])
            kb_name = kb_list[0]["name"]
            
            print(f"在知识库 '{kb_name}' 中搜索内容:")
            
            # 搜索知识库内容
            results = kb_client.query(
                kb_id=kb_id,
                query="如何使用",
                top_k=3,
                score_threshold=0.5
            )
            
            print(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                print(f"{i}. 相似度: {result.get('score', 0):.3f}")
                print(f"   内容: {result.get('content', '')[:100]}...")


def example_advanced_query():
    """高级查询示例"""
    print("\n🔧 高级查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 组合多个查询条件
    result = kb_client.query_kb_list(
        keywords="API",
        scope=1,  # 只查询自己创建的
        page_size=10,
        external_params={
            "custom_filter": "active_only"
        }
    )
    
    if result.get("code") == 0:
        data = result["data"]
        kb_list = data["list"]
        
        print(f"高级查询结果: {len(kb_list)} 个知识库")
        
        for kb in kb_list:
            print(f"- {kb['name']}")
            print(f"  状态: {kb.get('state', 'N/A')}")
            print(f"  权限: {kb.get('kbBtnPermission', [])}")
            
            # 显示扩展信息
            ext = kb.get('ext', {})
            if ext:
                print(f"  配置: 分块大小={ext.get('chunkSize', 'N/A')}")


if __name__ == "__main__":
    print("🧪 知识库查询功能使用示例")
    print("=" * 60)
    
    print("⚠️ 注意：运行这些示例需要有效的API密钥")
    print("请将 'your_personal_auth_key' 和 'your_personal_auth_secret' 替换为实际的密钥")
    print()
    
    # 显示各种使用示例
    example_basic_query()
    # example_keyword_search()
    # example_scope_filter()
    # example_folder_query()
    # example_pagination()
    # example_content_search()
    # example_advanced_query()
    
    print("\n" + "=" * 60)
    print("📖 查询功能说明:")
    print("1. query_kb_list() - 查询知识库列表，支持分页、关键词、范围过滤")
    print("2. query() - 搜索知识库内容，返回相关文档片段")
    print("3. 支持多种查询条件组合使用")
    print("4. 返回详细的知识库信息和权限设置")