#!/usr/bin/env python3
"""
加密框架使用示例
展示多种使用方式
"""
import asyncio
import json
from encryption_framework import (
    EncryptionAPI, 
    SecurityConfig,
    key_exchange,
    encrypt_data,
    decrypt_data,
    create_session,
    invalidate_session,
    get_session_info,
    health_check,
    # 同步版本
    key_exchange_sync,
    encrypt_data_sync,
    decrypt_data_sync,
    create_session_sync,
    invalidate_session_sync,
    get_session_info_sync,
    health_check_sync
)


async def example_1_basic_usage():
    """示例1：基本使用方式"""
    print("🔐 示例1：基本使用方式")
    print("=" * 50)
    
    # 创建配置
    config = SecurityConfig(
        rsa_key_size=2048,
        aes_key_size=32,
        session_expire_time=3600,
        cache_backend="memory"
    )
    
    # 创建API实例
    api = EncryptionAPI(config)
    
    # 密钥交换
    result = await api.key_exchange("client_001", "1.0.0")
    if result["success"]:
        session_id = result["session_id"]
        print(f"✅ 密钥交换成功，会话ID: {session_id}")
        
        # 加密数据
        data = {"message": "Hello, World!", "user_id": 123}
        encrypt_result = await api.encrypt_data(data, session_id)
        
        if encrypt_result["success"]:
            print(f"✅ 数据加密成功")
            
            # 解密数据
            decrypt_result = await api.decrypt_data(encrypt_result)
            if decrypt_result["success"]:
                print(f"✅ 数据解密成功: {decrypt_result['data']}")
            else:
                print(f"❌ 数据解密失败: {decrypt_result['error']}")
        else:
            print(f"❌ 数据加密失败: {encrypt_result['error']}")
    else:
        print(f"❌ 密钥交换失败: {result['error']}")


async def example_2_convenient_functions():
    """示例2：使用便捷函数"""
    print("\n🔐 示例2：使用便捷函数")
    print("=" * 50)
    
    # 使用便捷函数
    result = await key_exchange("client_002", "1.0.0")
    if result["success"]:
        session_id = result["session_id"]
        print(f"✅ 密钥交换成功，会话ID: {session_id}")
        
        # 加密数据
        data = {"message": "使用便捷函数", "timestamp": 1234567890}
        encrypt_result = await encrypt_data(data, session_id)
        
        if encrypt_result["success"]:
            print(f"✅ 数据加密成功")
            
            # 解密数据
            decrypt_result = await decrypt_data(encrypt_result)
            if decrypt_result["success"]:
                print(f"✅ 数据解密成功: {decrypt_result['data']}")
            else:
                print(f"❌ 数据解密失败: {decrypt_result['error']}")
        else:
            print(f"❌ 数据加密失败: {encrypt_result['error']}")
    else:
        print(f"❌ 密钥交换失败: {result['error']}")


def example_3_sync_functions():
    """示例3：使用同步函数"""
    print("\n🔐 示例3：使用同步函数")
    print("=" * 50)
    
    # 使用同步函数
    result = key_exchange_sync("client_003", "1.0.0")
    if result["success"]:
        session_id = result["session_id"]
        print(f"✅ 密钥交换成功，会话ID: {session_id}")
        
        # 加密数据
        data = {"message": "使用同步函数", "user_id": 456}
        encrypt_result = encrypt_data_sync(data, session_id)
        
        if encrypt_result["success"]:
            print(f"✅ 数据加密成功")
            
            # 解密数据
            decrypt_result = decrypt_data_sync(encrypt_result)
            if decrypt_result["success"]:
                print(f"✅ 数据解密成功: {decrypt_result['data']}")
            else:
                print(f"❌ 数据解密失败: {decrypt_result['error']}")
        else:
            print(f"❌ 数据加密失败: {encrypt_result['error']}")
    else:
        print(f"❌ 密钥交换失败: {result['error']}")


async def example_4_session_management():
    """示例4：会话管理"""
    print("\n🔐 示例4：会话管理")
    print("=" * 50)
    
    # 创建会话
    result = await create_session("client_004", "1.0.0")
    if result["success"]:
        session_id = result["session_id"]
        print(f"✅ 会话创建成功，会话ID: {session_id}")
        
        # 获取会话信息
        session_info = await get_session_info(session_id)
        if session_info["success"]:
            info = session_info["session_info"]
            print(f"✅ 会话信息获取成功")
            print(f"   客户端ID: {info['client_id']}")
            print(f"   创建时间: {info['created_at']}")
            print(f"   状态: {info['status']}")
        
        # 使会话失效
        invalidate_result = await invalidate_session(session_id)
        if invalidate_result["success"]:
            print(f"✅ 会话失效成功")
            
            # 验证会话已失效
            session_info = await get_session_info(session_id)
            if not session_info["success"]:
                print("✅ 会话已成功失效")
            else:
                print("❌ 会话失效验证失败")
        else:
            print(f"❌ 会话失效失败: {invalidate_result['error']}")
    else:
        print(f"❌ 会话创建失败: {result['error']}")


async def example_5_health_check():
    """示例5：健康检查"""
    print("\n🔐 示例5：健康检查")
    print("=" * 50)
    
    # 健康检查
    health_result = await health_check()
    if health_result["success"]:
        print(f"✅ 健康检查通过")
        print(f"   状态: {health_result['status']}")
        print(f"   组件: {health_result['components']}")
        print(f"   时间戳: {health_result['timestamp']}")
    else:
        print(f"❌ 健康检查失败: {health_result['error']}")


async def example_6_custom_config():
    """示例6：自定义配置"""
    print("\n🔐 示例6：自定义配置")
    print("=" * 50)
    
    # 自定义配置
    config = SecurityConfig(
        rsa_key_size=4096,  # 使用4096位RSA
        aes_key_size=32,
        aes_mode="CBC",     # 使用CBC模式
        session_expire_time=7200,  # 2小时过期
        max_timestamp_diff=600,    # 10分钟时间窗口
        cache_backend="memory",
        log_level="DEBUG"
    )
    
    api = EncryptionAPI(config)
    
    # 使用自定义配置
    result = await api.key_exchange("client_005", "1.0.0")
    if result["success"]:
        session_id = result["session_id"]
        print(f"✅ 使用自定义配置成功，会话ID: {session_id}")
        
        # 获取配置信息
        config_result = await api.get_security_config()
        if config_result["success"]:
            security_config = config_result["security_config"]
            print(f"✅ 配置信息获取成功")
            print(f"   RSA密钥大小: {security_config['rsa_key_size']}")
            print(f"   AES模式: {security_config['aes_mode']}")
            print(f"   会话过期时间: {security_config['session_expire_time']} 秒")
    else:
        print(f"❌ 使用自定义配置失败: {result['error']}")


async def example_7_error_handling():
    """示例7：错误处理"""
    print("\n🔐 示例7：错误处理")
    print("=" * 50)
    
    try:
        # 尝试使用无效会话ID
        data = {"test": "data"}
        result = await encrypt_data(data, "invalid_session_id")
        
        if result["success"]:
            print("✅ 加密成功")
        else:
            print(f"❌ 加密失败（预期）: {result['error']}")
            
    except Exception as e:
        print(f"❌ 发生异常: {e}")


def example_8_simple_import():
    """示例8：最简单的使用方式"""
    print("\n🔐 示例8：最简单的使用方式")
    print("=" * 50)
    
    # 最简单的使用方式
    from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync
    
    # 密钥交换
    result = key_exchange_sync("simple_client")
    if result["success"]:
        session_id = result["session_id"]
        
        # 加密
        data = {"message": "最简单的使用方式"}
        encrypt_result = encrypt_data_sync(data, session_id)
        
        if encrypt_result["success"]:
            # 解密
            decrypt_result = decrypt_data_sync(encrypt_result)
            if decrypt_result["success"]:
                print(f"✅ 最简单的使用方式成功: {decrypt_result['data']}")
            else:
                print(f"❌ 解密失败: {decrypt_result['error']}")
        else:
            print(f"❌ 加密失败: {encrypt_result['error']}")
    else:
        print(f"❌ 密钥交换失败: {result['error']}")


async def main():
    """主函数"""
    print("🚀 加密框架使用示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        await example_1_basic_usage()
        await example_2_convenient_functions()
        example_3_sync_functions()
        await example_4_session_management()
        await example_5_health_check()
        await example_6_custom_config()
        await example_7_error_handling()
        example_8_simple_import()
        
        print("\n🎉 所有示例运行完成！")
        
    except Exception as e:
        print(f"❌ 示例运行过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 