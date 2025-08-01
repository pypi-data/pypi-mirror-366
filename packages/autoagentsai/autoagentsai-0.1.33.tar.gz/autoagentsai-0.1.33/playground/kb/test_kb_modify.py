import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.client import KbClient


def example_basic_modify():
    """基础修改示例"""
    print("📝 基础修改示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    ext_config = {
        "configWay": None,
        "chunkSize": 5,
        "coverageRate": None,
        "similarity": None,
        "limit": None,
        "agentId": None,
        "language": None,
        "parserType": None,
        "contentEnhances": [],
        "search": None
    }

    # 修改知识库名称和描述
    result = kb_client.modify_kb(
        kb_id=3316,
        name="更新后的知识库名称",
        description="这是更新后的描述信息",
        ext_config=ext_config
    )
    
    if result.get("code") == 1:
        print("✅ 修改成功")
        print(f"消息: {result.get('msg')}")
    else:
        print("❌ 修改失败")


def example_modify_tags():
    """修改标签示例"""
    print("\n🏷️ 修改标签示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 更新标签列表
    new_tags = ["产品文档", "技术支持", "用户手册", "API文档"]
    
    result = kb_client.modify_kb(
        kb_id=123456,
        tags=new_tags
    )
    
    print(f"新标签: {new_tags}")
    print(f"修改结果: {result.get('msg')}")


def example_modify_avatar():
    """修改头像示例"""
    print("\n🖼️ 修改头像示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 更新头像URL
    new_avatar_url = "https://example.com/new-kb-avatar.png"
    
    result = kb_client.modify_kb(
        kb_id=123456,
        avatar_url=new_avatar_url
    )
    
    print(f"新头像: {new_avatar_url}")
    print(f"修改结果: {result.get('msg')}")


def example_modify_ext_config():
    """修改扩展配置示例"""
    print("\n🔧 修改扩展配置示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 更新扩展配置
    new_ext_config = {
        "configWay": "manual",
        "chunkSize": 800,
        "coverageRate": 0.85,
        "similarity": 0.75,
        "limit": 2500,
        "agentId": 12345,
        "language": "zh",
        "parserType": "auto",
        "contentEnhances": ["summary", "keyword", "ocr"],
        "search": {
            "vectorSimilarLimit": 0.8,
            "vectorSimilarWeight": 0.5,
            "topK": 8,
            "enableRerank": True,
            "rerankModelType": "bge-rerank-large",
            "rerankSimilarLimit": 0.9,
            "rerankTopK": 4
        }
    }
    
    result = kb_client.modify_kb(
        kb_id=123456,
        ext_config=new_ext_config
    )
    
    print("扩展配置已更新:")
    print(f"  分块大小: {new_ext_config['chunkSize']}")
    print(f"  相似度阈值: {new_ext_config['similarity']}")
    print(f"  搜索TopK: {new_ext_config['search']['topK']}")
    print(f"修改结果: {result.get('msg')}")


def example_comprehensive_modify():
    """综合修改示例"""
    print("\n🔄 综合修改示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 同时修改多个属性
    result = kb_client.modify_kb(
        kb_id=123456,
        name="企业知识管理系统",
        description="包含企业内部所有技术文档、流程规范和培训资料的综合知识库",
        avatar_url="https://company.com/kb-logo.png",
        tags=["企业知识库", "技术文档", "流程规范", "培训资料"],
        ext_config={
            "chunkSize": 600,
            "similarity": 0.8,
            "language": "zh",
            "search": {
                "topK": 5,
                "enableRerank": True
            }
        }
    )
    
    print("综合修改完成:")
    print(f"  新名称: 企业知识管理系统")
    print(f"  标签数量: 4个")
    print(f"  配置更新: 分块600, 相似度0.8")
    print(f"修改结果: {result.get('msg')}")


def example_partial_modify():
    """部分修改示例"""
    print("\n📝 部分修改示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 只修改描述
    result1 = kb_client.modify_kb(
        kb_id=123456,
        description="仅更新描述信息，其他属性保持不变"
    )
    print(f"仅修改描述: {result1.get('msg')}")
    
    # 只修改标签
    result2 = kb_client.modify_kb(
        kb_id=123456,
        tags=["新标签1", "新标签2"]
    )
    print(f"仅修改标签: {result2.get('msg')}")
    
    # 只修改部分扩展配置
    result3 = kb_client.modify_kb(
        kb_id=123456,
        ext_config={
            "chunkSize": 400,
            "search": {
                "topK": 3
            }
        }
    )
    print(f"仅修改部分配置: {result3.get('msg')}")


def example_batch_modify():
    """批量修改示例"""
    print("\n📦 批量修改示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 批量修改多个知识库
    kb_updates = [
        {
            "kb_id": 123456,
            "name": "产品文档库 v2.0",
            "tags": ["产品", "v2.0"]
        },
        {
            "kb_id": 123457,
            "name": "技术支持库 v2.0",
            "tags": ["技术支持", "v2.0"]
        },
        {
            "kb_id": 123458,
            "description": "更新后的培训资料库",
            "tags": ["培训", "更新"]
        }
    ]
    
    success_count = 0
    for update in kb_updates:
        try:
            result = kb_client.modify_kb(**update)
            if result.get("code") == 1:
                success_count += 1
                print(f"✅ 知识库 {update['kb_id']} 修改成功")
            else:
                print(f"❌ 知识库 {update['kb_id']} 修改失败")
        except Exception as e:
            print(f"❌ 知识库 {update['kb_id']} 修改异常: {str(e)}")
    
    print(f"批量修改完成: {success_count}/{len(kb_updates)} 成功")


def example_error_handling():
    """错误处理示例"""
    print("\n⚠️ 错误处理示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 处理参数错误
    try:
        result = kb_client.modify_kb(kb_id=123456)  # 没有提供任何修改参数
    except ValueError as e:
        print(f"参数错误: {str(e)}")
    
    # 处理API错误
    try:
        result = kb_client.modify_kb(
            kb_id=999999999,  # 不存在的知识库ID
            name="测试"
        )
    except Exception as e:
        print(f"API错误: {str(e)[:100]}...")
        
        # 根据错误类型进行处理
        if "404" in str(e):
            print("🔍 知识库不存在，请检查ID")
        elif "403" in str(e):
            print("🚫 权限不足，无法修改此知识库")
        elif "401" in str(e):
            print("🔑 认证失败，请检查API密钥")
        else:
            print("❓ 其他错误，请联系技术支持")


if __name__ == "__main__":
    print("🧪 知识库修改功能使用示例")
    print("=" * 60)
    
    print("⚠️ 注意：运行这些示例需要有效的API密钥")
    print("请将 'your_personal_auth_key' 和 'your_personal_auth_secret' 替换为实际的密钥")
    print("请将示例中的 kb_id 替换为实际的知识库ID")
    print()
    
    # 显示各种使用示例
    example_basic_modify()
    # example_modify_tags()
    # example_modify_avatar()
    # example_modify_ext_config()
    # example_comprehensive_modify()
    # example_partial_modify()
    # example_batch_modify()
    # example_error_handling()
    
    print("\n" + "=" * 60)
    print("📖 修改功能说明:")
    print("1. modify_kb() - 修改知识库信息，支持部分或全部属性更新")
    print("2. 支持修改: 名称、描述、头像、标签、扩展配置")
    print("3. 只有提供的参数会被更新，其他参数保持不变")
    print("4. 扩展配置的修改会影响后续的文档处理和搜索效果")
    print("5. 成功响应的code为1，失败时会抛出异常")