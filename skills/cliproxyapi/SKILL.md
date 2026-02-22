---
name: cliproxyapi
description: 管理本机 CLIProxyAPI 配置，包括添加/修改 AI 提供商、模型别名、payload 规则、管理面板密码等，并能重启服务使配置生效。
---

# CLIProxyAPI 配置管理 Skill

## 环境信息

| 项目 | 值 |
|------|-----|
| 安装方式 | Homebrew |
| 可执行文件 | `/usr/local/opt/cliproxyapi/bin/cliproxyapi` |
| **配置文件** | `/usr/local/etc/cliproxyapi.conf` |
| 认证目录 | `~/.cli-proxy-api` |
| 服务端口 | `8317` |
| 代理 API Key | `my-local-proxy-key` |
| 管理面板 | `http://localhost:8317/management.html` |
| 管理面板密码 | 见配置文件 `remote-management.secret-key`（bcrypt hash，原始值为设置时的明文） |
| curl 路径 | `/usr/bin/curl`（系统 PATH 中 curl 可能不可用，始终用绝对路径） |

## 重要注意事项

- **始终使用 `/usr/bin/curl`**，不要用 `curl`（shell PATH 中可能找不到）
- **始终用 `--noproxy localhost,127.0.0.1`**，系统代理 `http_proxy=http://127.0.0.1:7890` 会干扰本地请求
- 配置文件支持**热重载**，修改后无需重启服务（约 1-2 秒生效）
- 管理接口认证：`Authorization: Bearer <secret-key明文>`
- `secret-key` 填明文后，服务启动时会自动 hash 成 bcrypt 存回配置文件

## 配置文件结构

```yaml
# 当前有效配置（非注释部分）
host: ""                          # 空 = 监听所有接口
port: 8317
remote-management:
  allow-remote: false
  secret-key: "<bcrypt-hash>"     # 管理面板密码
auth-dir: "~/.cli-proxy-api"
api-keys:
  - "my-local-proxy-key"          # 客户端访问代理的 Key

openai-compatibility:             # OpenAI 兼容提供商（如 NVIDIA）
  - name: "nvidia"
    base-url: "https://integrate.api.nvidia.com/v1"
    api-key-entries:
      - api-key: "<nvidia-api-key>"
    models:
      - name: "qwen/qwen3.5-397b-a17b"
        alias: "qwen3.5"

payload:
  override:                       # 强制注入参数
    - models:
        - name: "qwen/qwen3.5-397b-a17b"
        - name: "qwen3.5"
      params:
        "chat_template_kwargs.enable_thinking": true
  filter:                         # 过滤掉不兼容的参数
    - models:
        - name: "qwen/qwen3.5-397b-a17b"
        - name: "qwen3.5"
      params:
        - "reasoning_effort"      # Claude Code 发 "xhigh"，NVIDIA 不支持
```

## 常用操作

### 验证服务状态

```bash
/usr/bin/curl -s --noproxy localhost,127.0.0.1 \
  http://localhost:8317/v1/models \
  -H "Authorization: Bearer my-local-proxy-key"
```

### 测试管理接口

```bash
/usr/bin/curl -s --noproxy localhost,127.0.0.1\
  http://localhost:8317/v0/management/api-keys \
  -H "Authorization: Bearer <管理密码明文>"
```

### 重启服务

```bash
brew services restart cliproxyapi
```

### 查看服务日志

```bash
# 实时日志（服务以 stdout 方式运行时）
log show --predicate 'process == "cliproxyapi"' --last 5m
```

### 测试实际模型（绕过 Claude Code 的 cloaking）

```bash
/usr/bin/curl -s --noproxy localhost,127.0.0.1 \
  http://localhost:8317/v1/chat/completions \
  -H "Authorization: Bearer my-local-proxy-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5",
    "messages": [{"role": "user", "content": "你是什么模型？"}],
    "max_tokens": 100
  }'
```

## 在 Claude Code 中使用

```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:8317"
export ANTHROPIC_API_KEY="my-local-proxy-key"
claude --model "qwen3.5"
```

## 在 OpenClaw 中使用

在 `~/.openclaw/openclaw.json` 的 `models.providers` 中添加：

```json
"nvidia-proxy": {
  "baseUrl": "http://127.0.0.1:8317/v1",
  "apiKey": "my-local-proxy-key",
  "api": "openai-completions",
  "models": [
    {
      "id": "qwen3.5",
      "name": "Qwen3.5 397B (NVIDIA)",
      "reasoning": true,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 131072,
      "maxTokens": 16384
    }
  ]
}
```

## 常见问题

### Claude Code 报 400 reasoning_effort 错误

**原因**：Claude Code 自动发送 `reasoning_effort: "xhigh"`，NVIDIA vLLM 不支持该值。  
**解决**：在 `payload.filter` 中过滤掉 `reasoning_effort` 字段（已配置）。

### 模型回答"我是 Claude Sonnet 4.5"

**原因**：正常现象。Claude Code 在 system prompt 中注入了身份声明，Qwen 模型照着扮演。  
**实际模型**：`qwen/qwen3.5-397b-a17b`（NVIDIA 托管）。

### 管理面板登录报"服务器地址无效"

**原因**：系统代理 `http_proxy=127.0.0.1:7890` 干扰了浏览器对 localhost 的请求。  
**解决**：在浏览器代理设置中将 `localhost` 和 `127.0.0.1` 加入排除列表。

### 管理接口返回 404

**原因**：`remote-management.secret-key` 为空时，管理路由完全不注册。  
**解决**：设置非空的 `secret-key` 并重启服务。

### 配置修改后不生效

**原因**：YAML 格式错误（中文注释可能导致行截断）。  
**解决**：避免在 YAML 值的同一行写中文注释；修改后用以下命令验证：
```bash
/usr/bin/curl -s --noproxy localhost,127.0.0.1 \
  http://localhost:8317/v1/models \
  -H "Authorization: Bearer my-local-proxy-key"
```

## payload 规则说明

| 规则类型 | 说明 |
|---------|------|
| `override` | 强制覆盖请求中的参数值（无论原值是什么） |
| `default` | 仅在参数缺失时才设置默认值 |
| `filter` | 从请求中删除指定参数 |
| `override-raw` | 同 override，但值为原始 JSON 字符串 |

模型名支持通配符：`"qwen*"`、`"*-397b-*"` 等。

## 添加新提供商的步骤

1. 在 `/usr/local/etc/cliproxyapi.conf` 的 `openai-compatibility` 下追加新条目
2. 如有需要，在 `payload.filter` 中添加该提供商不支持的参数
3. 等待 1-2 秒热重载，或执行 `brew services restart cliproxyapi`
4. 用 `/v1/models` 接口验证模型已注册
