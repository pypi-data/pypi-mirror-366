"""
测试加密API功能
"""

import pytest
import asyncio
from jiajia import EncryptionAPI, SecurityConfig


class TestEncryptionAPI:
    """测试加密API类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = SecurityConfig()
        self.api = EncryptionAPI(self.config)
    
    @pytest.mark.asyncio
    async def test_key_exchange(self):
        """测试密钥交换"""
        result = await self.api.key_exchange("test_client", "1.0.0")
        
        assert result["success"] is True
        assert "session_id" in result
        assert "public_key" in result
        assert "hmac_key" in result
        assert "server_timestamp" in result
        assert "session_info" in result
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_flow(self):
        """测试完整的加密解密流程"""
        # 1. 密钥交换
        exchange_result = await self.api.key_exchange("test_client", "1.0.0")
        assert exchange_result["success"] is True
        
        session_id = exchange_result["session_id"]
        
        # 2. 加密数据
        test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
        encrypt_result = await self.api.encrypt_data(test_data, session_id)
        assert encrypt_result["success"] is True
        assert "encrypted_data" in encrypt_result
        assert "iv" in encrypt_result
        assert "timestamp" in encrypt_result
        assert "nonce" in encrypt_result
        assert "signature" in encrypt_result
        
        # 3. 解密数据
        decrypt_payload = encrypt_result.copy()
        decrypt_payload["session_id"] = session_id
        decrypt_result = await self.api.decrypt_data(decrypt_payload)
        assert decrypt_result["success"] is True
        assert decrypt_result["data"] == test_data
    
    @pytest.mark.asyncio
    async def test_session_management(self):
        """测试会话管理"""
        # 创建会话
        exchange_result = await self.api.key_exchange("test_client", "1.0.0")
        session_id = exchange_result["session_id"]
        
        # 获取会话信息
        session_info = await self.api.get_session_info(session_id)
        assert session_info["success"] is True
        assert session_info["session_info"]["session_id"] == session_id
        
        # 使会话失效
        invalidate_result = await self.api.invalidate_session(session_id)
        assert invalidate_result["success"] is True
        
        # 验证会话已失效
        session_info = await self.api.get_session_info(session_id)
        assert session_info["success"] is False
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        result = await self.api.health_check()
        
        assert result["success"] is True
        assert "status" in result
        assert "timestamp" in result
        assert "version" in result
    
    @pytest.mark.asyncio
    async def test_get_security_config(self):
        """测试获取安全配置"""
        result = await self.api.get_security_config()
        
        assert result["success"] is True
        assert "config" in result
        config = result["config"]
        assert "aes_key_size" in config
        assert "aes_mode" in config
        assert "rsa_key_size" in config
        assert "session_expire_time" in config
    
    @pytest.mark.asyncio
    async def test_invalid_session(self):
        """测试无效会话"""
        # 尝试使用无效会话ID加密
        result = await self.api.encrypt_data({"test": "data"}, "invalid_session_id")
        assert result["success"] is False
        assert "会话无效或已过期" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_decrypt_payload(self):
        """测试无效的解密载荷"""
        # 创建有效会话
        exchange_result = await self.api.key_exchange("test_client", "1.0.0")
        session_id = exchange_result["session_id"]
        
        # 尝试解密无效载荷
        invalid_payload = {
            "session_id": session_id,
            "encrypted_data": "invalid_data",
            "iv": "invalid_iv",
            "timestamp": "1234567890",
            "nonce": "invalid_nonce",
            "signature": "invalid_signature"
        }
        
        result = await self.api.decrypt_data(invalid_payload)
        assert result["success"] is False
    
    @pytest.mark.asyncio
    async def test_set_session_info(self):
        """测试手动设置会话信息"""
        session_id = "test_session_123"
        hmac_key = "test_hmac_key"
        
        await self.api.set_session_info(session_id, hmac_key)
        
        # 验证会话信息已设置
        session_info = await self.api.get_session_info(session_id)
        assert session_info["success"] is True
        assert session_info["session_info"]["session_id"] == session_id 