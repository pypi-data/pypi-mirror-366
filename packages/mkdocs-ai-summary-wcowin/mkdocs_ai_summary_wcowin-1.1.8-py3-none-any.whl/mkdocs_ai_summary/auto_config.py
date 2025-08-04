"""自动配置模块

在插件首次安装时自动生成配置文件，简化用户配置过程。
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class AutoConfigManager:
    """自动配置管理器"""
    
    def __init__(self, project_root: Optional[str] = None):
        """初始化自动配置管理器
        
        Args:
            project_root: 项目根目录路径，如果为None则自动检测
        """
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.env_file = self.project_root / '.env'
        self.mkdocs_file = self.project_root / 'mkdocs.yml'
    
    def _find_project_root(self) -> Path:
        """查找项目根目录
        
        Returns:
            Path: 项目根目录路径
        """
        # 从当前工作目录开始向上查找mkdocs.yml文件
        current = Path.cwd()
        while current != current.parent:
            if (current / 'mkdocs.yml').exists():
                return current
            current = current.parent
        
        # 如果没找到，返回当前工作目录
        return Path.cwd()
    
    def check_and_create_env_file(self, debug: bool = False) -> bool:
        """检查并创建.env文件
        
        Args:
            debug: 是否显示调试信息
            
        Returns:
            bool: 是否创建了新的.env文件
        """
        if self.env_file.exists():
            if debug:
                print(f"📄 .env文件已存在: {self.env_file}")
            return False
        
        # 创建.env文件模板
        env_template = self._get_env_template()
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_template)
            
            if debug:
                print(f"✅ 已创建.env文件模板: {self.env_file}")
                print("💡 请编辑.env文件并填入您的API密钥")
            
            return True
            
        except Exception as e:
            if debug:
                print(f"❌ 创建.env文件失败: {e}")
            return False
    
    def _get_env_template(self) -> str:
        """获取.env文件模板内容
        
        Returns:
            str: .env文件模板内容
        """
        return """# MkDocs AI Summary Plugin 环境变量配置
# 请填入您的API密钥，至少需要配置一个服务

# DeepSeek API 配置 (推荐)
# 获取地址: https://platform.deepseek.com/
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# OpenAI API 配置
# 获取地址: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API 配置
# 获取地址: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# 智谱GLM API 配置
# 获取地址: https://open.bigmodel.cn/
GLM_API_KEY=your_glm_api_key_here

# 注意事项:
# 1. 请确保 .env 文件已添加到 .gitignore 中，避免泄露API密钥
# 2. 至少需要配置一个AI服务的API密钥
# 3. 建议配置多个服务作为备用，提高可用性
# 4. 配置完成后重新运行 mkdocs serve 或 mkdocs build
"""
    
    def check_and_add_plugin_config(self, debug: bool = False) -> bool:
        """检查并添加插件配置到mkdocs.yml
        
        Args:
            debug: 是否显示调试信息
            
        Returns:
            bool: 是否添加了新的配置
        """
        if not self.mkdocs_file.exists():
            if debug:
                print(f"❌ 未找到mkdocs.yml文件: {self.mkdocs_file}")
            return False
        
        try:
            # 读取现有配置
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析YAML
            config = yaml.safe_load(content) or {}
            
            # 检查是否已有ai-summary配置
            plugins = config.get('plugins', [])
            
            # 检查插件列表中是否已有ai-summary
            has_ai_summary = False
            for plugin in plugins:
                if isinstance(plugin, dict) and 'ai-summary' in plugin:
                    has_ai_summary = True
                    break
                elif isinstance(plugin, str) and plugin == 'ai-summary':
                    has_ai_summary = True
                    break
            
            if has_ai_summary:
                if debug:
                    print("📄 mkdocs.yml中已存在ai-summary配置")
                return False
            
            # 添加ai-summary配置
            ai_summary_config = self._get_plugin_config_template()
            
            # 确保plugins是列表
            if not isinstance(plugins, list):
                plugins = []
            
            # 添加ai-summary配置
            plugins.append({'ai-summary': ai_summary_config})
            config['plugins'] = plugins
            
            # 写回文件，尽量保持原有格式
            self._write_mkdocs_config(config, ai_summary_config)
            
            if debug:
                print(f"✅ 已添加ai-summary配置到mkdocs.yml")
                print("💡 请根据需要调整配置参数")
            
            return True
            
        except Exception as e:
            if debug:
                print(f"❌ 处理mkdocs.yml失败: {e}")
            return False
    
    def _get_plugin_config_template(self) -> Dict[str, Any]:
        """获取插件配置模板
        
        Returns:
            Dict[str, Any]: 插件配置字典
        """
        return {
            'ai_service': 'deepseek',  # 默认使用deepseek
            'fallback_services': ['openai', 'gemini', 'glm'],  # 备用服务
            'summary_language': 'zh',  # 摘要语言
            'cache_enabled': True,  # 启用缓存
            'local_enabled': True,  # 本地环境启用
            'cache_expire_days': 30,  # 缓存过期天数
            'debug': False,  # 调试模式
            'enabled_folders': ['docs/'],  # 启用的文件夹
            'exclude_patterns': ['index.md', 'tag.md']  # 排除的文件模式
        }
    
    def _write_mkdocs_config(self, config: Dict[str, Any], ai_summary_config: Dict[str, Any]) -> None:
        """写入mkdocs.yml配置，尽量保持原有格式
        
        Args:
            config: 完整的配置字典
            ai_summary_config: ai-summary插件配置
        """
        try:
            # 读取原始文件内容
            with open(self.mkdocs_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 生成ai-summary配置的YAML字符串
            ai_summary_yaml = yaml.dump(
                {'ai-summary': ai_summary_config}, 
                default_flow_style=False, 
                allow_unicode=True, 
                indent=2
            ).strip()
            
            # 格式化ai-summary配置
            ai_summary_lines = ai_summary_yaml.split('\n')
            # 将第一行改为插件列表格式
            ai_summary_lines[0] = '- ai-summary:'
            ai_summary_content = '\n'.join(ai_summary_lines)
            
            # 查找plugins部分
            lines = original_content.split('\n')
            new_lines = []
            plugins_found = False
            plugins_indent = 0
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # 检查是否是plugins行
                if line.strip() == 'plugins:' or line.strip().startswith('plugins:'):
                    plugins_found = True
                    plugins_indent = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    
                    # 添加现有的插件配置
                    i += 1
                    while i < len(lines) and (lines[i].strip() == '' or len(lines[i]) - len(lines[i].lstrip()) > plugins_indent):
                        new_lines.append(lines[i])
                        i += 1
                    
                    # 添加ai-summary配置
                    for config_line in ai_summary_content.split('\n'):
                        new_lines.append(' ' * (plugins_indent + 2) + config_line.strip())
                    
                    # 继续处理剩余行
                    i -= 1  # 回退一行，因为循环会自动+1
                else:
                    new_lines.append(line)
                
                i += 1
            
            # 如果没有找到plugins部分，在文件末尾添加
            if not plugins_found:
                new_lines.append('')
                new_lines.append('plugins:')
                for config_line in ai_summary_content.split('\n'):
                    new_lines.append('  ' + config_line.strip())
            
            # 写回文件
            with open(self.mkdocs_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
                
        except Exception:
            # 如果格式化失败，使用简单的YAML dump
            with open(self.mkdocs_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    def run_auto_config(self, debug: bool = False) -> Dict[str, bool]:
        """运行自动配置
        
        Args:
            debug: 是否显示调试信息
            
        Returns:
            Dict[str, bool]: 配置结果 {'env_created': bool, 'config_added': bool}
        """
        if debug:
            print("🔧 开始自动配置...")
        
        results = {
            'env_created': self.check_and_create_env_file(debug),
            'config_added': self.check_and_add_plugin_config(debug)
        }
        
        if debug:
            if results['env_created'] or results['config_added']:
                print("🎉 自动配置完成！")
                if results['env_created']:
                    print("📝 下一步: 编辑.env文件并填入您的API密钥")
                if results['config_added']:
                    print("📝 下一步: 根据需要调整mkdocs.yml中的ai-summary配置")
            else:
                print("ℹ️ 配置文件已存在，跳过自动配置")
        
        return results
    
    def check_gitignore(self, debug: bool = False) -> bool:
        """检查并更新.gitignore文件
        
        Args:
            debug: 是否显示调试信息
            
        Returns:
            bool: 是否更新了.gitignore
        """
        gitignore_file = self.project_root / '.gitignore'
        
        # 如果.gitignore不存在，创建一个
        if not gitignore_file.exists():
            try:
                with open(gitignore_file, 'w', encoding='utf-8') as f:
                    f.write("# Environment variables\n.env\n")
                if debug:
                    print(f"✅ 已创建.gitignore文件: {gitignore_file}")
                return True
            except Exception as e:
                if debug:
                    print(f"❌ 创建.gitignore失败: {e}")
                return False
        
        # 检查.gitignore中是否已包含.env
        try:
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '.env' in content:
                if debug:
                    print("📄 .gitignore中已包含.env")
                return False
            
            # 添加.env到.gitignore
            with open(gitignore_file, 'a', encoding='utf-8') as f:
                f.write("\n# Environment variables\n.env\n")
            
            if debug:
                print(f"✅ 已添加.env到.gitignore")
            return True
            
        except Exception as e:
            if debug:
                print(f"❌ 处理.gitignore失败: {e}")
            return False