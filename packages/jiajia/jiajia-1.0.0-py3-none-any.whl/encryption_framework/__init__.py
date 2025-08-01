"""
轻量级加密解密框架
提供RSA非对称加密、AES对称加密、HMAC签名验证等功能
可以直接在其他项目中import使用
"""

__version__ = "1.0.0"
__author__ = "开发团队"
__description__ = "轻量级加密解密框架"

# 导入核心类
from .encryption_core import EncryptionCore
from .session_manager import SessionManager
from .config import SecurityConfig
from .encryption_api import EncryptionAPI

# 导入便捷函数
from .utils import (
    encrypt_data,
    decrypt_data,
    key_exchange,
    create_session,
    invalidate_session,
    get_session_info,
    health_check,
    # 同步版本函数
    key_exchange_sync,
    encrypt_data_sync,
    decrypt_data_sync,
    create_session_sync,
    invalidate_session_sync,
    get_session_info_sync,
    health_check_sync
)

__all__ = [
    # 核心类
    "EncryptionCore",
    "SessionManager", 
    "SecurityConfig",
    "EncryptionAPI",
    
    # 异步便捷函数
    "encrypt_data",
    "decrypt_data", 
    "key_exchange",
    "create_session",
    "invalidate_session",
    "get_session_info",
    "health_check",
    
    # 同步便捷函数
    "key_exchange_sync",
    "encrypt_data_sync",
    "decrypt_data_sync",
    "create_session_sync",
    "invalidate_session_sync",
    "get_session_info_sync",
    "health_check_sync"
]

# 全局API实例
_api_instance = None

def get_api(config=None):
    """获取全局API实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = EncryptionAPI(config)
    return _api_instance

def set_config(config):
    """设置全局配置"""
    global _api_instance
    _api_instance = EncryptionAPI(config) 