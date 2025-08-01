#!/usr/bin/env python3
"""
测试加密框架的导入和使用
"""

def test_import():
    """测试框架导入"""
    try:
        from encryption_framework import (
            key_exchange_sync,
            encrypt_data_sync,
            decrypt_data_sync,
            SecurityConfig
        )
        print("✅ 框架导入成功")
        return True
    except ImportError as e:
        print(f"❌ 框架导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync
        
        # 测试密钥交换
        print("🔑 测试密钥交换...")
        result = key_exchange_sync("test_client")
        if result["success"]:
            print("✅ 密钥交换成功")
            session_id = result["session_id"]
        else:
            print("❌ 密钥交换失败")
            return False
        
        # 测试数据加密
        print("🔒 测试数据加密...")
        test_data = {"message": "Hello, World!", "user_id": 123}
        encrypted = encrypt_data_sync(test_data, session_id)
        if encrypted["success"]:
            print("✅ 数据加密成功")
        else:
            print("❌ 数据加密失败")
            return False
        
        # 测试数据解密
        print("🔓 测试数据解密...")
        decrypted = decrypt_data_sync(encrypted)
        if decrypted["success"] and decrypted["data"] == test_data:
            print("✅ 数据解密成功")
        else:
            print("❌ 数据解密失败")
            return False
        
        print("🎉 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_config():
    """测试配置功能"""
    try:
        from encryption_framework import SecurityConfig
        
        # 测试默认配置
        config = SecurityConfig()
        print(f"✅ 默认配置: RSA={config.rsa_key_size}, AES={config.aes_key_size}")
        
        # 测试自定义配置
        custom_config = SecurityConfig(
            rsa_key_size=4096,
            aes_key_size=32,
            session_expire_time=7200,
            cache_backend="memory"
        )
        print(f"✅ 自定义配置: RSA={custom_config.rsa_key_size}, AES={custom_config.aes_key_size}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试RSA-AES混合加密框架...")
    print("=" * 50)
    
    # 测试导入
    if not test_import():
        print("❌ 导入测试失败，请检查安装")
        return
    
    # 测试配置
    if not test_config():
        print("❌ 配置测试失败")
        return
    
    # 测试基本功能
    if not test_basic_functionality():
        print("❌ 基本功能测试失败")
        return
    
    print("=" * 50)
    print("🎉 所有测试通过！框架可以正常使用。")
    print("\n📝 使用示例:")
    print("""
from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync

# 密钥交换
result = key_exchange_sync("my_client")
session_id = result["session_id"]

# 加密数据
data = {"message": "Hello, World!"}
encrypted = encrypt_data_sync(data, session_id)

# 解密数据
decrypted = decrypt_data_sync(encrypted)
print(decrypted["data"])
    """)

if __name__ == "__main__":
    main() 