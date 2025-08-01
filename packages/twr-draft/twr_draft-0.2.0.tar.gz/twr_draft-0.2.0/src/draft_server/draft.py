import json
from typing import Dict, List, Optional
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("DraftServer")

# 内存中的草稿存储
_drafts_storage: Dict[str, Dict] = {}

def load_drafts() -> Dict[str, Dict]:
    """从内存加载所有草稿"""
    return _drafts_storage

def save_drafts(drafts: Dict[str, Dict]):
    """保存草稿到内存"""
    global _drafts_storage
    _drafts_storage = drafts

def _new_draft(draft_name: str, draft_content: str, category: str = "未分类", tags: str = "") -> str:
    """创建一个新草稿的内部实现"""
    try:
        drafts = load_drafts()
        if draft_name in drafts:
            return f"草稿 '{draft_name}' 已存在，请使用 update_draft 工具更新内容"
        
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        drafts[draft_name] = {
            "content": draft_content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": tag_list,
            "category": category
        }
        save_drafts(drafts)
        return f"成功创建草稿: {draft_name} (分类: {category}, 标签: {', '.join(tag_list) if tag_list else '无'})"
    except Exception as e:
        return f"创建草稿失败: {e}"

def _get_draft(draft_name: str) -> str:
    """获取草稿内容的内部实现"""
    try:
        drafts = load_drafts()
        if draft_name not in drafts:
            return f"草稿 '{draft_name}' 不存在"
        return drafts[draft_name]["content"]
    except Exception as e:
        return f"获取草稿失败: {e}"

def _update_draft(draft_name: str, draft_content: str, category: str = None, tags: str = None) -> str:
    """更新草稿内容的内部实现"""
    try:
        drafts = load_drafts()
        if draft_name not in drafts:
            return f"草稿 '{draft_name}' 不存在，请先创建"
        
        drafts[draft_name]["content"] = draft_content
        drafts[draft_name]["updated_at"] = datetime.now().isoformat()
        
        if category is not None:
            drafts[draft_name]["category"] = category
        if tags is not None:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
            drafts[draft_name]["tags"] = tag_list
        
        save_drafts(drafts)
        return f"成功更新草稿: {draft_name}"
    except Exception as e:
        return f"更新草稿失败: {e}"

def _delete_draft(draft_name: str) -> str:
    """删除草稿的内部实现"""
    try:
        drafts = load_drafts()
        if draft_name not in drafts:
            return f"草稿 '{draft_name}' 不存在"
        
        del drafts[draft_name]
        save_drafts(drafts)
        return f"成功删除草稿: {draft_name}"
    except Exception as e:
        return f"删除草稿失败: {e}"

def _list_drafts() -> str:
    """列出所有草稿的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        result = "所有草稿:\n"
        for name, data in sorted(drafts.items()):
            category = data.get("category", "未分类")
            tags = ", ".join(data.get("tags", [])) if data.get("tags") else "无"
            result += f"- {name} (分类: {category}, 标签: {tags})\n"
        
        return result
    except Exception as e:
        return f"列出草稿失败: {e}"

def _search_drafts(keyword: str) -> str:
    """搜索草稿的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        matching_drafts = []
        for name, data in drafts.items():
            content = data.get("content", "")
            category = data.get("category", "")
            tags = " ".join(data.get("tags", []))
            
            if (keyword.lower() in name.lower() or 
                keyword.lower() in content.lower() or
                keyword.lower() in category.lower() or
                keyword.lower() in tags.lower()):
                matching_drafts.append(name)
        
        if not matching_drafts:
            return f"没有找到包含关键词 '{keyword}' 的草稿"
        
        result = f"匹配的草稿:\n"
        for name in sorted(matching_drafts):
            data = drafts[name]
            category = data.get("category", "未分类")
            tags = ", ".join(data.get("tags", [])) if data.get("tags") else "无"
            result += f"- {name} (分类: {category}, 标签: {tags})\n"
        
        return result
    except Exception as e:
        return f"搜索草稿失败: {e}"

def _get_draft_info(draft_name: str) -> str:
    """获取草稿详细信息的内部实现"""
    try:
        drafts = load_drafts()
        if draft_name not in drafts:
            return f"草稿 '{draft_name}' 不存在"
        
        data = drafts[draft_name]
        content = data.get("content", "")
        category = data.get("category", "未分类")
        tags = ", ".join(data.get("tags", [])) if data.get("tags") else "无"
        created_at = data.get("created_at", "未知")
        updated_at = data.get("updated_at", "未知")
        
        char_count = len(content)
        word_count = len(content.split())
        line_count = len(content.splitlines())
        
        return f"""草稿信息: {draft_name}
分类: {category}
标签: {tags}
创建时间: {created_at}
更新时间: {updated_at}
字符数: {char_count}
单词数: {word_count}
行数: {line_count}
内容预览: {content[:100]}{'...' if len(content) > 100 else ''}"""
    except Exception as e:
        return f"获取草稿信息失败: {e}"

def _list_categories() -> str:
    """列出所有分类的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        categories = set()
        for data in drafts.values():
            category = data.get("category", "未分类")
            categories.add(category)
        
        if not categories:
            return "没有找到任何分类"
        
        result = "所有分类:\n"
        for category in sorted(categories):
            count = sum(1 for data in drafts.values() if data.get("category") == category)
            result += f"- {category} ({count} 个草稿)\n"
        
        return result
    except Exception as e:
        return f"列出分类失败: {e}"

def _list_tags() -> str:
    """列出所有标签的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        all_tags = set()
        for data in drafts.values():
            tags = data.get("tags", [])
            all_tags.update(tags)
        
        if not all_tags:
            return "没有找到任何标签"
        
        result = "所有标签:\n"
        for tag in sorted(all_tags):
            count = sum(1 for data in drafts.values() if tag in data.get("tags", []))
            result += f"- {tag} ({count} 个草稿)\n"
        
        return result
    except Exception as e:
        return f"列出标签失败: {e}"

def _get_drafts_by_category(category: str) -> str:
    """按分类获取草稿的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        matching_drafts = []
        for name, data in drafts.items():
            if data.get("category") == category:
                matching_drafts.append(name)
        
        if not matching_drafts:
            return f"分类 '{category}' 下没有找到任何草稿"
        
        result = f"分类 '{category}' 下的草稿:\n"
        for name in sorted(matching_drafts):
            data = drafts[name]
            tags = ", ".join(data.get("tags", [])) if data.get("tags") else "无"
            result += f"- {name} (标签: {tags})\n"
        
        return result
    except Exception as e:
        return f"按分类获取草稿失败: {e}"

def _get_drafts_by_tag(tag: str) -> str:
    """按标签获取草稿的内部实现"""
    try:
        drafts = load_drafts()
        if not drafts:
            return "没有找到任何草稿"
        
        matching_drafts = []
        for name, data in drafts.items():
            if tag in data.get("tags", []):
                matching_drafts.append(name)
        
        if not matching_drafts:
            return f"没有找到包含标签 '{tag}' 的草稿"
        
        result = f"包含标签 '{tag}' 的草稿:\n"
        for name in sorted(matching_drafts):
            data = drafts[name]
            category = data.get("category", "未分类")
            tags = ", ".join(data.get("tags", [])) if data.get("tags") else "无"
            result += f"- {name} (分类: {category}, 标签: {tags})\n"
        
        return result
    except Exception as e:
        return f"按标签获取草稿失败: {e}"

def _clear_all_drafts() -> str:
    """清空所有草稿的内部实现"""
    try:
        global _drafts_storage
        count = len(_drafts_storage)
        _drafts_storage = {}
        return f"成功清空所有草稿，共清空了 {count} 个草稿"
    except Exception as e:
        return f"清空草稿失败: {e}"

def _get_draft_count() -> str:
    """获取草稿总数的内部实现"""
    try:
        drafts = load_drafts()
        count = len(drafts)
        return f"当前共有 {count} 个草稿"
    except Exception as e:
        return f"获取草稿数量失败: {e}"

# MCP工具函数
@mcp.tool()
def new_draft(draft_name: str, draft_content: str, category: str = "未分类", tags: str = "") -> str:
    """创建一个新草稿
    
    Args:
        draft_name: 草稿名称
        draft_content: 草稿内容
        category: 草稿分类（可选）
        tags: 标签，用逗号分隔（可选）
        
    Returns:
        创建结果信息
    """
    return _new_draft(draft_name, draft_content, category, tags)

@mcp.tool()
def get_draft(draft_name: str) -> str:
    """获取草稿内容
    
    Args:
        draft_name: 草稿名称
        
    Returns:
        草稿内容或错误信息
    """
    return _get_draft(draft_name)

@mcp.tool()
def update_draft(draft_name: str, draft_content: str, category: str = None, tags: str = None) -> str:
    """更新草稿内容
    
    Args:
        draft_name: 草稿名称
        draft_content: 新的草稿内容
        category: 新的分类（可选）
        tags: 新的标签，用逗号分隔（可选）
        
    Returns:
        更新结果信息
    """
    return _update_draft(draft_name, draft_content, category, tags)

@mcp.tool()
def delete_draft(draft_name: str) -> str:
    """删除草稿
    
    Args:
        draft_name: 草稿名称
        
    Returns:
        删除结果信息
    """
    return _delete_draft(draft_name)

@mcp.tool()
def list_drafts() -> str:
    """列出所有草稿
    
    Returns:
        所有草稿的列表
    """
    return _list_drafts()

@mcp.tool()
def search_drafts(keyword: str) -> str:
    """搜索草稿
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        匹配的草稿列表
    """
    return _search_drafts(keyword)

@mcp.tool()
def get_draft_info(draft_name: str) -> str:
    """获取草稿详细信息
    
    Args:
        draft_name: 草稿名称
        
    Returns:
        草稿的详细信息
    """
    return _get_draft_info(draft_name)

@mcp.tool()
def list_categories() -> str:
    """列出所有分类
    
    Returns:
        所有分类的列表
    """
    return _list_categories()

@mcp.tool()
def list_tags() -> str:
    """列出所有标签
    
    Returns:
        所有标签的列表
    """
    return _list_tags()

@mcp.tool()
def get_drafts_by_category(category: str) -> str:
    """按分类获取草稿
    
    Args:
        category: 分类名称
        
    Returns:
        该分类下的所有草稿
    """
    return _get_drafts_by_category(category)

@mcp.tool()
def get_drafts_by_tag(tag: str) -> str:
    """按标签获取草稿
    
    Args:
        tag: 标签名称
        
    Returns:
        包含该标签的所有草稿
    """
    return _get_drafts_by_tag(tag)

@mcp.tool()
def clear_all_drafts() -> str:
    """清空所有草稿
    
    Returns:
        清空结果信息
    """
    return _clear_all_drafts()

@mcp.tool()
def get_draft_count() -> str:
    """获取草稿总数
    
    Returns:
        草稿总数信息
    """
    return _get_draft_count()

if __name__ == "__main__":
    mcp.run(transport="stdio")
