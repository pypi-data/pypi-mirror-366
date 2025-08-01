#!/usr/bin/env python3
"""
安装演示脚本
展示如何在实际项目中使用RSA-AES混合加密框架
"""

import os
import sys
import subprocess

def install_framework():
    """安装框架到当前Python环境"""
    print("🚀 开始安装RSA-AES混合加密框架...")
    
    try:
        # 检查是否已安装cryptography
        try:
            import cryptography
            print("✅ cryptography已安装")
        except ImportError:
            print("📦 安装cryptography依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
            print("✅ cryptography安装成功")
        
        # 安装框架到当前环境
        print("📦 安装加密框架...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ 框架安装成功")
        
        return True
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False

def test_usage():
    """测试框架使用"""
    print("\n🧪 测试框架使用...")
    
    try:
        # 导入框架
        from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync
        
        # 测试密钥交换
        print("🔑 执行密钥交换...")
        result = key_exchange_sync("demo_client")
        if not result["success"]:
            raise Exception("密钥交换失败")
        
        session_id = result["session_id"]
        print(f"✅ 密钥交换成功，会话ID: {session_id}")
        
        # 测试数据加密
        print("🔒 测试数据加密...")
        test_data = {
            "user_id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "message": "Hello, RSA-AES Hybrid Crypto Framework!"
        }
        
        encrypted = encrypt_data_sync(test_data, session_id)
        if not encrypted["success"]:
            raise Exception("数据加密失败")
        
        print("✅ 数据加密成功")
        
        # 测试数据解密
        print("🔓 测试数据解密...")
        decrypted = decrypt_data_sync(encrypted)
        if not decrypted["success"]:
            raise Exception("数据解密失败")
        
        if decrypted["data"] == test_data:
            print("✅ 数据解密成功，数据完整性验证通过")
        else:
            raise Exception("数据完整性验证失败")
        
        print("\n🎉 框架测试完全通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def show_usage_example():
    """显示使用示例"""
    print("\n📝 使用示例:")
    print("=" * 50)
    print("""
# 1. 在Python代码中使用
from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync

# 密钥交换
result = key_exchange_sync("my_client")
session_id = result["session_id"]

# 加密敏感数据
sensitive_data = {
    "user_id": 123,
    "password": "SecurePassword123!",
    "credit_card": "1234-5678-9012-3456"
}
encrypted = encrypt_data_sync(sensitive_data, session_id)

# 解密数据
decrypted = decrypt_data_sync(encrypted)
print(decrypted["data"])

# 2. 在FastAPI中使用
from fastapi import FastAPI, HTTPException
from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync

app = FastAPI()

@app.post("/api/secure/encrypt")
async def encrypt_data(data: dict):
    result = key_exchange_sync("web_client")
    session_id = result["session_id"]
    encrypted = encrypt_data_sync(data, session_id)
    return {"encrypted_data": encrypted, "session_id": session_id}

@app.post("/api/secure/decrypt")
async def decrypt_data(encrypted_data: dict):
    decrypted = decrypt_data_sync(encrypted_data)
    return {"data": decrypted["data"]}

# 3. 在Flask中使用
from flask import Flask, request, jsonify
from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync

app = Flask(__name__)

@app.route('/api/encrypt', methods=['POST'])
def encrypt_endpoint():
    data = request.json
    result = key_exchange_sync("web_client")
    session_id = result["session_id"]
    encrypted = encrypt_data_sync(data, session_id)
    return jsonify({"encrypted_data": encrypted, "session_id": session_id})

@app.route('/api/decrypt', methods=['POST'])
def decrypt_endpoint():
    encrypted_data = request.json.get("encrypted_data")
    decrypted = decrypt_data_sync(encrypted_data)
    return jsonify({"data": decrypted["data"]})
    """)
    print("=" * 50)

def main():
    """主函数"""
    print("🔐 RSA-AES混合加密框架安装演示")
    print("=" * 50)
    
    # 安装框架
    if not install_framework():
        print("❌ 安装失败，请检查错误信息")
        return
    
    # 测试使用
    if not test_usage():
        print("❌ 测试失败，请检查错误信息")
        return
    
    # 显示使用示例
    show_usage_example()
    
    print("\n🎉 安装和测试完成！")
    print("💡 现在您可以在项目中使用这个加密框架了。")

if __name__ == "__main__":
    main() 