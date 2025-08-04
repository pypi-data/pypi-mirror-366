# 会话管理
import base64
import json
import secrets
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from config import SecurityConfig


class CacheBackend(ABC):
    """缓存后端抽象类"""
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        pass


class MemoryCacheBackend(CacheBackend):
    """内存缓存后端"""
    
    # 全局缓存，所有实例共享
    _global_cache = {}
    _global_expire_times = {}
    
    def __init__(self):
        # 使用类级别的全局缓存
        pass
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._global_cache:
            del self._global_cache[key]
        if key in self._global_expire_times:
            del self._global_expire_times[key]
        return True
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.get(key) is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self._global_cache:
            return None
        
        # 检查是否过期
        if key in self._global_expire_times and time.time() > self._global_expire_times[key]:
            del self._global_cache[key]
            del self._global_expire_times[key]
            return None
        
        return self._global_cache[key]
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        self._global_cache[key] = value
        if expire:
            self._global_expire_times[key] = time.time() + expire
        return True


class RedisCacheBackend(CacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis = None
    
    async def _get_redis(self):
        """获取Redis连接"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError("Redis依赖未安装，请运行: pip install redis")
        return self._redis
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        redis_client = await self._get_redis()
        return await redis_client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        redis_client = await self._get_redis()
        return await redis_client.exists(key) > 0
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        redis_client = await self._get_redis()
        value = await redis_client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        redis_client = await self._get_redis()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await redis_client.set(key, value, ex=expire)


class SessionManager:
    """会话管理器"""
    
    # 全局会话管理器实例
    _global_instance = None
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self._cache = self._create_cache_backend()
        
        # 如果是第一个实例，设置为全局实例
        if SessionManager._global_instance is None:
            SessionManager._global_instance = self
    
    def _create_cache_backend(self) -> CacheBackend:
        """创建缓存后端"""
        if self.config.cache_backend.lower() == "redis":
            return RedisCacheBackend(self.config.redis_url)
        else:
            return MemoryCacheBackend()
    
    @classmethod
    def get_global_instance(cls):
        """获取全局会话管理器实例"""
        return cls._global_instance
    
    def generate_session_id(self, client_id: str) -> str:
        """生成会话ID"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(8)
        return f"{client_id}_{timestamp}_{random_part}"
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        # 对于内存缓存，过期检查在get时进行
        # 对于Redis缓存，Redis会自动清理过期键
        return 0
    
    async def create_session(self, client_id: str, client_version: str = None) -> Dict[str, Any]:
        """创建会话"""
        session_id = self.generate_session_id(client_id)
        
        session_info = {
            "session_id": session_id,
            "client_id": client_id,
            "client_version": client_version,
            "created_at": time.time(),
            "last_activity": time.time(),
            "status": "active"
        }
        
        # 存储会话信息
        await self._cache.set(f"session:{session_id}", session_info, self.config.session_expire_time)
        
        return session_info
    
    async def get_aes_key(self, session_id: str) -> Optional[str]:
        """获取AES密钥"""
        key_data = await self._cache.get(f"keys:{session_id}")
        if key_data:
            return key_data.get("aes_key")
        return None
    
    async def get_hmac_key(self, session_id: str) -> Optional[str]:
        """获取HMAC密钥"""
        key_data = await self._cache.get(f"keys:{session_id}")
        if key_data:
            return key_data.get("hmac_key")
        return None
    
    async def get_private_key(self, session_id: str) -> Optional[str]:
        """获取私钥"""
        key_data = await self._cache.get(f"keys:{session_id}")
        if key_data:
            return key_data.get("private_key")
        return None
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        return await self._cache.get(f"session:{session_id}")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        # 这里可以实现更详细的统计信息
        return {
            "cache_backend": self.config.cache_backend,
            "session_expire_time": self.config.session_expire_time,
            "max_timestamp_diff": self.config.max_timestamp_diff
        }
    
    async def invalidate_session(self, session_id: str) -> bool:
        """使会话失效"""
        # 删除会话信息
        await self._cache.delete(f"session:{session_id}")
        # 删除密钥
        await self._cache.delete(f"keys:{session_id}")
        return True
    
    async def is_session_valid(self, session_id: str) -> bool:
        """检查会话是否有效"""
        session_info = await self.get_session_info(session_id)
        if not session_info:
            return False
        
        # 检查会话状态
        if session_info.get("status") != "active":
            return False
        
        # 检查是否过期
        last_activity = session_info.get("last_activity", 0)
        if time.time() - last_activity > self.config.session_expire_time:
            return False
        
        return True
    
    async def store_aes_key(self, session_id: str, aes_key: str) -> bool:
        """存储AES密钥"""
        key_data = await self._cache.get(f"keys:{session_id}")
        if key_data:
            key_data["aes_key"] = aes_key
            return await self._cache.set(f"keys:{session_id}", key_data, self.config.session_expire_time)
        return False
    
    async def store_keys(self, session_id: str, private_key: str, hmac_key: str) -> bool:
        """存储密钥"""
        key_data = {
            "private_key": private_key,
            "hmac_key": hmac_key,
            "stored_at": time.time()
        }
        
        return await self._cache.set(f"keys:{session_id}", key_data, self.config.session_expire_time)
    
    async def update_session_activity(self, session_id: str) -> bool:
        """更新会话活动时间"""
        session_info = await self.get_session_info(session_id)
        if session_info:
            session_info["last_activity"] = time.time()
            return await self._cache.set(f"session:{session_id}", session_info, self.config.session_expire_time)
        return False 