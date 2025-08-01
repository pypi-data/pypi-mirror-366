#!/usr/bin/env python3
"""
TWR Draft MCP服务器使用示例（内存存储版本）
"""

from draft_server.draft import (
    new_draft, get_draft, update_draft, delete_draft, 
    list_drafts, search_drafts, get_draft_info,
    list_categories, list_tags, get_drafts_by_category, get_drafts_by_tag,
    clear_all_drafts, get_draft_count
)

def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 清空之前的测试数据
    clear_all_drafts()
    
    # 创建草稿
    print("\n1. 创建草稿...")
    result = new_draft("我的第一个草稿", "这是第一个草稿的内容")
    print(result)
    
    # 获取草稿内容
    print("\n2. 获取草稿内容...")
    content = get_draft("我的第一个草稿")
    print(f"草稿内容: {content}")
    
    # 更新草稿
    print("\n3. 更新草稿...")
    result = update_draft("我的第一个草稿", "这是更新后的草稿内容")
    print(result)
    
    # 获取草稿信息
    print("\n4. 获取草稿信息...")
    info = get_draft_info("我的第一个草稿")
    print(info)
    
    # 获取草稿总数
    print("\n5. 获取草稿总数...")
    count = get_draft_count()
    print(count)

def advanced_usage_example():
    """高级使用示例（分类和标签）"""
    print("\n=== 高级使用示例 ===")
    
    # 清空之前的测试数据
    clear_all_drafts()
    
    # 创建带分类和标签的草稿
    print("\n1. 创建带分类和标签的草稿...")
    new_draft("项目计划", "新项目的详细计划", "项目", "计划,重要")
    new_draft("会议记录", "团队会议记录", "会议", "记录,团队")
    new_draft("技术笔记", "学习笔记", "技术", "笔记,学习")
    
    # 获取草稿总数
    print("\n2. 获取草稿总数...")
    count = get_draft_count()
    print(count)
    
    # 列出所有草稿
    print("\n3. 列出所有草稿...")
    drafts = list_drafts()
    print(drafts)
    
    # 列出所有分类
    print("\n4. 列出所有分类...")
    categories = list_categories()
    print(categories)
    
    # 列出所有标签
    print("\n5. 列出所有标签...")
    tags = list_tags()
    print(tags)
    
    # 按分类获取草稿
    print("\n6. 按分类获取草稿...")
    project_drafts = get_drafts_by_category("项目")
    print(project_drafts)
    
    # 按标签获取草稿
    print("\n7. 按标签获取草稿...")
    important_drafts = get_drafts_by_tag("重要")
    print(important_drafts)
    
    # 搜索草稿
    print("\n8. 搜索草稿...")
    search_results = search_drafts("技术")
    print(search_results)

def workflow_example():
    """工作流程示例"""
    print("\n=== 工作流程示例 ===")
    
    # 清空之前的测试数据
    clear_all_drafts()
    
    # 模拟一个完整的工作流程
    print("\n1. 创建项目相关的草稿...")
    new_draft("需求分析", "用户需求分析文档", "项目", "需求,分析")
    new_draft("技术方案", "技术实现方案", "项目", "技术,方案")
    new_draft("开发计划", "开发时间计划", "项目", "计划,开发")
    
    print("\n2. 创建会议相关的草稿...")
    new_draft("需求评审会议", "需求评审会议记录", "会议", "评审,需求")
    new_draft("技术讨论", "技术方案讨论记录", "会议", "讨论,技术")
    
    print("\n3. 查看当前草稿总数...")
    count = get_draft_count()
    print(count)
    
    print("\n4. 查看项目分类下的所有草稿...")
    project_drafts = get_drafts_by_category("项目")
    print(project_drafts)
    
    print("\n5. 搜索所有包含'需求'的草稿...")
    requirement_drafts = search_drafts("需求")
    print(requirement_drafts)
    
    print("\n6. 更新技术方案...")
    update_draft("技术方案", "更新后的技术实现方案，包含更多细节", "项目", "技术,方案,详细")
    
    print("\n7. 查看更新后的草稿信息...")
    info = get_draft_info("技术方案")
    print(info)

def memory_management_example():
    """内存管理示例"""
    print("\n=== 内存管理示例 ===")
    
    # 清空之前的测试数据
    clear_all_drafts()
    
    print("\n1. 创建一些测试草稿...")
    new_draft("草稿1", "内容1")
    new_draft("草稿2", "内容2")
    new_draft("草稿3", "内容3")
    
    print("\n2. 查看当前草稿数量...")
    count = get_draft_count()
    print(count)
    
    print("\n3. 删除一个草稿...")
    result = delete_draft("草稿2")
    print(result)
    
    print("\n4. 查看删除后的草稿数量...")
    count = get_draft_count()
    print(count)
    
    print("\n5. 清空所有草稿...")
    result = clear_all_drafts()
    print(result)
    
    print("\n6. 验证清空结果...")
    count = get_draft_count()
    print(count)

def cleanup_example():
    """清理示例"""
    print("\n=== 清理示例 ===")
    
    # 清空所有草稿
    result = clear_all_drafts()
    print(f"清理结果: {result}")
    
    # 验证清理结果
    count = get_draft_count()
    print(f"清理后草稿数量: {count}")

if __name__ == "__main__":
    print("TWR Draft MCP服务器使用示例（内存存储版本）")
    print("=" * 60)
    
    try:
        # 运行基本示例
        basic_usage_example()
        
        # 运行高级示例
        advanced_usage_example()
        
        # 运行工作流程示例
        workflow_example()
        
        # 运行内存管理示例
        memory_management_example()
        
        # 清理测试数据
        cleanup_example()
        
        print("\n✅ 所有示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc() 