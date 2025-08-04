"""
测试便捷函数
"""

import pytest
import asyncio
from jiajia import (
    SecurityConfig,
    key_exchange,
    encrypt_data,
    decrypt_data,
    get_session_info,
    invalidate_session,
    health_check,
    key_exchange_sync,
    encrypt_data_sync,
    decrypt_data_sync,
    get_session_info_sync,
    invalidate_session_sync,
    health_check_sync,
)


class TestUtils:
    """测试便捷函数"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = SecurityConfig()
    
    @pytest.mark.asyncio
    async def test_async_utils(self):
        """测试异步便捷函数"""
        # 密钥交换
        exchange_result = await key_exchange("test_client", "1.0.0", self.config)
        assert exchange_result["success"] is True
        session_id = exchange_result["session_id"]
        
        # 加密数据
        test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
        encrypt_result = await encrypt_data(test_data, session_id, self.config)
        assert encrypt_result["success"] is True
        
        # 解密数据
        decrypt_payload = encrypt_result.copy()
        decrypt_payload["session_id"] = session_id
        decrypt_result = await decrypt_data(decrypt_payload, self.config)
        assert decrypt_result["success"] is True
        assert decrypt_result["data"] == test_data
        
        # 获取会话信息
        session_info = await get_session_info(session_id, self.config)
        assert session_info["success"] is True
        
        # 健康检查
        health_result = await health_check(self.config)
        assert health_result["success"] is True
        
        # 使会话失效
        invalidate_result = await invalidate_session(session_id, self.config)
        assert invalidate_result["success"] is True
    
    def test_sync_utils(self):
        """测试同步便捷函数"""
        # 密钥交换
        exchange_result = key_exchange_sync("test_client", "1.0.0", self.config)
        assert exchange_result["success"] is True
        session_id = exchange_result["session_id"]
        
        # 加密数据
        test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
        encrypt_result = encrypt_data_sync(test_data, session_id, self.config)
        assert encrypt_result["success"] is True
        
        # 解密数据
        decrypt_payload = encrypt_result.copy()
        decrypt_payload["session_id"] = session_id
        decrypt_result = decrypt_data_sync(decrypt_payload, self.config)
        assert decrypt_result["success"] is True
        assert decrypt_result["data"] == test_data
        
        # 获取会话信息
        session_info = get_session_info_sync(session_id, self.config)
        assert session_info["success"] is True
        
        # 健康检查
        health_result = health_check_sync(self.config)
        assert health_result["success"] is True
        
        # 使会话失效
        invalidate_result = invalidate_session_sync(session_id, self.config)
        assert invalidate_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_utils_without_config(self):
        """测试不带配置的便捷函数"""
        # 密钥交换
        exchange_result = await key_exchange("test_client", "1.0.0")
        assert exchange_result["success"] is True
        session_id = exchange_result["session_id"]
        
        # 加密数据
        test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
        encrypt_result = await encrypt_data(test_data, session_id)
        assert encrypt_result["success"] is True
        
        # 解密数据
        decrypt_payload = encrypt_result.copy()
        decrypt_payload["session_id"] = session_id
        decrypt_result = await decrypt_data(decrypt_payload)
        assert decrypt_result["success"] is True
        assert decrypt_result["data"] == test_data
    
    def test_sync_utils_without_config(self):
        """测试不带配置的同步便捷函数"""
        # 密钥交换
        exchange_result = key_exchange_sync("test_client", "1.0.0")
        assert exchange_result["success"] is True
        session_id = exchange_result["session_id"]
        
        # 加密数据
        test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
        encrypt_result = encrypt_data_sync(test_data, session_id)
        assert encrypt_result["success"] is True
        
        # 解密数据
        decrypt_payload = encrypt_result.copy()
        decrypt_payload["session_id"] = session_id
        decrypt_result = decrypt_data_sync(decrypt_payload)
        assert decrypt_result["success"] is True
        assert decrypt_result["data"] == test_data 