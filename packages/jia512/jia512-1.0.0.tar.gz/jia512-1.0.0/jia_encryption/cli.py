#!/usr/bin/env python3
"""
Jia Encryption Framework CLI
提供命令行工具来测试和使用加密功能
"""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any

from __init__ import (
    EncryptionAPI,
    SecurityConfig,
    key_exchange,
    encrypt_data,
    decrypt_data,
    health_check,
    get_session_info,
    invalidate_session,
)


def print_json(data: Dict[str, Any]) -> None:
    """打印JSON格式的数据"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


async def cmd_key_exchange(args: argparse.Namespace) -> None:
    """密钥交换命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    result = await key_exchange(args.client_id, args.client_version, config)
    print_json(result)


async def cmd_encrypt(args: argparse.Namespace) -> None:
    """加密命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    # 解析数据
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError:
        print("错误: 数据格式必须是有效的JSON")
        sys.exit(1)
    
    result = await encrypt_data(data, args.session_id, config)
    print_json(result)


async def cmd_decrypt(args: argparse.Namespace) -> None:
    """解密命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    # 解析载荷
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError:
        print("错误: 载荷格式必须是有效的JSON")
        sys.exit(1)
    
    result = await decrypt_data(payload, config)
    print_json(result)


async def cmd_health_check(args: argparse.Namespace) -> None:
    """健康检查命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    result = await health_check(config)
    print_json(result)


async def cmd_session_info(args: argparse.Namespace) -> None:
    """获取会话信息命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    result = await get_session_info(args.session_id, config)
    print_json(result)


async def cmd_invalidate_session(args: argparse.Namespace) -> None:
    """使会话失效命令"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    result = await invalidate_session(args.session_id, config)
    print_json(result)


async def cmd_test(args: argparse.Namespace) -> None:
    """测试完整流程"""
    config = SecurityConfig()
    if args.config:
        config = SecurityConfig.from_env()
    
    print("=== JiaJia 加密框架测试 ===")
    
    # 1. 密钥交换
    print("\n1. 执行密钥交换...")
    exchange_result = await key_exchange("test_client", "1.0.0", config)
    if not exchange_result["success"]:
        print(f"密钥交换失败: {exchange_result['error']}")
        sys.exit(1)
    
    session_id = exchange_result["session_id"]
    print(f"会话ID: {session_id}")
    
    # 2. 加密数据
    print("\n2. 加密测试数据...")
    test_data = {"message": "Hello, JiaJia!", "timestamp": 1234567890}
    encrypt_result = await encrypt_data(test_data, session_id, config)
    if not encrypt_result["success"]:
        print(f"加密失败: {encrypt_result['error']}")
        sys.exit(1)
    
    print("加密成功")
    
    # 3. 解密数据
    print("\n3. 解密数据...")
    decrypt_payload = encrypt_result.copy()
    decrypt_payload["session_id"] = session_id
    decrypt_result = await decrypt_data(decrypt_payload, config)
    if not decrypt_result["success"]:
        print(f"解密失败: {decrypt_result['error']}")
        sys.exit(1)
    
    print("解密成功")
    print(f"原始数据: {test_data}")
    print(f"解密数据: {decrypt_result['data']}")
    
    # 4. 验证数据一致性
    if decrypt_result["data"] == test_data:
        print("\n✅ 测试通过! 数据加密解密成功")
    else:
        print("\n❌ 测试失败! 数据不一致")
        sys.exit(1)


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="JiaJia 加密框架命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  jiajia test                           # 运行完整测试
  jiajia key-exchange --client-id test  # 密钥交换
  jiajia encrypt --data '{"msg":"test"}' --session-id xxx  # 加密数据
  jiajia decrypt --payload '{"encrypted_data":"..."}'      # 解密数据
  jiajia health-check                   # 健康检查
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 测试命令
    test_parser = subparsers.add_parser("test", help="运行完整测试")
    test_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    test_parser.set_defaults(func=cmd_test)
    
    # 密钥交换命令
    exchange_parser = subparsers.add_parser("key-exchange", help="执行密钥交换")
    exchange_parser.add_argument("--client-id", required=True, help="客户端ID")
    exchange_parser.add_argument("--client-version", default="1.0.0", help="客户端版本")
    exchange_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    exchange_parser.set_defaults(func=cmd_key_exchange)
    
    # 加密命令
    encrypt_parser = subparsers.add_parser("encrypt", help="加密数据")
    encrypt_parser.add_argument("--data", required=True, help="要加密的JSON数据")
    encrypt_parser.add_argument("--session-id", required=True, help="会话ID")
    encrypt_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    encrypt_parser.set_defaults(func=cmd_encrypt)
    
    # 解密命令
    decrypt_parser = subparsers.add_parser("decrypt", help="解密数据")
    decrypt_parser.add_argument("--payload", required=True, help="要解密的JSON载荷")
    decrypt_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    decrypt_parser.set_defaults(func=cmd_decrypt)
    
    # 健康检查命令
    health_parser = subparsers.add_parser("health-check", help="健康检查")
    health_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    health_parser.set_defaults(func=cmd_health_check)
    
    # 会话信息命令
    session_parser = subparsers.add_parser("session-info", help="获取会话信息")
    session_parser.add_argument("--session-id", required=True, help="会话ID")
    session_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    session_parser.set_defaults(func=cmd_session_info)
    
    # 使会话失效命令
    invalidate_parser = subparsers.add_parser("invalidate-session", help="使会话失效")
    invalidate_parser.add_argument("--session-id", required=True, help="会话ID")
    invalidate_parser.add_argument("--config", action="store_true", help="从环境变量加载配置")
    invalidate_parser.set_defaults(func=cmd_invalidate_session)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 