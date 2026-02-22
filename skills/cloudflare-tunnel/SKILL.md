---
name: cloudflare-tunnel
description: 快速创建 Cloudflare Tunnel 内网穿透，支持临时隧道和固定隧道配置。
when: "When user needs to expose local services to internet via Cloudflare Tunnel."
examples:
  - "创建一个临时隧道"
  - "配置固定隧道"
  - "把 8080 端口暴露到公网"
  - "查看隧道状态"
metadata:
  {
    "openclaw": {
      "emoji": "🌐",
      "requires": { "bins": ["cloudflared"] }
    }
  }
---

# Cloudflare Tunnel

## 快速开始

### 临时隧道（无需配置）
```bash
# 暴露本地 8080 端口
cloudflared tunnel --url http://localhost:8080
```

**输出：**
```
https://random-name.trycloudflare.com
```

### 固定隧道（长期有效）

#### 1️⃣ 创建隧道
```bash
cloudflared tunnel create my-tunnel
```

#### 2️⃣ 配置隧道
创建 `~/.cloudflared/config.yml`:
```yaml
tunnel: my-tunnel
credentials-file: /Users/xxx/.cloudflared/my-tunnel.json

ingress:
  - service: http://localhost:8080
    hostname: myapp.example.com
  - service: http://localhost:3000
    hostname: api.example.com
  - service: http_status:404  # 默认 404
```

#### 3️⃣ 运行隧道
```bash
# 前台运行
cloudflared tunnel run my-tunnel

# 后台运行
cloudflared service install
cloudflared service start
```

#### 4️⃣ DNS 配置
在 Cloudflare Dashboard 添加 CNAME 记录：
```
myapp.example.com  CNAME  my-tunnel.cfargotunnel.com
```

## 常用命令

| 命令 | 描述 |
|------|------|
| `cloudflared tunnel list` | 列出隧道 |
| `cloudflared tunnel create <name>` | 创建隧道 |
| `cloudflared tunnel run <name>` | 运行隧道 |
| `cloudflared tunnel delete <name>` | 删除隧道 |
| `cloudflared service install` | 安装系统服务 |
| `cloudflared service start` | 启动服务 |
| `cloudflared service stop` | 停止服务 |

## 配置示例

### 暴露多个服务
```yaml
tunnel: my-tunnel
credentials-file: /path/to/creds.json

ingress:
  # Web 应用
  - service: http://localhost:3000
    hostname: app.example.com
  
  # API 服务
  - service: http://localhost:8080
    hostname: api.example.com
    path: /api/*
  
  # WebSocket
  - service: http://localhost:9000
    hostname: ws.example.com
  
  # 默认 404
  - service: http_status:404
```

### 添加认证
```yaml
access:
  - domain: example.com
    policy:
      - require:
        - email:
            domain: company.com
```

## 故障排查

**查看状态：**
```bash
cloudflared tunnel list
cloudflared service status
```

**查看日志：**
```bash
# macOS
tail -f /var/log/cloudflared.log

# Linux
journalctl -u cloudflared -f
```

**测试连接：**
```bash
curl -I https://myapp.example.com
```
