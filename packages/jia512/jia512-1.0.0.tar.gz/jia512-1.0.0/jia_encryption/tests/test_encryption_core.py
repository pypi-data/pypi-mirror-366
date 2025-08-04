"""
测试加密核心功能
"""

import pytest
import base64
import json
from jiajia import EncryptionCore, SecurityConfig


class TestEncryptionCore:
    """测试加密核心类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = SecurityConfig()
        self.core = EncryptionCore(self.config)
    
    def test_generate_rsa_keypair(self):
        """测试RSA密钥对生成"""
        private_key, public_key = self.core.generate_rsa_keypair()
        
        assert isinstance(private_key, bytes)
        assert isinstance(public_key, bytes)
        assert b"PRIVATE KEY" in private_key
        assert b"PUBLIC KEY" in public_key
    
    def test_generate_aes_key(self):
        """测试AES密钥生成"""
        key = self.core.generate_aes_key()
        
        assert isinstance(key, bytes)
        assert len(key) == self.config.aes_key_size
    
    def test_generate_hmac_key(self):
        """测试HMAC密钥生成"""
        key = self.core.generate_hmac_key()
        
        assert isinstance(key, bytes)
        assert len(key) == 32
    
    def test_generate_iv(self):
        """测试初始化向量生成"""
        iv = self.core.generate_iv()
        
        assert isinstance(iv, bytes)
        assert len(iv) == 16
    
    def test_generate_nonce(self):
        """测试随机数生成"""
        nonce = self.core.generate_nonce()
        
        assert isinstance(nonce, bytes)
        assert len(nonce) == 16
    
    def test_rsa_encrypt_decrypt(self):
        """测试RSA加密解密"""
        private_key, public_key = self.core.generate_rsa_keypair()
        test_data = b"Hello, JiaJia!"
        
        # 加密
        encrypted = self.core.rsa_encrypt(public_key, test_data)
        assert isinstance(encrypted, bytes)
        assert encrypted != test_data
        
        # 解密
        decrypted = self.core.rsa_decrypt(private_key, encrypted)
        assert decrypted == test_data
    
    def test_aes_encrypt_decrypt_gcm(self):
        """测试AES GCM模式加密解密"""
        self.config.aes_mode = "GCM"
        core = EncryptionCore(self.config)
        
        key = core.generate_aes_key()
        test_data = b"Hello, JiaJia!"
        
        # 加密
        iv, ciphertext, tag = core.aes_encrypt(key, test_data)
        assert isinstance(iv, bytes)
        assert isinstance(ciphertext, bytes)
        assert isinstance(tag, bytes)
        assert len(iv) == 16
        
        # 解密
        decrypted = core.aes_decrypt(key, iv, ciphertext, tag)
        assert decrypted == test_data
    
    def test_aes_encrypt_decrypt_cbc(self):
        """测试AES CBC模式加密解密"""
        self.config.aes_mode = "CBC"
        core = EncryptionCore(self.config)
        
        key = core.generate_aes_key()
        test_data = b"Hello, JiaJia!"
        
        # 加密
        iv, ciphertext, tag = core.aes_encrypt(key, test_data)
        assert isinstance(iv, bytes)
        assert isinstance(ciphertext, bytes)
        assert tag == b""  # CBC模式没有tag
        
        # 解密
        decrypted = core.aes_decrypt(key, iv, ciphertext, tag)
        assert decrypted == test_data
    
    def test_hmac_sign_verify(self):
        """测试HMAC签名验证"""
        key = self.core.generate_hmac_key()
        test_data = b"Hello, JiaJia!"
        
        # 签名
        signature = self.core.hmac_sign(key, test_data)
        assert isinstance(signature, bytes)
        
        # 验证
        is_valid = self.core.hmac_verify(key, test_data, signature)
        assert is_valid is True
        
        # 验证错误数据
        wrong_data = b"Wrong data"
        is_valid = self.core.hmac_verify(key, wrong_data, signature)
        assert is_valid is False
    
    def test_hybrid_encrypt_decrypt(self):
        """测试混合加密解密"""
        private_key, public_key = self.core.generate_rsa_keypair()
        hmac_key = self.core.generate_hmac_key()
        test_data = b"Hello, JiaJia!"
        
        # 混合加密
        result = self.core.hybrid_encrypt(public_key, test_data, hmac_key)
        assert "encrypted_data" in result
        assert "encrypted_key" in result
        assert "signature" in result
        
        # 混合解密
        decrypted = self.core.hybrid_decrypt(
            private_key,
            result["encrypted_data"],
            result["encrypted_key"],
            hmac_key
        )
        assert decrypted == test_data
    
    def test_create_secure_payload(self):
        """测试安全载荷创建"""
        aes_key = self.core.generate_aes_key()
        hmac_key = self.core.generate_hmac_key()
        test_data = b"Hello, JiaJia!"
        timestamp = 1234567890
        nonce = self.core.generate_nonce()
        
        # 创建安全载荷
        payload = self.core.create_secure_payload(
            test_data, aes_key, hmac_key, timestamp, nonce
        )
        
        assert "encrypted_data" in payload
        assert "iv" in payload
        assert "timestamp" in payload
        assert "nonce" in payload
        assert "signature" in payload
        
        if self.config.aes_mode.upper() == "GCM":
            assert "tag" in payload
    
    def test_verify_and_decrypt_payload(self):
        """测试载荷验证和解密"""
        aes_key = self.core.generate_aes_key()
        hmac_key = self.core.generate_hmac_key()
        test_data = b"Hello, JiaJia!"
        timestamp = 1234567890
        nonce = self.core.generate_nonce()
        
        # 创建安全载荷
        payload = self.core.create_secure_payload(
            test_data, aes_key, hmac_key, timestamp, nonce
        )
        
        # 验证和解密
        decrypted = self.core.verify_and_decrypt_payload(
            payload, aes_key, hmac_key
        )
        assert decrypted == test_data 