/**
 * 前端加密用户API使用示例
 * 展示如何使用RSA-AES混合加密框架与后端API交互
 */

class EncryptedUserAPI {
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
        this.sessionId = null;
        this.publicKey = null;
        this.hmacKey = null;
    }

    /**
     * 密钥交换 - 获取加密会话
     */
    async keyExchange(clientId = 'web_client') {
        try {
            const response = await fetch(`${this.baseUrl}/auth/secure/key-exchange?client_id=${clientId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.sessionId = result.data.session_id;
                this.publicKey = result.data.public_key;
                this.hmacKey = result.data.hmac_key;
                
                console.log('密钥交换成功:', {
                    sessionId: this.sessionId,
                    publicKey: this.publicKey ? '已获取' : '未获取',
                    hmacKey: this.hmacKey ? '已获取' : '未获取'
                });
                
                return result.data;
            } else {
                throw new Error(result.message || '密钥交换失败');
            }
        } catch (error) {
            console.error('密钥交换失败:', error);
            throw error;
        }
    }

    /**
     * 加密用户注册
     */
    async encryptedRegister(userData) {
        if (!this.sessionId) {
            throw new Error('请先执行密钥交换');
        }

        try {
            // 使用加密框架加密数据
            const encryptedData = await this.encryptData(userData);
            
            const response = await fetch(`${this.baseUrl}/auth/secure/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    encrypted_data: encryptedData,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                console.log('加密注册成功:', result.data);
                return result.data;
            } else {
                throw new Error(result.message || '注册失败');
            }
        } catch (error) {
            console.error('加密注册失败:', error);
            throw error;
        }
    }

    /**
     * 加密用户登录
     */
    async encryptedLogin(loginData) {
        if (!this.sessionId) {
            throw new Error('请先执行密钥交换');
        }

        try {
            // 使用加密框架加密数据
            const encryptedData = await this.encryptData(loginData);
            
            const response = await fetch(`${this.baseUrl}/auth/secure/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    encrypted_data: encryptedData,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                console.log('加密登录成功:', result.data);
                
                // 保存令牌
                if (result.data.tokens) {
                    localStorage.setItem('access_token', result.data.tokens.access_token);
                    localStorage.setItem('refresh_token', result.data.tokens.refresh_token);
                }
                
                return result.data;
            } else {
                throw new Error(result.message || '登录失败');
            }
        } catch (error) {
            console.error('加密登录失败:', error);
            throw error;
        }
    }

    /**
     * 加密修改密码
     */
    async encryptedChangePassword(passwordData) {
        if (!this.sessionId) {
            throw new Error('请先执行密钥交换');
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('请先登录');
        }

        try {
            // 使用加密框架加密数据
            const encryptedData = await this.encryptData(passwordData);
            
            const response = await fetch(`${this.baseUrl}/auth/secure/change-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    encrypted_data: encryptedData,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                console.log('加密修改密码成功:', result.data);
                return result.data;
            } else {
                throw new Error(result.message || '修改密码失败');
            }
        } catch (error) {
            console.error('加密修改密码失败:', error);
            throw error;
        }
    }

    /**
     * 获取加密系统状态
     */
    async getEncryptedSystemStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/secure/status`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                console.log('加密系统状态:', result.data);
                return result.data;
            } else {
                throw new Error(result.message || '获取系统状态失败');
            }
        } catch (error) {
            console.error('获取加密系统状态失败:', error);
            throw error;
        }
    }

    /**
     * 使用加密框架加密数据
     * 这里需要调用加密框架的加密功能
     */
    async encryptData(data) {
        // 这里应该调用加密框架的加密功能
        // 由于这是示例，我们模拟加密过程
        console.log('加密数据:', data);
        
        // 在实际使用中，这里应该调用加密框架
        // const encrypted = await encrypt_data_sync(data, this.sessionId);
        // return encrypted;
        
        // 模拟返回加密数据
        return {
            encrypted_data: btoa(JSON.stringify(data)), // Base64编码模拟
            session_id: this.sessionId,
            timestamp: Date.now(),
            nonce: Math.random().toString(36).substring(7),
            signature: 'mock_signature'
        };
    }
}

// 使用示例
async function demoEncryptedUserAPI() {
    const api = new EncryptedUserAPI();
    
    try {
        // 1. 密钥交换
        console.log('=== 1. 密钥交换 ===');
        await api.keyExchange('demo_client');
        
        // 2. 加密注册
        console.log('=== 2. 加密注册 ===');
        const registerData = {
            username: 'testuser',
            email: 'test@example.com',
            password: 'SecurePassword123!',
            full_name: '测试用户'
        };
        
        try {
            const registerResult = await api.encryptedRegister(registerData);
            console.log('注册结果:', registerResult);
        } catch (error) {
            console.log('注册失败:', error.message);
        }
        
        // 3. 加密登录
        console.log('=== 3. 加密登录 ===');
        const loginData = {
            username: 'testuser',
            password: 'SecurePassword123!'
        };
        
        try {
            const loginResult = await api.encryptedLogin(loginData);
            console.log('登录结果:', loginResult);
        } catch (error) {
            console.log('登录失败:', error.message);
        }
        
        // 4. 加密修改密码
        console.log('=== 4. 加密修改密码 ===');
        const changePasswordData = {
            old_password: 'SecurePassword123!',
            new_password: 'NewSecurePassword456!'
        };
        
        try {
            const changePasswordResult = await api.encryptedChangePassword(changePasswordData);
            console.log('修改密码结果:', changePasswordResult);
        } catch (error) {
            console.log('修改密码失败:', error.message);
        }
        
        // 5. 获取系统状态
        console.log('=== 5. 获取加密系统状态 ===');
        const statusResult = await api.getEncryptedSystemStatus();
        console.log('系统状态:', statusResult);
        
    } catch (error) {
        console.error('演示失败:', error);
    }
}

// 在浏览器中运行演示
if (typeof window !== 'undefined') {
    // 浏览器环境
    window.EncryptedUserAPI = EncryptedUserAPI;
    window.demoEncryptedUserAPI = demoEncryptedUserAPI;
    
    console.log('加密用户API已加载，可以调用 demoEncryptedUserAPI() 开始演示');
} else {
    // Node.js环境
    module.exports = {
        EncryptedUserAPI,
        demoEncryptedUserAPI
    };
} 