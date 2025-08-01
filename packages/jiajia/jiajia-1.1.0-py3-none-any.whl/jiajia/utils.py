# 便捷函数模块
# 提供简单的使用接口
import asyncio
from typing import Any, Dict, Optional

from .config import SecurityConfig
from .encryption_api import EncryptionAPI

# 全局API实例
_api_instance = None


def _get_api(config=None) -> EncryptionAPI:
    """获取API实例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = EncryptionAPI(config)
    return _api_instance


def set_config(config: SecurityConfig):
    """设置全局配置"""
    global _api_instance
    _api_instance = EncryptionAPI(config)


# 异步便捷函数
async def create_session(client_id: str, client_version: str = None, config: SecurityConfig = None) -> Dict[str, Any]:
    """创建会话（便捷函数）"""
    api = _get_api(config)
    return await api.key_exchange(client_id, client_version)


async def decrypt_data(request_data: Dict[str, Any], config: SecurityConfig = None) -> Dict[str, Any]:
    """解密数据（便捷函数）"""
    api = _get_api(config)
    return await api.decrypt_data(request_data)


async def encrypt_data(data: Dict[str, Any], session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """加密数据（便捷函数）"""
    api = _get_api(config)
    return await api.encrypt_data(data, session_id)


async def get_session_info(session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """获取会话信息（便捷函数）"""
    api = _get_api(config)
    return await api.get_session_info(session_id)


async def health_check(config: SecurityConfig = None) -> Dict[str, Any]:
    """健康检查（便捷函数）"""
    api = _get_api(config)
    return await api.health_check()


async def invalidate_session(session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """使会话失效（便捷函数）"""
    api = _get_api(config)
    return await api.invalidate_session(session_id)


async def key_exchange(client_id: str, client_version: str = None, config: SecurityConfig = None) -> Dict[str, Any]:
    """密钥交换（便捷函数）"""
    api = _get_api(config)
    return await api.key_exchange(client_id, client_version)


# 同步版本的便捷函数
def create_session_sync(client_id: str, client_version: str = None, config: SecurityConfig = None) -> Dict[str, Any]:
    """创建会话（同步版本）"""
    return asyncio.run(create_session(client_id, client_version, config))


def decrypt_data_sync(request_data: Dict[str, Any], config: SecurityConfig = None) -> Dict[str, Any]:
    """解密数据（同步版本）"""
    return asyncio.run(decrypt_data(request_data, config))


def encrypt_data_sync(data: Dict[str, Any], session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """加密数据（同步版本）"""
    return asyncio.run(encrypt_data(data, session_id, config))


def get_session_info_sync(session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """获取会话信息（同步版本）"""
    return asyncio.run(get_session_info(session_id, config))


def health_check_sync(config: SecurityConfig = None) -> Dict[str, Any]:
    """健康检查（同步版本）"""
    return asyncio.run(health_check(config))


def invalidate_session_sync(session_id: str, config: SecurityConfig = None) -> Dict[str, Any]:
    """使会话失效（同步版本）"""
    return asyncio.run(invalidate_session(session_id, config))


def key_exchange_sync(client_id: str, client_version: str = None, config: SecurityConfig = None) -> Dict[str, Any]:
    """密钥交换（同步版本）"""
    return asyncio.run(key_exchange(client_id, client_version, config)) 