import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.client import KbClient

def example_basic_delete():
    """基础删除示例"""
    print("🗑️ 基础删除示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="135c9b6f7660456ba14a2818a311a80e",
        personal_auth_secret="i34ia5UpBnjuW42huwr97xTiFlIyeXc7"
    )
    
    # 删除知识库
    try:
        result = kb_client.delete_kb(kb_id=3316)
        
        if result.get("code") == 1:
            print("✅ 知识库删除成功")
            print(f"消息: {result.get('msg')}")
        else:
            print("❌ 删除失败")
            print(f"错误: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ 删除异常: {str(e)}")


def example_safe_delete():
    """安全删除示例（带确认）"""
    print("\n🔒 安全删除示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    kb_id = 123456
    
    try:
        # 1. 先获取知识库信息
        kb_list_result = kb_client.query_kb_list()
        
        target_kb = None
        if kb_list_result.get("code") == 0:
            kb_list = kb_list_result["data"]["list"]
            for kb in kb_list:
                if kb.get("id") == kb_id:
                    target_kb = kb
                    break
        
        if target_kb:
            print(f"找到知识库: {target_kb['name']}")
            print(f"描述: {target_kb.get('description', 'N/A')}")
            print(f"数据量: {target_kb.get('dataAmount', 0)} 条")
            print(f"权限: {target_kb.get('kbBtnPermission', [])}")
            
            # 2. 检查删除权限
            if "delete" not in target_kb.get("kbBtnPermission", []):
                print("❌ 没有删除权限")
                return
            
            # 3. 用户确认（在实际应用中）
            # confirm = input("确认删除此知识库？(yes/no): ")
            # if confirm.lower() != 'yes':
            #     print("取消删除")
            #     return
            
            # 4. 执行删除
            result = kb_client.delete_kb(kb_id=kb_id)
            
            if result.get("code") == 1:
                print("✅ 知识库已安全删除")
            else:
                print(f"❌ 删除失败: {result.get('msg')}")
                
        else:
            print(f"❌ 未找到ID为 {kb_id} 的知识库")
            
    except Exception as e:
        print(f"❌ 安全删除过程异常: {str(e)}")


def example_batch_delete():
    """批量删除示例"""
    print("\n📦 批量删除示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 要删除的知识库ID列表
    kb_ids_to_delete = [123456, 123457, 123458]
    
    success_count = 0
    failed_count = 0
    
    for kb_id in kb_ids_to_delete:
        try:
            print(f"\n删除知识库 {kb_id}...")
            result = kb_client.delete_kb(kb_id=kb_id)
            
            if result.get("code") == 1:
                print(f"✅ 知识库 {kb_id} 删除成功")
                success_count += 1
            else:
                print(f"❌ 知识库 {kb_id} 删除失败: {result.get('msg')}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ 知识库 {kb_id} 删除异常: {str(e)}")
            failed_count += 1
    
    print(f"\n📊 批量删除结果:")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {failed_count} 个")


def example_conditional_delete():
    """条件删除示例"""
    print("\n🎯 条件删除示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    try:
        # 获取所有知识库
        kb_list_result = kb_client.query_kb_list(page_size=50)
        
        if kb_list_result.get("code") == 0:
            kb_list = kb_list_result["data"]["list"]
            
            # 删除条件：包含"测试"标签且数据量为0的知识库
            candidates = []
            
            for kb in kb_list:
                tags = kb.get("tags", [])
                data_amount = kb.get("dataAmount", 0)
                permissions = kb.get("kbBtnPermission", [])
                
                if ("测试" in tags and 
                    data_amount == 0 and 
                    "delete" in permissions):
                    candidates.append(kb)
            
            print(f"找到 {len(candidates)} 个符合删除条件的知识库:")
            
            for kb in candidates:
                print(f"- {kb['name']} (ID: {kb['id']})")
                print(f"  标签: {kb.get('tags', [])}")
                print(f"  数据量: {kb.get('dataAmount', 0)}")
                
                try:
                    result = kb_client.delete_kb(kb_id=kb["id"])
                    if result.get("code") == 1:
                        print(f"  ✅ 删除成功")
                    else:
                        print(f"  ❌ 删除失败: {result.get('msg')}")
                except Exception as e:
                    print(f"  ❌ 删除异常: {str(e)}")
                    
        else:
            print(f"❌ 获取知识库列表失败: {kb_list_result}")
            
    except Exception as e:
        print(f"❌ 条件删除异常: {str(e)}")


def example_delete_with_backup():
    """带备份的删除示例"""
    print("\n💾 带备份的删除示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    kb_id = 123456
    
    try:
        # 1. 获取知识库详细信息作为备份
        kb_list_result = kb_client.query_kb_list()
        
        target_kb = None
        if kb_list_result.get("code") == 0:
            kb_list = kb_list_result["data"]["list"]
            for kb in kb_list:
                if kb.get("id") == kb_id:
                    target_kb = kb
                    break
        
        if target_kb:
            # 2. 保存知识库信息到备份
            backup_info = {
                "id": target_kb.get("id"),
                "name": target_kb.get("name"),
                "description": target_kb.get("description"),
                "tags": target_kb.get("tags", []),
                "avatarUrl": target_kb.get("avatarUrl"),
                "ext": target_kb.get("ext"),
                "dataAmount": target_kb.get("dataAmount", 0),
                "backup_time": "2024-01-01 12:00:00"  # 实际应用中使用当前时间
            }
            
            print("📋 知识库信息已备份:")
            print(f"  名称: {backup_info['name']}")
            print(f"  数据量: {backup_info['dataAmount']}")
            
            # 在实际应用中，这里应该将backup_info保存到文件或数据库
            # import json
            # with open(f"kb_backup_{kb_id}.json", "w", encoding="utf-8") as f:
            #     json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            # 3. 执行删除
            result = kb_client.delete_kb(kb_id=kb_id)
            
            if result.get("code") == 1:
                print("✅ 知识库删除成功，备份信息已保存")
            else:
                print(f"❌ 删除失败: {result.get('msg')}")
                
        else:
            print(f"❌ 未找到知识库 {kb_id}")
            
    except Exception as e:
        print(f"❌ 带备份删除异常: {str(e)}")


def example_error_handling():
    """错误处理示例"""
    print("\n⚠️ 错误处理示例")
    print("-" * 40)
    
    kb_client = KbClient(
        personal_auth_key="your_personal_auth_key",
        personal_auth_secret="your_personal_auth_secret"
    )
    
    # 测试各种错误情况
    error_cases = [
        {"kb_id": 999999999, "desc": "不存在的知识库"},
        {"kb_id": "invalid", "desc": "无效的ID类型"},
        {"kb_id": -1, "desc": "负数ID"}
    ]
    
    for case in error_cases:
        print(f"\n测试: {case['desc']}")
        try:
            result = kb_client.delete_kb(kb_id=case["kb_id"])
            print(f"⚠️ 意外成功: {result}")
        except ValueError as e:
            print(f"✅ 参数错误: {str(e)}")
        except Exception as e:
            print(f"✅ API错误: {str(e)[:100]}...")
            
            # 根据错误类型进行处理
            error_str = str(e)
            if "404" in error_str:
                print("🔍 知识库不存在")
            elif "403" in error_str:
                print("🚫 权限不足")
            elif "401" in error_str:
                print("🔑 认证失败")
            else:
                print("❓ 其他错误")


if __name__ == "__main__":
    print("🧪 知识库删除功能使用示例")
    print("=" * 60)
    
    print("⚠️ 注意：运行这些示例需要有效的API密钥")
    print("请将 'your_personal_auth_key' 和 'your_personal_auth_secret' 替换为实际的密钥")
    print("请将示例中的 kb_id 替换为实际的知识库ID")
    print("⚠️ 删除操作不可逆，请谨慎使用！")
    print()
    
    # 显示各种使用示例
    example_basic_delete()
    # example_safe_delete()
    # example_batch_delete()
    # example_conditional_delete()
    # example_delete_with_backup()
    # example_error_handling()
    
    print("\n" + "=" * 60)
    print("📖 删除功能说明:")
    print("1. delete_kb() - 通过知识库ID删除知识库")
    print("2. 删除操作不可逆，会同时删除所有文档")
    print("3. 需要有删除权限才能执行")
    print("4. 建议删除前先备份重要信息")
    print("5. 成功响应的code为1，失败时会抛出异常")
    print("6. 支持批量删除和条件删除")