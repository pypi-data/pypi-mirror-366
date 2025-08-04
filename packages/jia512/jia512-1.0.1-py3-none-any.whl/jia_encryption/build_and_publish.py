#!/usr/bin/env python3
"""
Jia 加密框架构建和发布脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, cwd=None):
    """运行命令"""
    print(f"执行命令: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        sys.exit(1)
    print(f"命令执行成功: {result.stdout}")
    return result


def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    build_dirs = ["build", "dist", "*.egg-info"]
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除: {dir_name}")


def build_package():
    """构建包"""
    print("构建包...")
    run_command("python -m build")


def run_tests():
    """运行测试"""
    print("运行测试...")
    run_command("python -m pytest tests/ -v")


def check_package():
    """检查包"""
    print("检查包...")
    run_command("python -m twine check dist/*")


def upload_to_test_pypi():
    """上传到测试PyPI"""
    print("上传到测试PyPI...")
    run_command("python -m twine upload --repository testpypi dist/*")


def upload_to_pypi():
    """上传到PyPI"""
    print("上传到PyPI...")
    run_command("python -m twine upload dist/*")


def main():
    """主函数"""
    print("=== Jia 加密框架构建和发布脚本 ===")
    
    if len(sys.argv) < 2:
        print("用法: python build_and_publish.py [clean|build|test|check|upload-test|upload|all]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "clean":
        clean_build()
    elif command == "build":
        clean_build()
        build_package()
    elif command == "test":
        run_tests()
    elif command == "check":
        build_package()
        check_package()
    elif command == "upload-test":
        build_package()
        check_package()
        upload_to_test_pypi()
    elif command == "upload":
        build_package()
        check_package()
        upload_to_pypi()
    elif command == "all":
        clean_build()
        run_tests()
        build_package()
        check_package()
        print("包已构建完成，可以手动上传到PyPI")
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
    
    print("操作完成!")


if __name__ == "__main__":
    main() 