import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.client import KbClient


def example_basic_create():
    """基础创建示例"""
    print("📚 基础创建示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 最简单的创建方式
    result = kb_client.create_kb(
        name="我的第一个知识库",
        description="这是一个简单的知识库示例"
    )
    
    print(f"知识库创建成功，ID: {result['data']}")


def example_advanced_create():
    """高级配置创建示例"""
    print("\n🔧 高级配置示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 高级配置
    ext_config = {
        "configWay": "manual",           # 配置方式
        "chunkSize": 500,                # 分块大小
        "coverageRate": 0.8,             # 覆盖率
        "similarity": 0.75,              # 相似度阈值
        "limit": 2000,                   # 最大限制
        "language": "zh",                # 语言
        "parserType": "auto",            # 解析类型
        "contentEnhances": ["summary", "keyword", "ocr"],  # 内容增强
        "search": {                      # 搜索配置
            "vectorSimilarLimit": 0.85,
            "vectorSimilarWeight": 0.5,
            "topK": 5,
            "enableRerank": True,
            "rerankModelType": "bge-rerank",
            "rerankSimilarLimit": 0.9,
            "rerankTopK": 3
        }
    }
    
    result_kbId = kb_client.create_kb(
        name="高级配置知识库",
        description="包含完整配置的专业知识库",
        vector_model="text-embedding-ada-002",
        tags=["技术文档", "产品手册", "API文档"],
        ext_config=ext_config
    )
    
    print(f"高级知识库创建成功，ID: {result_kbId}")


def example_folder_management():
    """文件夹管理示例"""
    print("\n📁 文件夹管理示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 1. 创建根文件夹
    root_folder = kb_client.create_kb(
        name="项目文档",
        description="项目相关的所有文档",
        kb_type="folder"
    )
    root_folder_id = int(root_folder['data'])
    
    # 2. 在根文件夹下创建子文件夹
    tech_folder = kb_client.create_kb(
        name="技术文档",
        description="技术相关文档",
        parent_id=root_folder_id,
        kb_type="folder"
    )
    
    # 3. 在子文件夹下创建知识库
    api_kb = kb_client.create_kb(
        name="API文档库",
        description="API接口文档",
        parent_id=int(tech_folder['data']),
        kb_type="kb",
        tags=["API", "接口文档"]
    )
    
    print(f"文件夹结构创建完成:")
    print(f"  项目文档 (ID: {root_folder_id})")
    print(f"  └── 技术文档 (ID: {tech_folder['data']})")
    print(f"      └── API文档库 (ID: {api_kb['data']})")


def example_specialized_kb():
    """专业化知识库示例"""
    print("\n🎯 专业化知识库示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 客服知识库
    customer_service_config = {
        "chunkSize": 300,
        "similarity": 0.8,
        "language": "zh",
        "contentEnhances": ["summary", "keyword"],
        "search": {
            "topK": 3,
            "enableRerank": True,
            "rerankTopK": 2
        }
    }
    
    cs_kb = kb_client.create_kb(
        name="客服知识库",
        description="客户服务常见问题和解答",
        tags=["客服", "FAQ", "问答"],
        ext_config=customer_service_config
    )
    
    # 技术文档库
    tech_doc_config = {
        "chunkSize": 800,
        "similarity": 0.7,
        "language": "zh",
        "parserType": "markdown",
        "contentEnhances": ["summary", "code_highlight"],
        "search": {
            "topK": 5,
            "enableRerank": True,
            "rerankModelType": "bge-rerank"
        }
    }
    
    tech_kb = kb_client.create_kb(
        name="技术文档库",
        description="开发和运维技术文档",
        vector_model="text-embedding-ada-002",
        tags=["技术", "开发", "运维"],
        ext_config=tech_doc_config
    )
    
    print(f"客服知识库创建成功，ID: {cs_kb['kbId']}")
    print(f"技术文档库创建成功，ID: {tech_kb['kbId']}")


def example_backward_compatibility():
    """向后兼容示例"""
    print("\n🔄 向后兼容示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 使用旧版本的简化方法
    result = kb_client.create_kb_simple(
        kb_name="兼容性测试库",
        kb_description="测试向后兼容性的知识库"
    )
    
    print(f"兼容性知识库创建成功，ID: {result['kbId']}")
    print("✅ 旧版本代码无需修改即可使用")


def example_batch_create():
    """批量创建示例"""
    print("\n📦 批量创建示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 定义多个知识库配置
    kb_configs = [
        {
            "name": "产品手册库",
            "description": "产品使用手册和说明",
            "tags": ["产品", "手册"],
            "ext_config": {"chunkSize": 400, "similarity": 0.8}
        },
        {
            "name": "培训资料库",
            "description": "员工培训相关资料",
            "tags": ["培训", "HR"],
            "ext_config": {"chunkSize": 600, "similarity": 0.75}
        },
        {
            "name": "法律文档库",
            "description": "合同、协议等法律文档",
            "tags": ["法律", "合同"],
            "ext_config": {"chunkSize": 800, "similarity": 0.85}
        }
    ]
    
    created_kbs = []
    for config in kb_configs:
        try:
            result = kb_client.create_kb(**config)
            created_kbs.append(result)
            print(f"✅ {config['name']} 创建成功，ID: {result['kbId']}")
        except Exception as e:
            print(f"❌ {config['name']} 创建失败: {str(e)}")
    
    print(f"批量创建完成，成功创建 {len(created_kbs)} 个知识库")


def example_error_handling():
    """错误处理示例"""
    print("\n⚠️ 错误处理示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        # 尝试创建知识库
        result = kb_client.create_kb(
            name="测试知识库",
            description="错误处理测试"
        )
        print(f"知识库创建成功，ID: {result['kbId']}")
        
    except Exception as e:
        print(f"创建失败: {str(e)}")
        
        # 根据错误类型进行处理
        if "401" in str(e):
            print("🔑 认证失败，请检查API密钥")
        elif "403" in str(e):
            print("🚫 权限不足，请检查账户权限")
        elif "500" in str(e):
            print("🔧 服务器错误，请稍后重试")
        else:
            print("❓ 未知错误，请联系技术支持")


if __name__ == "__main__":
    print("🧪 新版知识库API使用示例")
    print("=" * 60)
    
    # 注意：这些示例需要有效的API密钥才能运行
    print("⚠️ 注意：运行这些示例需要有效的API密钥")
    print("请将 'your_personal_auth_key' 和 'your_personal_auth_secret' 替换为实际的密钥")
    print()
    
    # 显示各种使用示例
    # example_basic_create()
    # example_advanced_create()
    example_folder_management()
    # example_specialized_kb()
    # example_backward_compatibility()
    # example_batch_create()
    # example_error_handling()
    
    print("\n" + "=" * 60)
    print("📖 更多信息请参考官方文档")
    print("🔗 新版API支持更丰富的配置选项和更灵活的知识库管理")