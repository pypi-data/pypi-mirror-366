# 核心加密功能
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Tuple, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

from .config import SecurityConfig


class EncryptionCore:
    """加密核心类"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
    
    def aes_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes, tag: bytes = b"", associated_data: bytes = b"") -> bytes:
        """AES解密"""
        if self.config.aes_mode.upper() == "GCM":
            return self._aes_gcm_decrypt(key, iv, ciphertext, tag, associated_data)
        else:
            return self._aes_cbc_decrypt(key, iv, ciphertext)
    
    def aes_encrypt(self, key: bytes, plaintext: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes, bytes]:
        """AES加密"""
        if self.config.aes_mode.upper() == "GCM":
            return self._aes_gcm_encrypt(key, plaintext, associated_data)
        else:
            return self._aes_cbc_encrypt(key, plaintext)
    
    def create_secure_payload(self, data: bytes, aes_key: bytes, hmac_key: bytes, timestamp: int, nonce: bytes) -> Dict[str, str]:
        """创建安全载荷"""
        # 加密数据
        iv, ciphertext, tag = self.aes_encrypt(aes_key, data)
        
        # 创建载荷
        payload = {
            "encrypted_data": base64.b64encode(ciphertext).decode(),
            "iv": base64.b64encode(iv).decode(),
            "timestamp": str(timestamp),
            "nonce": base64.b64encode(nonce).decode()
        }
        
        # 添加标签（GCM模式）
        if tag:
            payload["tag"] = base64.b64encode(tag).decode()
        
        # 计算HMAC签名
        payload_str = json.dumps(payload, sort_keys=True)
        signature = self.hmac_sign(hmac_key, payload_str.encode())
        payload["signature"] = base64.b64encode(signature).decode()
        
        return payload
    
    def generate_aes_key(self) -> bytes:
        """生成AES密钥"""
        return os.urandom(self.config.aes_key_size)
    
    def generate_hmac_key(self) -> bytes:
        """生成HMAC密钥"""
        return os.urandom(32)
    
    def generate_iv(self) -> bytes:
        """生成初始化向量"""
        return os.urandom(16)
    
    def generate_nonce(self) -> bytes:
        """生成随机数"""
        return secrets.token_bytes(16)
    
    def generate_rsa_keypair(self) -> Tuple[bytes, bytes]:
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=self.config.rsa_public_exponent,
            key_size=self.config.rsa_key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # 序列化密钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def hmac_sign(self, key: bytes, data: bytes) -> bytes:
        """HMAC签名"""
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def hmac_verify(self, key: bytes, data: bytes, signature: bytes) -> bool:
        """HMAC验证"""
        expected_signature = self.hmac_sign(key, data)
        return hmac.compare_digest(signature, expected_signature)
    
    def hybrid_decrypt(self, private_key_pem: bytes, encrypted_data: str, encrypted_key: str, hmac_key: bytes) -> bytes:
        """混合解密"""
        # 解密AES密钥
        aes_key = self.rsa_decrypt(private_key_pem, base64.b64decode(encrypted_key))
        
        # 解密数据
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # 对于GCM模式，需要分离tag
        if self.config.aes_mode.upper() == "GCM":
            tag_size = 16
            ciphertext = encrypted_bytes[16:-tag_size]
            tag = encrypted_bytes[-tag_size:]
            return self.aes_decrypt(aes_key, iv, ciphertext, tag)
        else:
            return self.aes_decrypt(aes_key, iv, ciphertext)
    
    def hybrid_encrypt(self, public_key_pem: bytes, data: bytes, hmac_key: bytes) -> Dict[str, str]:
        """混合加密"""
        # 生成AES密钥
        aes_key = self.generate_aes_key()
        
        # 加密数据
        iv, ciphertext, tag = self.aes_encrypt(aes_key, data)
        
        # 加密AES密钥
        encrypted_key = self.rsa_encrypt(public_key_pem, aes_key)
        
        # 组合加密数据
        if self.config.aes_mode.upper() == "GCM":
            encrypted_data = iv + ciphertext + tag
        else:
            encrypted_data = iv + ciphertext
        
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "encrypted_key": base64.b64encode(encrypted_key).decode()
        }
    
    def rsa_decrypt(self, private_key_pem: bytes, ciphertext: bytes) -> bytes:
        """RSA解密"""
        private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    def rsa_encrypt(self, public_key_pem: bytes, plaintext: bytes) -> bytes:
        """RSA加密"""
        public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    def verify_and_decrypt_payload(self, payload: Dict[str, Any], aes_key: bytes, hmac_key: bytes) -> bytes:
        """验证并解密载荷"""
        encrypted_data = base64.b64decode(payload["encrypted_data"])
        timestamp = int(payload["timestamp"])
        nonce = base64.b64decode(payload["nonce"])
        signature = base64.b64decode(payload["signature"])
        
        # 验证时间戳
        current_time = int(time.time())
        if abs(current_time - timestamp) > self.config.max_timestamp_diff:
            raise ValueError("时间戳验证失败")
        
        # 验证签名
        payload_copy = payload.copy()
        payload_copy.pop("signature", None)
        payload_str = json.dumps(payload_copy, sort_keys=True)
        
        if not self.hmac_verify(hmac_key, payload_str.encode(), signature):
            raise ValueError("HMAC签名验证失败")
        
        # 解密数据
        iv = base64.b64decode(payload["iv"])
        tag = base64.b64decode(payload.get("tag", ""))
        
        return self.aes_decrypt(aes_key, iv, encrypted_data, tag)
    
    def _aes_cbc_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
        """AES-CBC解密"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充
        unpadder = crypto_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext
    
    def _aes_cbc_encrypt(self, key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """AES-CBC加密"""
        iv = self.generate_iv()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 添加填充
        padder = crypto_padding.PKCS7(128).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return iv, ciphertext, b""
    
    def _aes_gcm_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes = b"") -> bytes:
        """AES-GCM解密"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    
    def _aes_gcm_encrypt(self, key: bytes, plaintext: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes, bytes]:
        """AES-GCM加密"""
        iv = self.generate_iv()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag
        
        return iv, ciphertext, tag 