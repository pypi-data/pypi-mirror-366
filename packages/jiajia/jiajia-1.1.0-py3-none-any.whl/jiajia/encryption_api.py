# 统一加密API接口
import base64
import json
import time
from typing import Any, Dict, Optional

from .config import SecurityConfig
from .encryption_core import EncryptionCore
from .session_manager import SessionManager


class EncryptionAPI:
    """统一加密API"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.encryption_core = EncryptionCore(self.config)
        self.session_manager = SessionManager(self.config)
    
    async def key_exchange(self, client_id: str, client_version: str = None) -> Dict[str, Any]:
        """密钥交换"""
        try:
            # 创建会话
            session_info = await self.session_manager.create_session(client_id, client_version)
            session_id = session_info["session_id"]
            
            # 生成RSA密钥对
            private_key_pem, public_key_pem = self.encryption_core.generate_rsa_keypair()
            
            # 生成HMAC密钥
            hmac_key = self.encryption_core.generate_hmac_key()
            
            # 存储私钥和HMAC密钥
            await self.session_manager.store_keys(
                session_id,
                private_key_pem.decode(),
                base64.b64encode(hmac_key).decode()
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "public_key": public_key_pem.decode(),
                "hmac_key": base64.b64encode(hmac_key).decode(),
                "server_timestamp": int(time.time()),
                "session_info": session_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def encrypt_data(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """加密数据"""
        try:
            # 验证会话
            if not await self.session_manager.is_session_valid(session_id):
                return {
                    "success": False,
                    "error": "会话无效或已过期"
                }
            
            # 获取HMAC密钥
            hmac_key_b64 = await self.session_manager.get_hmac_key(session_id)
            if not hmac_key_b64:
                return {
                    "success": False,
                    "error": "HMAC密钥未找到"
                }
            
            hmac_key = base64.b64decode(hmac_key_b64)
            
            # 序列化数据
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # 生成时间戳和随机数
            timestamp = int(time.time())
            nonce = self.encryption_core.generate_nonce()
            
            # 生成AES密钥并存储
            aes_key = self.encryption_core.generate_aes_key()
            await self.session_manager.store_aes_key(
                session_id, 
                base64.b64encode(aes_key).decode()
            )
            
            # 创建安全载荷
            payload = self.encryption_core.create_secure_payload(
                data_bytes, 
                aes_key, 
                hmac_key, 
                timestamp, 
                nonce
            )
            
            # 更新会话活动
            await self.session_manager.update_session_activity(session_id)
            
            # 返回结果，不修改原始载荷
            result = {
                "success": True,
                "session_id": session_id
            }
            result.update(payload)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def decrypt_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """解密数据"""
        try:
            session_id = request_data.get("session_id")
            if not session_id:
                return {
                    "success": False,
                    "error": "缺少会话ID"
                }
            
            # 验证会话
            if not await self.session_manager.is_session_valid(session_id):
                return {
                    "success": False,
                    "error": "会话无效或已过期"
                }
            
            # 获取HMAC密钥和AES密钥
            hmac_key_b64 = await self.session_manager.get_hmac_key(session_id)
            aes_key_b64 = await self.session_manager.get_aes_key(session_id)
            
            if not hmac_key_b64 or not aes_key_b64:
                return {
                    "success": False,
                    "error": "密钥未找到"
                }
            
            hmac_key = base64.b64decode(hmac_key_b64)
            aes_key = base64.b64decode(aes_key_b64)
            
            # 创建用于验证的载荷副本，移除额外字段
            payload_for_verification = request_data.copy()
            payload_for_verification.pop("success", None)
            payload_for_verification.pop("session_id", None)
            
            # 验证并解密数据
            decrypted_bytes = self.encryption_core.verify_and_decrypt_payload(
                payload_for_verification,
                aes_key,
                hmac_key
            )
            
            # 反序列化数据
            data = json.loads(decrypted_bytes.decode('utf-8'))
            
            # 更新会话活动
            await self.session_manager.update_session_activity(session_id)
            
            return {
                "success": True,
                "data": data,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def invalidate_session(self, session_id: str) -> Dict[str, Any]:
        """使会话失效"""
        try:
            success = await self.session_manager.invalidate_session(session_id)
            return {
                "success": success,
                "session_id": session_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        try:
            session_info = await self.session_manager.get_session_info(session_id)
            if session_info:
                return {
                    "success": True,
                    "session_info": session_info
                }
            else:
                return {
                    "success": False,
                    "error": "会话不存在"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        try:
            session_stats = await self.session_manager.get_session_stats()
            
            return {
                "success": True,
                "security_config": self.config.to_dict(),
                "session_stats": session_stats,
                "supported_algorithms": {
                    "rsa": ["2048", "4096"],
                    "aes": ["GCM", "CBC"],
                    "hmac": ["sha256", "sha512"]
                },
                "security_level": "high"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试基本功能
            test_data = {"test": "health_check"}
            test_result = await self.encrypt_data(test_data, "health_check_session")
            
            return {
                "success": True,
                "status": "healthy",
                "components": {
                    "encryption_core": "ok",
                    "session_manager": "ok",
                    "cache_backend": self.config.cache_backend
                },
                "timestamp": int(time.time())
            }
        except Exception as e:
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": int(time.time())
            } 