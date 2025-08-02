# homelab_config

[![✅ Code Quality & Tests](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/ci-tests.yaml)
[![🚀 Release Build & Publish](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/package-release.yaml/badge.svg)](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/package-release.yaml)
[![📚 Deploy Documentation](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/docs-deploy.yaml/badge.svg)](https://github.com/shawndeng-homelab/homelab-config/actions/workflows/docs-deploy.yaml)

一个基于 Consul 的家庭实验室配置管理工具，提供环境感知和缓存功能。

## 功能特点

- 🌍 多环境支持 (dev/staging/prod)
- 🔒 安全的配置存储和访问
- 🚀 高性能缓存机制
- ⚡ 灵活的 Consul 连接管理
- 🔄 自动故障转移支持
- 📝 完整的类型注解支持

## 安装

```bash
# 使用 pip 安装
pip install homelab_config

# 使用 uv 安装
uv pip install homelab_config
```

## 快速开始

```python
from homelab_config import create_client

# 创建客户端
client = create_client()

# 获取配置 (使用默认环境)
config = client("app/myapp/config")

# 获取特定环境的配置
dev_config = client("app/myapp/config,dev")
prod_config = client("app/myapp/config,prod")
```

## 配置

支持通过环境变量进行配置：

```bash
# 运行环境设置
HOMELAB_ENVIRONMENT=dev

# Consul 服务器地址 (支持多个地址，用逗号分隔)
HOMELAB_CONSUL_URLS=http://localhost:8500

# Consul 认证令牌 (可选)
HOMELAB_CONSUL_TOKEN=your-token

# 连接缓存时间 (秒)
HOMELAB_CONSUL_CACHE_TTL=300
```
