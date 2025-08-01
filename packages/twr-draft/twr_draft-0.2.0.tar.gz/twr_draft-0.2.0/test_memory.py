#!/usr/bin/env python3
"""
测试内存存储版本的TWR Draft MCP服务器
"""

import sys
sys.path.append('src')

from draft_server.draft import (
    _new_draft, _get_draft, _update_draft, _delete_draft, 
    _list_drafts, _search_drafts, _get_draft_info,
    _list_categories, _list_tags, _get_drafts_by_category, _get_drafts_by_tag,
    _clear_all_drafts, _get_draft_count
)

def test_memory_storage():
    """测试内存存储功能"""
    print("🧪 测试内存存储版本的TWR Draft MCP服务器...")
    
    try:
        # 清空之前的测试数据
        print("\n1. 清空之前的测试数据...")
        result = _clear_all_drafts()
        print(f"   结果: {result}")
        
        # 测试创建草稿
        print("\n2. 测试创建草稿...")
        result = _new_draft("测试草稿", "这是一个测试草稿的内容", "测试", "测试,示例")
        print(f"   结果: {result}")
        
        # 测试获取草稿
        print("\n3. 测试获取草稿...")
        content = _get_draft("测试草稿")
        print(f"   内容: {content}")
        
        # 测试获取草稿信息
        print("\n4. 测试获取草稿信息...")
        info = _get_draft_info("测试草稿")
        print(f"   信息: {info}")
        
        # 测试获取草稿数量
        print("\n5. 测试获取草稿数量...")
        count = _get_draft_count()
        print(f"   数量: {count}")
        
        # 测试列出草稿
        print("\n6. 测试列出草稿...")
        drafts = _list_drafts()
        print(f"   草稿列表: {drafts}")
        
        # 测试搜索草稿
        print("\n7. 测试搜索草稿...")
        search_result = _search_drafts("测试")
        print(f"   搜索结果: {search_result}")
        
        # 测试更新草稿
        print("\n8. 测试更新草稿...")
        update_result = _update_draft("测试草稿", "这是更新后的内容", "重要测试", "测试,重要")
        print(f"   更新结果: {update_result}")
        
        # 测试清空草稿
        print("\n9. 测试清空草稿...")
        clear_result = _clear_all_drafts()
        print(f"   清空结果: {clear_result}")
        
        # 验证清空结果
        print("\n10. 验证清空结果...")
        final_count = _get_draft_count()
        print(f"   最终数量: {final_count}")
        
        print("\n✅ 内存存储测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_storage() 