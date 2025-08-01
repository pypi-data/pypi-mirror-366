#!/usr/bin/env python3
"""
测试TWR Draft MCP服务器的高级功能（分类和标签）- 内存存储版本
"""

from draft_server.draft import (
    _new_draft, _get_draft, _update_draft, _delete_draft, 
    _list_drafts, _search_drafts, _get_draft_info,
    _list_categories, _list_tags, _get_drafts_by_category, _get_drafts_by_tag,
    _clear_all_drafts, _get_draft_count
)

def test_advanced_features():
    """测试草稿服务器的高级功能"""
    
    try:
        print("🧪 开始测试TWR Draft MCP服务器高级功能（内存存储版本）...")
        
        # 清空之前的测试数据
        print("\n0. 清空之前的测试数据...")
        _clear_all_drafts()
        
        # 测试1: 创建带分类和标签的草稿
        print("\n1. 测试创建带分类和标签的草稿...")
        result = _new_draft("项目计划", "这是一个新项目的详细计划", "项目", "计划,重要")
        print(f"   结果: {result}")
        
        # 测试2: 创建更多不同分类的草稿
        print("\n2. 测试创建更多不同分类的草稿...")
        _new_draft("会议记录", "今天团队会议的重要记录", "会议", "记录,团队")
        _new_draft("技术笔记", "关于新技术的笔记", "技术", "笔记,学习")
        _new_draft("个人想法", "一些个人想法和灵感", "个人", "想法,灵感")
        print("   创建了3个新草稿")
        
        # 测试3: 获取草稿总数
        print("\n3. 测试获取草稿总数...")
        result = _get_draft_count()
        print(f"   结果: {result}")
        
        # 测试4: 列出所有草稿（应该显示分类和标签）
        print("\n4. 测试列出所有草稿...")
        result = _list_drafts()
        print(f"   结果: {result}")
        
        # 测试5: 列出所有分类
        print("\n5. 测试列出所有分类...")
        result = _list_categories()
        print(f"   结果: {result}")
        
        # 测试6: 列出所有标签
        print("\n6. 测试列出所有标签...")
        result = _list_tags()
        print(f"   结果: {result}")
        
        # 测试7: 按分类获取草稿
        print("\n7. 测试按分类获取草稿...")
        result = _get_drafts_by_category("项目")
        print(f"   结果: {result}")
        
        # 测试8: 按标签获取草稿
        print("\n8. 测试按标签获取草稿...")
        result = _get_drafts_by_tag("重要")
        print(f"   结果: {result}")
        
        # 测试9: 搜索功能（应该能搜索分类和标签）
        print("\n9. 测试搜索功能...")
        result = _search_drafts("技术")
        print(f"   结果: {result}")
        
        # 测试10: 更新草稿的分类和标签
        print("\n10. 测试更新草稿的分类和标签...")
        result = _update_draft("项目计划", "更新后的项目计划内容", "重要项目", "计划,重要,紧急")
        print(f"   结果: {result}")
        
        # 测试11: 获取更新后的草稿信息
        print("\n11. 测试获取更新后的草稿信息...")
        result = _get_draft_info("项目计划")
        print(f"   结果: {result}")
        
        # 测试12: 验证更新后的分类和标签
        print("\n12. 测试验证更新后的分类和标签...")
        result = _get_drafts_by_category("重要项目")
        print(f"   结果: {result}")
        
        result = _get_drafts_by_tag("紧急")
        print(f"   结果: {result}")
        
        # 测试13: 清空所有草稿
        print("\n13. 测试清空所有草稿...")
        result = _clear_all_drafts()
        print(f"   结果: {result}")
        
        # 测试14: 验证清空结果
        print("\n14. 验证清空结果...")
        result = _get_draft_count()
        print(f"   结果: {result}")
        
        print("\n✅ 所有高级功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_advanced_features() 