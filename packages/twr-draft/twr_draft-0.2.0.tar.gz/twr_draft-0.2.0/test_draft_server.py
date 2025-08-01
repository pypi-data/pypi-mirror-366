#!/usr/bin/env python3
"""
测试TWR Draft MCP服务器的功能（内存存储版本）
"""

from draft_server.draft import (
    _new_draft, _get_draft, _update_draft, _delete_draft, 
    _list_drafts, _search_drafts, _get_draft_info,
    _clear_all_drafts, _get_draft_count
)

def test_draft_server():
    """测试草稿服务器的所有功能"""
    
    try:
        print("🧪 开始测试TWR Draft MCP服务器（内存存储版本）...")
        
        # 清空之前的测试数据
        print("\n0. 清空之前的测试数据...")
        _clear_all_drafts()
        
        # 测试1: 创建新草稿
        print("\n1. 测试创建新草稿...")
        result = _new_draft("测试草稿", "这是一个测试草稿的内容")
        print(f"   结果: {result}")
        
        # 测试2: 获取草稿内容
        print("\n2. 测试获取草稿内容...")
        result = _get_draft("测试草稿")
        print(f"   结果: {result}")
        
        # 测试3: 更新草稿
        print("\n3. 测试更新草稿...")
        result = _update_draft("测试草稿", "这是更新后的测试草稿内容")
        print(f"   结果: {result}")
        
        # 测试4: 获取草稿信息
        print("\n4. 测试获取草稿信息...")
        result = _get_draft_info("测试草稿")
        print(f"   结果: {result}")
        
        # 测试5: 创建更多草稿
        print("\n5. 测试创建更多草稿...")
        _new_draft("项目想法", "关于新项目的想法和计划")
        _new_draft("会议记录", "今天会议的重要记录")
        print("   创建了2个新草稿")
        
        # 测试6: 获取草稿总数
        print("\n6. 测试获取草稿总数...")
        result = _get_draft_count()
        print(f"   结果: {result}")
        
        # 测试7: 列出所有草稿
        print("\n7. 测试列出所有草稿...")
        result = _list_drafts()
        print(f"   结果: {result}")
        
        # 测试8: 搜索草稿
        print("\n8. 测试搜索草稿...")
        result = _search_drafts("项目")
        print(f"   结果: {result}")
        
        # 测试9: 搜索不存在的草稿
        print("\n9. 测试搜索不存在的草稿...")
        result = _search_drafts("不存在的关键词")
        print(f"   结果: {result}")
        
        # 测试10: 获取不存在的草稿
        print("\n10. 测试获取不存在的草稿...")
        result = _get_draft("不存在的草稿")
        print(f"   结果: {result}")
        
        # 测试11: 删除草稿
        print("\n11. 测试删除草稿...")
        result = _delete_draft("会议记录")
        print(f"   结果: {result}")
        
        # 测试12: 删除后列出草稿
        print("\n12. 测试删除后列出草稿...")
        result = _list_drafts()
        print(f"   结果: {result}")
        
        # 测试13: 清空所有草稿
        print("\n13. 测试清空所有草稿...")
        result = _clear_all_drafts()
        print(f"   结果: {result}")
        
        # 测试14: 验证清空结果
        print("\n14. 验证清空结果...")
        result = _get_draft_count()
        print(f"   结果: {result}")
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_draft_server() 