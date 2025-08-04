#!/usr/bin/env python3
"""MkDocs AI Summary Plugin 命令行工具

提供独立的初始化命令，用于首次安装后的自动配置。
"""

import sys
import argparse
from pathlib import Path
from .auto_config import AutoConfigManager


def init_command():
    """初始化命令：自动配置.env文件和mkdocs.yml"""
    print("🚀 MkDocs AI Summary Plugin 初始化工具")
    print("=" * 50)
    
    try:
        # 创建自动配置管理器
        auto_config = AutoConfigManager()
        
        print(f"📁 项目根目录: {auto_config.project_root}")
        print()
        
        # 运行自动配置
        results = auto_config.run_auto_config(debug=True)
        
        # 检查.gitignore
        if results['env_created']:
            auto_config.check_gitignore(debug=True)
        
        print()
        print("=" * 50)
        
        if results['env_created'] or results['config_added']:
            print("🎉 初始化完成！")
            print()
            
            if results['env_created']:
                print("📝 下一步操作:")
                print(f"   1. 编辑 {auto_config.env_file} 文件")
                print("   2. 填入您的AI服务API密钥")
                print("   3. 至少配置一个服务的API密钥")
                print()
            
            if results['config_added']:
                print("⚙️ 配置说明:")
                print(f"   - 已在 {auto_config.mkdocs_file} 中添加ai-summary插件配置")
                print("   - 您可以根据需要调整配置参数")
                print()
            
            print("🔗 获取API密钥:")
            print("   • DeepSeek (推荐): https://platform.deepseek.com/")
            print("   • OpenAI: https://platform.openai.com/api-keys")
            print("   • Google Gemini: https://makersuite.google.com/app/apikey")
            print("   • 智谱GLM: https://open.bigmodel.cn/")
            print()
            
            print("🚀 完成配置后运行:")
            print("   mkdocs serve  # 启动开发服务器")
            print("   mkdocs build  # 构建静态站点")
            
        else:
            print("ℹ️ 配置文件已存在，无需重新初始化")
            print("💡 如需重新配置，请手动删除相关文件后重新运行")
        
        return 0
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("💡 请检查当前目录是否为MkDocs项目根目录")
        return 1


def status_command():
    """状态命令：检查当前配置状态"""
    print("📊 MkDocs AI Summary Plugin 配置状态")
    print("=" * 50)
    
    try:
        auto_config = AutoConfigManager()
        
        print(f"📁 项目根目录: {auto_config.project_root}")
        print()
        
        # 检查.env文件
        if auto_config.env_file.exists():
            print("✅ .env文件: 已存在")
            
            # 检查API密钥配置
            try:
                from dotenv import load_dotenv
                import os
                
                load_dotenv(auto_config.env_file)
                
                services = {
                    'DEEPSEEK_API_KEY': 'DeepSeek',
                    'OPENAI_API_KEY': 'OpenAI',
                    'GOOGLE_API_KEY': 'Google Gemini',
                    'GLM_API_KEY': '智谱GLM'
                }
                
                configured_services = []
                for key, name in services.items():
                    value = os.getenv(key)
                    if value and value != f'your_{key.lower()}_here':
                        configured_services.append(name)
                
                if configured_services:
                    print(f"   已配置的服务: {', '.join(configured_services)}")
                else:
                    print("   ⚠️ 未检测到有效的API密钥配置")
                    
            except Exception:
                print("   ⚠️ 无法读取API密钥配置")
        else:
            print("❌ .env文件: 不存在")
        
        # 检查mkdocs.yml配置
        if auto_config.mkdocs_file.exists():
            print("✅ mkdocs.yml文件: 已存在")
            
            try:
                import yaml
                with open(auto_config.mkdocs_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                plugins = config.get('plugins', [])
                has_ai_summary = False
                
                for plugin in plugins:
                    if isinstance(plugin, dict) and 'ai-summary' in plugin:
                        has_ai_summary = True
                        break
                    elif isinstance(plugin, str) and plugin == 'ai-summary':
                        has_ai_summary = True
                        break
                
                if has_ai_summary:
                    print("   ✅ ai-summary插件: 已配置")
                else:
                    print("   ❌ ai-summary插件: 未配置")
                    
            except Exception:
                print("   ⚠️ 无法解析mkdocs.yml配置")
        else:
            print("❌ mkdocs.yml文件: 不存在")
        
        print()
        print("💡 如需重新初始化，请运行: mkdocs-ai-summary-init")
        
        return 0
        
    except Exception as e:
        print(f"❌ 检查状态失败: {e}")
        return 1


def init_entry_point():
    """命令行入口点（用于setup.py）"""
    parser = argparse.ArgumentParser(
        description='MkDocs AI Summary Plugin 初始化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用示例:
  mkdocs-ai-summary-init          # 运行自动配置
  mkdocs-ai-summary-init --status # 检查配置状态
        """
    )
    
    parser.add_argument(
        '--status', 
        action='store_true', 
        help='检查当前配置状态'
    )
    
    args = parser.parse_args()
    
    if args.status:
        status_command()
    else:
        init_command()


def main():
    """主入口点（向后兼容）"""
    init_entry_point()


if __name__ == '__main__':
    main()