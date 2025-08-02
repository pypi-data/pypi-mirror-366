"""缓存管理器模块

负责处理AI摘要的缓存存储、读取和清理功能。
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, enabled: bool = True, expire_days: int = 30, auto_clean: bool = True):
        """初始化缓存管理器
        
        Args:
            enabled: 是否启用缓存
            expire_days: 缓存过期天数
            auto_clean: 是否自动清理过期缓存
        """
        self.enabled = enabled
        self.expire_days = expire_days
        self.auto_clean = auto_clean
        
        # 缓存目录
        self.cache_dir = Path(".ai_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 服务配置文件
        self.service_config_file = self.cache_dir / "service_config.json"
        
        if self.enabled and self.auto_clean:
            self._clean_expired_cache()
    
    def get_cached_summary(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """获取缓存的摘要
        
        Args:
            content_hash: 内容哈希值
            
        Returns:
            dict|None: 缓存的摘要数据，如果没有有效缓存则返回None
        """
        if not self.enabled:
            return None
        
        cache_file = self.cache_dir / f"{content_hash}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '1970-01-01'))
            if (datetime.now() - cache_time).days < self.expire_days:
                return cache_data
            else:
                cache_file.unlink()
                return None
        except Exception:
            # 删除损坏的缓存文件
            cache_file.unlink(missing_ok=True)
            return None
    
    def save_summary_cache(self, content_hash: str, summary_data: Dict[str, Any]) -> None:
        """保存摘要到缓存
        
        Args:
            content_hash: 内容哈希值
            summary_data: 要保存的摘要数据
        """
        if not self.enabled:
            return
        
        cache_file = self.cache_dir / f"{content_hash}.json"
        try:
            summary_data.update({
                'timestamp': datetime.now().isoformat(),
                'cache_version': '1.0.1'
            })
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")
    
    def _clean_expired_cache(self) -> None:
        """清理过期缓存"""
        try:
            current_time = datetime.now()
            expired_count = 0
            
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.name == "service_config.json":
                    continue
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cache_time = datetime.fromisoformat(cache_data.get('timestamp', '1970-01-01'))
                    if (current_time - cache_time).days >= self.expire_days:
                        cache_file.unlink()
                        expired_count += 1
                except Exception:
                    cache_file.unlink()
                    expired_count += 1
            
            if expired_count > 0:
                print(f"🧹 清理了 {expired_count} 个过期缓存文件")
        except Exception as e:
            print(f"⚠️ 清理过期缓存失败: {e}")
    
    def clear_all_cache(self) -> None:
        """清理所有摘要缓存文件
        
        保留配置文件，只清理摘要缓存文件。
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            config_files = ['service_config.json']  # 需要保留的配置文件
            
            cleared_count = 0
            for cache_file in cache_files:
                if cache_file.name not in config_files:
                    cache_file.unlink()
                    cleared_count += 1
            
            if cleared_count > 0:
                print(f"🧹 已清理 {cleared_count} 个缓存文件")
            
        except Exception as e:
            print(f"❌ 清理缓存失败: {e}")
    
    def save_service_config(self, config: Dict[str, Any]) -> None:
        """保存服务配置到文件
        
        Args:
            config: 包含服务和语言配置的字典
        """
        try:
            with open(self.service_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存服务配置失败: {e}")
    
    def load_service_config(self) -> Optional[Dict[str, Any]]:
        """加载服务配置
        
        Returns:
            dict|None: 服务配置数据，如果文件不存在或损坏则返回None
        """
        if not self.service_config_file.exists():
            return None
        
        try:
            with open(self.service_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 读取服务配置失败: {e}")
            return None
    
    def check_service_change(self, current_config: Dict[str, Any]) -> bool:
        """检查AI服务配置变更
        
        Args:
            current_config: 当前配置
            
        Returns:
            bool: True表示配置有变更，False表示无变更
        """
        previous_config = self.load_service_config()
        
        if previous_config is None:
            # 配置文件不存在，首次运行
            self.save_service_config(current_config)
            return True
        
        # 检查关键配置是否变更
        config_changed = (
            previous_config.get('ai_service') != current_config.get('ai_service') or
            previous_config.get('summary_language') != current_config.get('summary_language') or
            previous_config.get('version') != current_config.get('version')
        )
        
        if config_changed:
            # 记录变更详情
            old_service = previous_config.get('ai_service', 'unknown')
            old_lang = previous_config.get('summary_language', 'zh')
            
            print(f"🔄 检测到配置变更:")
            if old_service != current_config.get('ai_service'):
                print(f"   AI服务: {old_service} → {current_config.get('ai_service')}")
            if old_lang != current_config.get('summary_language'):
                print(f"   语言设置: {old_lang} → {current_config.get('summary_language')}")
            
            # 清理所有缓存
            self.clear_all_cache()
            
            # 保存新配置
            self.save_service_config(current_config)
        
        return config_changed