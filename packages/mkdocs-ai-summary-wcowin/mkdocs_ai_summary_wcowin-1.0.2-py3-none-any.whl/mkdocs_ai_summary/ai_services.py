"""AI服务管理器模块

负责管理多种AI服务的调用和降级处理。
"""

import os
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class AIServiceManager:
    """AI服务管理器"""
    
    def __init__(self, default_service: str, model: str, max_tokens: int, temperature: float):
        """初始化AI服务管理器
        
        Args:
            default_service: 默认AI服务名称
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        self.default_service = default_service
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # AI服务配置
        self.ai_services = {
            'deepseek': {
                'url': 'https://api.deepseek.com/v1/chat/completions',
                'model': 'deepseek-chat',
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
            },
            'openai': {
                'url': 'https://api.chatanywhere.tech/v1/chat/completions',
                'model': 'gpt-3.5-turbo',
                'api_key': os.getenv('OPENAI_API_KEY'),
            },
            'gemini': {
                'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
                'model': 'gemini-pro',
                'api_key': os.getenv('GOOGLE_API_KEY'),
            },
            'glm': {
                'url': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                'model': 'glm-4-flash',
                'api_key': os.getenv('GLM_API_KEY'),
            }
        }
        
        # 服务降级顺序
        self.fallback_order = ['openai', 'glm', 'deepseek', 'gemini']
    
    def generate_summary(self, content: str, title: str) -> Optional[Dict[str, Any]]:
        """生成AI摘要
        
        Args:
            content: 页面内容
            title: 页面标题
            
        Returns:
            dict|None: 包含摘要和服务信息的字典，失败时返回None
        """
        # 首先尝试默认服务
        result = self._try_service(self.default_service, content, title)
        if result:
            return result
        
        # 如果默认服务失败，按降级顺序尝试其他服务
        for service_name in self.fallback_order:
            if service_name != self.default_service:
                result = self._try_service(service_name, content, title)
                if result:
                    return result
        
        return None
    
    def _try_service(self, service_name: str, content: str, title: str) -> Optional[Dict[str, Any]]:
        """尝试调用指定的AI服务
        
        Args:
            service_name: 服务名称
            content: 页面内容
            title: 页面标题
            
        Returns:
            dict|None: 包含摘要和服务信息的字典，失败时返回None
        """
        service_config = self.ai_services.get(service_name)
        if not service_config or not service_config.get('api_key'):
            return None
        
        try:
            if service_name == 'gemini':
                return self._call_gemini_api(service_config, content, title)
            else:
                return self._call_openai_compatible_api(service_config, content, title, service_name)
        except Exception as e:
            print(f"⚠️ {service_name} 服务调用失败: {e}")
            return None
    
    def _call_openai_compatible_api(self, config: Dict, content: str, title: str, service_name: str) -> Dict[str, Any]:
        """调用OpenAI兼容的API
        
        Args:
            config: 服务配置
            content: 页面内容
            title: 页面标题
            service_name: 服务名称
            
        Returns:
            dict: 包含摘要和服务信息的字典
        """
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        prompt = self._build_prompt(content, title)
        
        data = {
            'model': config['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
        
        response = requests.post(config['url'], headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        
        return {
            'summary': summary,
            'service': service_name
        }
    
    def _call_gemini_api(self, config: Dict, content: str, title: str) -> Dict[str, Any]:
        """调用Gemini API
        
        Args:
            config: 服务配置
            content: 页面内容
            title: 页面标题
            
        Returns:
            dict: 包含摘要和服务信息的字典
        """
        url = f"{config['url']}?key={config['api_key']}"
        
        headers = {'Content-Type': 'application/json'}
        
        prompt = self._build_prompt(content, title)
        
        data = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'maxOutputTokens': self.max_tokens,
                'temperature': self.temperature
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        summary = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        return {
            'summary': summary,
            'service': 'gemini'
        }
    
    def _build_prompt(self, content: str, title: str) -> str:
        """构建AI提示词
        
        Args:
            content: 页面内容
            title: 页面标题
            
        Returns:
            str: 构建好的提示词
        """
        return f"""请为以下文档生成一个简洁的摘要（100-150字）：

标题：{title}

内容：
{content[:2000]}  # 限制内容长度

要求：
1. 用中文回答
2. 突出文档的核心要点
3. 语言简洁明了
4. 不要包含无关信息"""
    
    def get_available_services(self) -> list:
        """获取可用的AI服务列表
        
        Returns:
            list: 有API密钥的服务名称列表
        """
        available = []
        for service_name, config in self.ai_services.items():
            if config.get('api_key'):
                available.append(service_name)
        return available
    
    def validate_service_config(self) -> bool:
        """验证服务配置
        
        Returns:
            bool: True表示至少有一个服务可用，False表示没有可用服务
        """
        available_services = self.get_available_services()
        if not available_services:
            print("⚠️ 没有可用的AI服务，请检查API密钥配置")
            return False
        
        if self.default_service not in available_services:
            print(f"⚠️ 默认服务 {self.default_service} 不可用，将使用 {available_services[0]}")
            self.default_service = available_services[0]
        
        return True