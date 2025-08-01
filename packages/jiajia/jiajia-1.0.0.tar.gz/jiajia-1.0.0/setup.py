from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "RSA-AES混合加密框架"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return ["cryptography>=3.4.8"]

setup(
    name="jiajia",
    version="1.0.0",
    author="夏云龙",
    author_email="1900098962@qq.com",
    description="RSA-AES混合加密框架，提供非对称加密、对称加密、数字签名等功能",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiatian/rsa-aes-hybrid-crypto-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    keywords="encryption, cryptography, rsa, aes, hmac, security, hybrid",
    project_urls={
        "Bug Reports": "https://github.com/xiatian/rsa-aes-hybrid-crypto-framework/issues",
        "Source": "https://github.com/xiatian/rsa-aes-hybrid-crypto-framework",
        "Documentation": "https://github.com/xiatian/rsa-aes-hybrid-crypto-framework/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
) 