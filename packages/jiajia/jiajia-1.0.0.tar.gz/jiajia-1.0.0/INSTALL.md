# 安装说明

## 方式1：直接安装（推荐）

```bash
# 进入框架目录
cd rsa-aes-hybrid-crypto-framework

# 安装到当前Python环境
pip install -e .

# 或者直接安装依赖
pip install cryptography
```

## 方式2：复制框架文件

```bash
# 复制整个框架到你的项目
cp -r encryption_framework/ your_project/

# 安装依赖
pip install cryptography
```

## 方式3：添加到Python路径

```bash
# 将框架路径添加到PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/rsa-aes-hybrid-crypto-framework

# 或者在代码中添加路径
import sys
sys.path.append('/path/to/rsa-aes-hybrid-crypto-framework')
```

## 验证安装

```python
# 测试导入
from encryption_framework import key_exchange_sync, encrypt_data_sync, decrypt_data_sync

# 测试基本功能
result = key_exchange_sync("test_client")
print("安装成功:", result["success"])
```

## 在项目中使用

```python
# 直接导入使用
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
``` 