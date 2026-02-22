#!/usr/bin/env python3
"""
Cloudflare Tunnel Quick Launcher
快速创建和管理 Cloudflare Tunnel
"""

import subprocess
import sys
import json
import os
from datetime import datetime

def check_cloudflared():
    """检查 cloudflared 是否安装"""
    try:
        result = subprocess.run(
            ['cloudflared', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ cloudflared 已安装：{result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ cloudflared 未安装")
        print("\n安装命令:")
        print("  macOS:  brew install cloudflared")
        print("  Linux:  wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
        return False

def create_quick_tunnel(port=8080, protocol='http'):
    """创建临时隧道"""
    url = f"{protocol}://localhost:{port}"
    print(f"🚀 正在创建临时隧道...")
    print(f"📍 本地地址：{url}")
    print()
    
    try:
        cmd = ['cloudflared', 'tunnel', '--url', url]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ 隧道已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建失败：{e}")
        sys.exit(1)

def login():
    """登录 Cloudflare"""
    print("🔐 正在打开浏览器登录...")
    try:
        subprocess.run(['cloudflared', 'tunnel', 'login'], check=True)
        print("✅ 登录成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 登录失败：{e}")
        sys.exit(1)

def create_named_tunnel(name):
    """创建命名隧道"""
    print(f"🚇 正在创建隧道：{name}")
    try:
        subprocess.run(['cloudflared', 'tunnel', 'create', name], check=True)
        print(f"✅ 隧道 {name} 创建成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建失败：{e}")
        sys.exit(1)

def list_tunnels():
    """列出所有隧道"""
    print("📋 隧道列表:")
    try:
        result = subprocess.run(
            ['cloudflared', 'tunnel', 'list', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        tunnels = json.loads(result.stdout)
        for tunnel in tunnels:
            print(f"\n  🔹 {tunnel.get('name', 'N/A')}")
            print(f"     ID: {tunnel.get('id', 'N/A')}")
            created = tunnel.get('createdat', 'N/A')
            print(f"     创建时间：{created}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取失败：{e}")
        sys.exit(1)

def run_tunnel(name):
    """运行隧道"""
    print(f"🚀 正在启动隧道：{name}")
    try:
        subprocess.run(['cloudflared', 'tunnel', 'run', name], check=True)
    except KeyboardInterrupt:
        print("\n✅ 隧道已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败：{e}")
        sys.exit(1)

def install_service():
    """安装为系统服务"""
    print("🔧 正在安装系统服务...")
    try:
        subprocess.run(['cloudflared', 'service', 'install'], check=True)
        print("✅ 服务安装成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败：{e}")
        sys.exit(1)

def show_help():
    """显示帮助"""
    help_text = """
🚇 Cloudflare Tunnel 快速启动器

用法:
  python3 cloudflare_tunnel.py quick [端口]     创建临时隧道 (默认 8080)
  python3 cloudflare_tunnel.py login            登录 Cloudflare
  python3 cloudflare_tunnel.py create <名称>    创建命名隧道
  python3 cloudflare_tunnel.py list             列出所有隧道
  python3 cloudflare_tunnel.py run <名称>       运行隧道
  python3 cloudflare_tunnel.py service          安装为系统服务
  python3 cloudflare_tunnel.py check            检查安装状态
  python3 cloudflare_tunnel.py help             显示帮助

示例:
  # 快速创建临时隧道暴露 8080 端口
  python3 cloudflare_tunnel.py quick 8080
  
  # 创建固定隧道
  python3 cloudflare_tunnel.py login
  python3 cloudflare_tunnel.py create my-app
  python3 cloudflare_tunnel.py run my-app
  
  # 检查 cloudflared 是否安装
  python3 cloudflare_tunnel.py check
"""
    print(help_text)

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        check_cloudflared()
    
    elif command == 'quick':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        if check_cloudflared():
            create_quick_tunnel(port)
    
    elif command == 'login':
        if check_cloudflared():
            login()
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ 请提供隧道名称")
            print("用法：python3 cloudflare_tunnel.py create <名称>")
            sys.exit(1)
        if check_cloudflared():
            create_named_tunnel(sys.argv[2])
    
    elif command == 'list':
        if check_cloudflared():
            list_tunnels()
    
    elif command == 'run':
        if len(sys.argv) < 3:
            print("❌ 请提供隧道名称")
            print("用法：python3 cloudflare_tunnel.py run <名称>")
            sys.exit(1)
        if check_cloudflared():
            run_tunnel(sys.argv[2])
    
    elif command == 'service':
        if check_cloudflared():
            install_service()
    
    elif command == 'help':
        show_help()
    
    else:
        print(f"❌ 未知命令：{command}")
        show_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
