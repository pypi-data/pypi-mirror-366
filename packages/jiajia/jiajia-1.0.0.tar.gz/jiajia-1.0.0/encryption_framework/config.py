"""
配置管理
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SecurityConfig:
    """安全配置类"""
    # RSA配置
    rsa_key_size: int = 2048
    rsa_public_exponent: int = 65537
    
    # AES配置
    aes_key_size: int = 32  # 256位
    aes_mode: str = "GCM"  # GCM或CBC
    
    # HMAC配置
    hmac_algorithm: str = "sha256"
    
    # 会话配置
    session_expire_time: int = 3600  # 秒
    max_timestamp_diff: int = 300  # 秒
    
    # 缓存配置
    cache_backend: str = "memory"  # memory或redis
    redis_url: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    enable_logging: bool = True
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """从环境变量加载配置"""
        return cls(
            rsa_key_size=int(os.getenv("RSA_KEY_SIZE", "2048")),
            aes_key_size=int(os.getenv("AES_KEY_SIZE", "32")),
            aes_mode=os.getenv("AES_MODE", "GCM"),
            session_expire_time=int(os.getenv("SESSION_EXPIRE_TIME", "3600")),
            max_timestamp_diff=int(os.getenv("MAX_TIMESTAMP_DIFF", "300")),
            cache_backend=os.getenv("CACHE_BACKEND", "memory"),
            redis_url=os.getenv("REDIS_URL"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            enable_logging=os.getenv("ENABLE_LOGGING", "true").lower() == "true"
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "rsa_key_size": self.rsa_key_size,
            "aes_key_size": self.aes_key_size,
            "aes_mode": self.aes_mode,
            "hmac_algorithm": self.hmac_algorithm,
            "session_expire_time": self.session_expire_time,
            "max_timestamp_diff": self.max_timestamp_diff,
            "cache_backend": self.cache_backend,
            "log_level": self.log_level,
            "enable_logging": self.enable_logging
        }


# 默认配置
default_config = SecurityConfig() 