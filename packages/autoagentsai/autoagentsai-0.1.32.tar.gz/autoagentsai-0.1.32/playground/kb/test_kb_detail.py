import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.client import KbClient

def example_basic_detail():
    """基础详情查询示例"""
    print("📋 基础详情查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 查询知识库详情
    try:
        result = kb_client.get_kb_detail(kb_id=3318)
        
        if result.get("code") == 1:
            kb_info = result["data"]
            
            print("✅ 查询成功")
            print(f"知识库名称: {kb_info['name']}")
            print(f"描述: {kb_info.get('description', 'N/A')}")
            print(f"类型: {kb_info['type']}")
            print(f"状态: {kb_info['state']} (1=启用, 2=禁用)")
            print(f"数据量: {kb_info['dataAmount']}")
            print(f"作者: {kb_info.get('authorName', 'Unknown')}")
            print(f"标签: {kb_info.get('tags', [])}")
            
        else:
            print(f"❌ 查询失败: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ 查询异常: {str(e)}")


def example_check_permissions():
    """权限检查示例"""
    print("\n🔐 权限检查示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        result = kb_client.get_kb_detail(kb_id=123456)
        
        if result.get("code") == 1:
            kb_info = result["data"]
            permissions = kb_info.get("kbBtnPermission", [])
            
            print(f"知识库: {kb_info['name']}")
            print(f"权限列表: {permissions}")
            
            # 检查具体权限
            can_edit = "edit" in permissions
            can_delete = "delete" in permissions
            can_view = True  # 能查询到详情说明有查看权限
            
            print(f"\n权限检查结果:")
            print(f"  可查看: {can_view}")
            print(f"  可编辑: {can_edit}")
            print(f"  可删除: {can_delete}")
            
            # 根据权限执行不同操作
            if can_edit:
                print("✅ 可以修改此知识库")
            else:
                print("❌ 无法修改此知识库")
                
            if can_delete:
                print("✅ 可以删除此知识库")
            else:
                print("❌ 无法删除此知识库")
                
    except Exception as e:
        print(f"❌ 权限检查失败: {str(e)}")


def example_analyze_config():
    """配置分析示例"""
    print("\n🔧 配置分析示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        result = kb_client.get_kb_detail(kb_id=123456)
        
        if result.get("code") == 1:
            kb_info = result["data"]
            ext_config = kb_info.get("ext", {})
            
            print(f"知识库: {kb_info['name']}")
            print(f"向量模型: {kb_info.get('vectorModel', 'N/A')}")
            
            if ext_config:
                print(f"\n📊 基础配置:")
                print(f"  配置方式: {ext_config.get('configWay', 'N/A')}")
                print(f"  分块大小: {ext_config.get('chunkSize', 'N/A')}")
                print(f"  覆盖率: {ext_config.get('coverageRate', 'N/A')}")
                print(f"  相似度阈值: {ext_config.get('similarity', 'N/A')}")
                print(f"  限制条数: {ext_config.get('limit', 'N/A')}")
                print(f"  语言: {ext_config.get('language', 'N/A')}")
                print(f"  解析器: {ext_config.get('parserType', 'N/A')}")
                print(f"  内容增强: {ext_config.get('contentEnhances', [])}")
                
                search_config = ext_config.get("search", {})
                if search_config:
                    print(f"\n🔍 搜索配置:")
                    print(f"  向量相似度限制: {search_config.get('vectorSimilarLimit', 'N/A')}")
                    print(f"  向量权重: {search_config.get('vectorSimilarWeight', 'N/A')}")
                    print(f"  TopK: {search_config.get('topK', 'N/A')}")
                    print(f"  启用重排序: {search_config.get('enableRerank', False)}")
                    print(f"  重排序模型: {search_config.get('rerankModelType', 'N/A')}")
                    print(f"  重排序TopK: {search_config.get('rerankTopK', 'N/A')}")
            else:
                print("⚠️ 没有扩展配置信息")
                
    except Exception as e:
        print(f"❌ 配置分析失败: {str(e)}")


def example_batch_detail_query():
    """批量详情查询示例"""
    print("\n📦 批量详情查询示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 要查询的知识库ID列表
    kb_ids = [123456, 123457, 123458]
    
    kb_details = []
    
    for kb_id in kb_ids:
        try:
            print(f"\n查询知识库 {kb_id}...")
            result = kb_client.get_kb_detail(kb_id=kb_id)
            
            if result.get("code") == 1:
                kb_info = result["data"]
                kb_details.append(kb_info)
                
                print(f"✅ {kb_info['name']}")
                print(f"   数据量: {kb_info['dataAmount']}")
                print(f"   状态: {kb_info['state']}")
                
            else:
                print(f"❌ 查询失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 查询异常: {str(e)}")
    
    # 汇总分析
    if kb_details:
        print(f"\n📊 批量查询汇总:")
        print(f"  成功查询: {len(kb_details)} 个知识库")
        
        total_data = sum(kb.get('dataAmount', 0) for kb in kb_details)
        active_count = sum(1 for kb in kb_details if kb.get('state') == 1)
        
        print(f"  总数据量: {total_data}")
        print(f"  启用状态: {active_count}/{len(kb_details)}")


def example_conditional_analysis():
    """条件分析示例"""
    print("\n🎯 条件分析示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        # 先获取知识库列表
        kb_list_result = kb_client.query_kb_list(page_size=10)
        
        if kb_list_result.get("code") == 0:
            kb_list = kb_list_result["data"]["list"]
            
            print(f"分析 {len(kb_list)} 个知识库:")
            
            # 分类统计
            categories = {
                "large_kb": [],      # 大型知识库 (数据量 > 100)
                "empty_kb": [],      # 空知识库 (数据量 = 0)
                "editable_kb": [],   # 可编辑知识库
                "folder_type": []    # 文件夹类型
            }
            
            for kb_summary in kb_list:
                kb_id = kb_summary["id"]
                
                try:
                    # 获取详细信息
                    result = kb_client.get_kb_detail(kb_id=kb_id)
                    
                    if result.get("code") == 1:
                        kb_detail = result["data"]
                        
                        # 分类
                        data_amount = kb_detail.get("dataAmount", 0)
                        kb_type = kb_detail.get("type", "")
                        permissions = kb_detail.get("kbBtnPermission", [])
                        
                        if data_amount > 100:
                            categories["large_kb"].append(kb_detail)
                        if data_amount == 0:
                            categories["empty_kb"].append(kb_detail)
                        if "edit" in permissions:
                            categories["editable_kb"].append(kb_detail)
                        if kb_type == "folder":
                            categories["folder_type"].append(kb_detail)
                            
                except Exception as e:
                    print(f"❌ 分析知识库 {kb_id} 失败: {str(e)}")
            
            # 输出分析结果
            print(f"\n📊 分析结果:")
            print(f"  大型知识库 (>100条): {len(categories['large_kb'])} 个")
            print(f"  空知识库 (0条): {len(categories['empty_kb'])} 个")
            print(f"  可编辑知识库: {len(categories['editable_kb'])} 个")
            print(f"  文件夹类型: {len(categories['folder_type'])} 个")
            
            # 显示大型知识库详情
            if categories["large_kb"]:
                print(f"\n🏢 大型知识库详情:")
                for kb in categories["large_kb"][:3]:  # 只显示前3个
                    print(f"  - {kb['name']}: {kb['dataAmount']} 条数据")
                    
    except Exception as e:
        print(f"❌ 条件分析失败: {str(e)}")


def example_export_kb_info():
    """导出知识库信息示例"""
    print("\n💾 导出知识库信息示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        result = kb_client.get_kb_detail(kb_id=123456)
        
        if result.get("code") == 1:
            kb_info = result["data"]
            
            # 整理导出信息
            export_data = {
                "basic_info": {
                    "id": kb_info.get("id"),
                    "name": kb_info.get("name"),
                    "description": kb_info.get("description"),
                    "type": kb_info.get("type"),
                    "state": kb_info.get("state"),
                    "dataAmount": kb_info.get("dataAmount"),
                    "authorName": kb_info.get("authorName"),
                    "tags": kb_info.get("tags", [])
                },
                "configuration": kb_info.get("ext", {}),
                "permissions": kb_info.get("kbBtnPermission", []),
                "metadata": {
                    "vectorModel": kb_info.get("vectorModel"),
                    "parentId": kb_info.get("parentId"),
                    "virtualDsId": kb_info.get("virtualDsId"),
                    "dsNum": kb_info.get("dsNum"),
                    "approvalMode": kb_info.get("approvalMode"),
                    "approvalState": kb_info.get("approvalState")
                }
            }
            
            print("📋 知识库信息已整理完成")
            print(f"基础信息: {len(export_data['basic_info'])} 个字段")
            print(f"配置信息: {len(export_data['configuration'])} 个字段")
            print(f"权限信息: {len(export_data['permissions'])} 个权限")
            
            # 在实际应用中，可以保存到文件
            # with open(f"kb_info_{kb_info['id']}.json", "w", encoding="utf-8") as f:
            #     json.dump(export_data, f, ensure_ascii=False, indent=2)
            # print("✅ 信息已导出到文件")
            
        else:
            print(f"❌ 查询失败: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ 导出失败: {str(e)}")


if __name__ == "__main__":
    print("🧪 知识库详情查询功能使用示例")
    print("=" * 60)
    
    print("⚠️ 注意：运行这些示例需要有效的API密钥")
    print("请将 'your_personal_auth_key' 和 'your_personal_auth_secret' 替换为实际的密钥")
    print("请将示例中的 kb_id 替换为实际的知识库ID")
    print()
    
    # 显示各种使用示例
    example_basic_detail()
    # example_check_permissions()
    # example_analyze_config()
    # example_batch_detail_query()
    # example_conditional_analysis()
    # example_export_kb_info()
    
    print("\n" + "=" * 60)
    print("📖 详情查询功能说明:")
    print("1. get_kb_detail() - 通过知识库ID查询完整详细信息")
    print("2. 包含比列表查询更丰富的信息（配置、权限、统计等）")
    print("3. 可用于权限检查和配置验证")
    print("4. 支持批量查询和条件分析")
    print("5. 成功响应的code为1，失败时会抛出异常")
    print("6. 适用于管理界面和详细分析场景")