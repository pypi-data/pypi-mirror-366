"""Utility functions for MkDocs AI Summary Plugin"""

import os
import re
from typing import List, Optional


def get_ci_name() -> str:
    """获取CI环境名称"""
    ci_mapping = {
        'GITHUB_ACTIONS': 'GitHub Actions',
        'GITLAB_CI': 'GitLab CI',
        'JENKINS_URL': 'Jenkins',
        'TRAVIS': 'Travis CI',
        'CIRCLECI': 'CircleCI',
        'AZURE_HTTP_USER_AGENT': 'Azure DevOps',
        'TEAMCITY_VERSION': 'TeamCity',
        'BUILDKITE': 'Buildkite',
        'CODEBUILD_BUILD_ID': 'AWS CodeBuild',
        'NETLIFY': 'Netlify',
        'VERCEL': 'Vercel',
        'CF_PAGES': 'Cloudflare Pages'
    }
    
    for env_var, name in ci_mapping.items():
        if os.getenv(env_var):
            return name
    
    return 'Unknown CI'


def clean_markdown_content(content: str) -> str:
    """清理Markdown内容，移除格式化元素"""
    # 移除代码块
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'`[^`]+`', '', content)
    
    # 移除图片
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # 移除链接，保留文本
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # 移除HTML标签
    content = re.sub(r'<[^>]+>', '', content)
    
    # 移除Markdown标题标记
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    
    # 移除列表标记
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
    
    # 清理多余空白
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = content.strip()
    
    return content


def validate_api_key(api_key: Optional[str]) -> bool:
    """验证API密钥格式"""
    if not api_key:
        return False
    
    # 基本长度检查
    if len(api_key) < 10:
        return False
    
    # 检查是否包含明显的占位符
    placeholders = ['your_api_key', 'api_key_here', 'replace_me', 'xxx']
    if api_key.lower() in placeholders:
        return False
    
    return True


def truncate_content(content: str, max_length: int = 2000) -> str:
    """截断内容到指定长度"""
    if len(content) <= max_length:
        return content
    
    # 尝试在句号处截断
    truncated = content[:max_length]
    last_period = truncated.rfind('。')
    if last_period > max_length * 0.8:  # 如果句号位置合理
        return truncated[:last_period + 1]
    
    # 否则直接截断并添加省略号
    return truncated + '...'


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def is_valid_folder_path(path: str) -> bool:
    """验证文件夹路径格式"""
    if not path:
        return False
    
    # 检查路径是否以/结尾（文件夹标识）
    if not path.endswith('/'):
        return False
    
    # 检查是否包含非法字符
    illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in path for char in illegal_chars):
        return False
    
    return True