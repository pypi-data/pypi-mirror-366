"""
核心加密功能
"""
import os
import base64
import json
import time
import secrets
import hmac
import hashlib
from typing import Tuple, Optional, Dict, Any, Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

from .config import SecurityConfig


class EncryptionCore:
    """加密核心类"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
    
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
    
    def rsa_decrypt(self, private_key_pem: bytes, ciphertext: bytes) -> bytes:
        """RSA解密"""
        private_key = serialization.load_pem_private_key(private_key_pem, backend=default_backend())
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    def generate_aes_key(self) -> bytes:
        """生成AES密钥"""
        return os.urandom(self.config.aes_key_size)
    
    def generate_nonce(self) -> bytes:
        """生成随机数"""
        return secrets.token_bytes(16)
    
    def generate_iv(self) -> bytes:
        """生成初始化向量"""
        return os.urandom(16)
    
    def aes_encrypt(self, key: bytes, plaintext: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes, bytes]:
        """AES加密"""
        if self.config.aes_mode.upper() == "GCM":
            return self._aes_gcm_encrypt(key, plaintext, associated_data)
        else:
            return self._aes_cbc_encrypt(key, plaintext)
    
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
    
    def _aes_cbc_encrypt(self, key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """AES-CBC加密"""
        iv = self.generate_iv()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # PKCS7填充
        padder = crypto_padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv, ciphertext, b""  # CBC模式没有tag
    
    def aes_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes, tag: bytes = b"", associated_data: bytes = b"") -> bytes:
        """AES解密"""
        if self.config.aes_mode.upper() == "GCM":
            return self._aes_gcm_decrypt(key, iv, ciphertext, tag, associated_data)
        else:
            return self._aes_cbc_decrypt(key, iv, ciphertext)
    
    def _aes_gcm_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes = b"") -> bytes:
        """AES-GCM解密"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    
    def _aes_cbc_decrypt(self, key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
        """AES-CBC解密"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除PKCS7填充
        unpadder = crypto_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext
    
    def generate_hmac_key(self) -> bytes:
        """生成HMAC密钥"""
        return os.urandom(32)
    
    def hmac_sign(self, key: bytes, data: bytes) -> bytes:
        """HMAC签名"""
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def hmac_verify(self, key: bytes, data: bytes, signature: bytes) -> bool:
        """HMAC验证"""
        expected_signature = self.hmac_sign(key, data)
        return hmac.compare_digest(signature, expected_signature)
    
    def create_secure_payload(self, data: bytes, aes_key: bytes, hmac_key: bytes, timestamp: int, nonce: bytes) -> Dict[str, str]:
        """创建安全载荷"""
        # 加密数据
        iv, ciphertext, tag = self.aes_encrypt(aes_key, data)
        
        # 组合加密数据
        encrypted_data = iv + ciphertext + tag
        
        # 创建签名数据
        signature_data = f"{base64.b64encode(encrypted_data).decode()}:{timestamp}:{base64.b64encode(nonce).decode()}"
        signature = self.hmac_sign(hmac_key, signature_data.encode())
        
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "timestamp": str(timestamp),
            "nonce": base64.b64encode(nonce).decode(),
            "signature": base64.b64encode(signature).decode()
        }
    
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
        signature_data = f"{payload['encrypted_data']}:{timestamp}:{payload['nonce']}"
        if not self.hmac_verify(hmac_key, signature_data.encode(), signature):
            raise ValueError("签名验证失败")
        
        # 解密数据
        iv_size = 16
        tag_size = 16 if self.config.aes_mode.upper() == "GCM" else 0
        
        iv = encrypted_data[:iv_size]
        ciphertext = encrypted_data[iv_size:-tag_size] if tag_size > 0 else encrypted_data[iv_size:]
        tag = encrypted_data[-tag_size:] if tag_size > 0 else b""
        
        return self.aes_decrypt(aes_key, iv, ciphertext, tag)
    
    def hybrid_encrypt(self, public_key_pem: bytes, data: bytes, hmac_key: bytes) -> Dict[str, str]:
        """混合加密"""
        # 生成AES密钥
        aes_key = self.generate_aes_key()
        
        # 用RSA加密AES密钥
        encrypted_key = self.rsa_encrypt(public_key_pem, aes_key)
        
        # 用AES加密数据
        timestamp = int(time.time())
        nonce = self.generate_nonce()
        
        payload = self.create_secure_payload(data, aes_key, hmac_key, timestamp, nonce)
        payload["encrypted_key"] = base64.b64encode(encrypted_key).decode()
        
        return payload
    
    def hybrid_decrypt(self, private_key_pem: bytes, encrypted_data: str, encrypted_key: str, hmac_key: bytes) -> bytes:
        """混合解密"""
        # 解密AES密钥
        aes_key = self.rsa_decrypt(private_key_pem, base64.b64decode(encrypted_key))
        
        # 解密数据
        payload = {
            "encrypted_data": encrypted_data,
            "timestamp": str(int(time.time())),
            "nonce": base64.b64encode(self.generate_nonce()).decode(),
            "signature": base64.b64encode(self.hmac_sign(hmac_key, b"dummy")).decode()
        }
        
        return self.verify_and_decrypt_payload(payload, aes_key, hmac_key) 