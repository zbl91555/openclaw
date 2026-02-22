# Cloudflare Tunnel Skill 使用指南

## 📦 技能位置
```
/Users/mudandan/.openclaw/workspace/skills/cloudflare-tunnel/
```

## 🚀 快速使用

### 方式 1：直接使用 Python 脚本

```bash
# 检查安装
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py check

# 快速创建临时隧道（暴露 8080 端口）
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py quick 8080

# 登录 Cloudflare（创建固定隧道需要）
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py login

# 创建命名隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py create my-app

# 列出所有隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py list

# 运行隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py run my-app
```

### 方式 2：直接使用 cloudflared 命令

```bash
# 临时隧道（最简单）
cloudflared tunnel --url http://localhost:8080

# 固定隧道
cloudflared tunnel login
cloudflared tunnel create my-tunnel
cloudflared tunnel run my-tunnel
```

### 方式 3：让 AI 助手帮你

直接告诉 OpenClaw：
- "帮我创建一个 Cloudflare Tunnel 暴露 8080 端口"
- "快速创建一个临时隧道"
- "配置固定隧道 my-app"

## 📋 常见场景

### 场景 1：快速分享本地项目
```bash
# 1. 启动本地服务器
cd /path/to/project
python3 -m http.server 8888

# 2. 创建隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py quick 8888

# 3. 分享生成的 URL
# https://xxx-xxx.trycloudflare.com
```

### 场景 2：Webhook 调试
```bash
# 1. 启动本地 webhook 服务
node webhook-server.js  # http://localhost:9000

# 2. 创建隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py quick 9000

# 3. 使用生成的 URL 作为回调地址
# https://xxx-xxx.trycloudflare.com/webhook
```

### 场景 3：长期服务
```bash
# 1. 登录
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py login

# 2. 创建隧道
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py create nas-service

# 3. 配置路由（编辑 ~/.cloudflared/config.yml）

# 4. 运行
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py run nas-service

# 5. 安装为服务（可选）
python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py service
```

## 🔧 故障排查

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8080

# 杀死进程
kill -9 <PID>
```

### cloudflared 未安装
```bash
# macOS
brew install cloudflared

# 验证
cloudflared --version
```

### 隧道连接失败
```bash
# 更新 cloudflared
brew upgrade cloudflared

# 重新登录
cloudflared tunnel login
```

## 📊 技能文件结构

```
cloudflare-tunnel/
├── SKILL.md              # 技能说明文档
├── _meta.json            # 元数据
└── scripts/
    └── tunnel_launcher.py  # 快速启动脚本
```

## 🎯 下一步

1. **测试临时隧道**
   ```bash
   python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py quick 8080
   ```

2. **配置固定隧道**（需要 Cloudflare 账号和域名）
   ```bash
   python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py login
   python3 skills/cloudflare-tunnel/scripts/tunnel_launcher.py create my-app
   ```

3. **让 AI 助手自动化**
   - 告诉 OpenClaw 你的需求
   - 它会自动使用这个技能创建隧道

## 📖 参考资料

- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [技能文档](./SKILL.md)
