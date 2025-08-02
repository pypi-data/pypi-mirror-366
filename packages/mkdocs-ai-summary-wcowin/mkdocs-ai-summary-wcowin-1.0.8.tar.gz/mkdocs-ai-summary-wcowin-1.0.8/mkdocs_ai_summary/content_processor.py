"""内容处理器模块

负责处理页面内容、判断是否生成摘要、格式化摘要显示等功能。
"""

import re
import hashlib
import yaml
from typing import List, Optional
from mkdocs.structure.pages import Page


class ContentProcessor:
    """内容处理器"""
    
    def __init__(self, enabled_folders: List[str], exclude_patterns: List[str], 
                 exclude_files: List[str], summary_language: str):
        """初始化内容处理器
        
        Args:
            enabled_folders: 启用摘要的文件夹列表
            exclude_patterns: 排除模式列表
            exclude_files: 排除文件列表
            summary_language: 摘要语言
        """
        self.enabled_folders = enabled_folders
        self.exclude_patterns = exclude_patterns
        self.exclude_files = exclude_files
        self.summary_language = summary_language
    
    def should_generate_summary(self, page: Page) -> bool:
        """判断是否应该为页面生成摘要
        
        Args:
            page: MkDocs页面对象
            
        Returns:
            bool: True表示应该生成摘要，False表示不应该生成
        """
        file_path = str(page.file.src_path)
        
        # 检查排除文件
        if file_path in self.exclude_files:
            return False
        
        # 检查排除模式
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return False
        
        # 检查启用文件夹
        for folder in self.enabled_folders:
            if file_path.startswith(folder):
                return True
        
        return False
    
    def parse_front_matter(self, markdown: str) -> tuple[Optional[dict], str]:
        """解析markdown的front matter
        
        Args:
            markdown: 原始markdown内容
            
        Returns:
            tuple: (front_matter_dict, content_without_front_matter)
        """
        front_matter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', markdown, re.DOTALL)
        
        if front_matter_match:
            try:
                front_matter_yaml = front_matter_match.group(1)
                front_matter = yaml.safe_load(front_matter_yaml)
                content = markdown[front_matter_match.end():]
                return front_matter, content
            except yaml.YAMLError:
                # 如果YAML解析失败，返回None和原始内容
                return None, markdown
        
        return None, markdown
    
    def get_page_language(self, markdown: str) -> str:
        """获取页面级别的语言设置
        
        Args:
            markdown: 原始markdown内容
            
        Returns:
            str: 页面语言设置，如果没有设置则返回全局设置
        """
        front_matter, _ = self.parse_front_matter(markdown)
        
        if front_matter and 'ai_summary_lang' in front_matter:
            page_lang = front_matter['ai_summary_lang']
            # 验证语言设置是否有效
            if page_lang in ['zh', 'en', 'both']:
                return page_lang
        
        return self.summary_language
    
    def clean_content_for_ai(self, markdown: str) -> str:
        """清理内容用于AI处理
        
        Args:
            markdown: 原始markdown内容
            
        Returns:
            str: 清理后的内容
        """
        content = markdown
        
        # 移除YAML front matter
        content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
        
        # 移除已存在的摘要块
        content = re.sub(r'!!! info "📖 阅读信息".*?(?=\n\n|\n#|\Z)', '', content, flags=re.DOTALL)
        content = re.sub(r'!!! abstract "🤖 AI摘要".*?(?=\n\n|\n#|\Z)', '', content, flags=re.DOTALL)
        
        # 移除代码块
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]+`', '', content)
        
        # 移除图片和链接
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 清理多余空白
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def get_content_hash(self, content: str, language: Optional[str] = None) -> str:
        """生成内容哈希
        
        Args:
            content: 内容字符串
            language: 语言设置，如果为None则使用默认语言
            
        Returns:
            str: MD5哈希值
        """
        lang = language or self.summary_language
        content_with_lang = f"{content}_{lang}"
        return hashlib.md5(content_with_lang.encode('utf-8')).hexdigest()
    
    def format_summary(self, summary: str, service: str, language: str) -> str:
        """格式化摘要显示
        
        Args:
            summary: 摘要内容
            service: AI服务名称
            language: 摘要语言
            
        Returns:
            str: 格式化后的摘要markdown
        """
        # 服务图标映射
        service_icons = {
            'deepseek': '🧠',
            'openai': '🤖',
            'gemini': '✨',
            'glm': '⚡',
            'fallback': '📝'
        }
        
        icon = service_icons.get(service, '🤖')
        
        if language == 'zh':
            title = f"{icon} AI摘要 ({service.upper()})"
        else:
            title = f"{icon} AI Summary ({service.upper()})"
        
        return f'!!! abstract "{title}"\n\n    {summary}\n'
    
    def inject_summary(self, markdown: str, summary: str) -> str:
        """将摘要注入到markdown内容中
        
        Args:
            markdown: 原始markdown内容
            summary: 格式化后的摘要
            
        Returns:
            str: 注入摘要后的markdown内容
        """
        # 移除YAML front matter以找到正确的插入位置
        front_matter_match = re.match(r'^(---.*?---\s*)', markdown, re.DOTALL)
        
        if front_matter_match:
            front_matter = front_matter_match.group(1)
            content = markdown[len(front_matter):]
            return front_matter + summary + '\n' + content
        else:
            return summary + '\n' + markdown
    
    def get_fallback_summary(self, title: str, language: str = 'zh') -> str:
        """生成备用摘要
        
        Args:
            title: 页面标题
            language: 摘要语言
            
        Returns:
            str: 备用摘要内容
        """
        if language == 'zh':
            return f"本文档《{title}》包含重要内容，建议仔细阅读以获取详细信息。"
        else:
            return f"This document '{title}' contains important content. Please read carefully for detailed information."
    
    def validate_summary_content(self, summary: str) -> bool:
        """验证摘要内容
        
        Args:
            summary: 摘要内容
            
        Returns:
            bool: True表示摘要有效，False表示无效
        """
        if not summary or not summary.strip():
            return False
        
        # 检查摘要长度（至少10个字符）
        if len(summary.strip()) < 10:
            return False
        
        # 检查是否包含明显的错误信息
        error_indicators = ['error', 'failed', 'unable', '错误', '失败', '无法']
        summary_lower = summary.lower()
        
        for indicator in error_indicators:
            if indicator in summary_lower:
                return False
        
        return True
    
    def truncate_content(self, content: str, max_length: int = 2000) -> str:
        """截断内容到指定长度
        
        Args:
            content: 原始内容
            max_length: 最大长度
            
        Returns:
            str: 截断后的内容
        """
        if len(content) <= max_length:
            return content
        
        # 尝试在句号处截断
        truncated = content[:max_length]
        last_period = truncated.rfind('。')
        if last_period > max_length * 0.8:  # 如果句号位置合理
            return truncated[:last_period + 1]
        
        # 否则直接截断并添加省略号
        return truncated + '...'