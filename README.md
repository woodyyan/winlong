# Winlong

Winlong 是一个前后端分离的站点：

- 前端：`apps/web`，基于 Next.js 15
- 后端：`apps/api`，基于 FastAPI
- 本地一键启动脚本：`start-local.sh`

## 项目功能

Winlong 的核心目标，是把一组加密货币按多因子模型做统一打分，并以可视化方式展示给用户，帮助快速筛选值得关注的标的。

当前版本已经覆盖这些功能：

- AI 因子币种排行榜：首页会拉取全量币池数据，按总分展示币种排名
- 搜索和前端筛选：支持按币种名、符号、中文名、标签搜索，并支持自选、动量、高流动性、AI 主题、排名上升等筛选
- 自选列表：用户可以在前端维护自己的关注币种列表
- 币种详情页：展示单个币种的价格走势、评分走势、四类因子雷达图、类别得分拆解和衍生品数据
- 系统状态页：展示评分调度时间、池内规模、数据质量、运行时长、数据源健康状态和最近日志
- API 服务：后端提供币种列表、币种详情、历史数据、系统状态和健康检查接口

当前页面结构大致分为三块：

- 首页排行榜：用于快速筛选和浏览全站币池
- 币种详情页：用于查看单个币的评分构成和走势
- 状态页：用于查看系统运行情况和数据健康度

这一版已经把前端壳子、交互结构和基础 API 路由打通，后续可以继续把模拟数据替换成真实采集与评分任务，而不需要推翻现有展示层。

## 本地开发

直接运行：

```bash
./start-local.sh
```

默认行为：

- 后端启动在 `127.0.0.1:8001`
- 前端启动在 `127.0.0.1:3001`
- 脚本会自动写入 `apps/web/.env.local`

## 线上部署

仓库内已包含 GitHub Actions 工作流：`[deploy-web.yml](/Users/yansongbai/Documents/Documents - WOODYYAN-MC2/projects/winlong/.github/workflows/deploy-web.yml)`。

工作流会执行这些步骤：

1. 在 GitHub Actions 中构建 `apps/web`
2. 生成 Next.js standalone 部署包
3. 通过 SSH 用户名 + 密码把部署包传到服务器
4. 在服务器上用 Docker 启动前端容器
5. 部署完成后自动执行健康检查

当前前端已改为同源代理方案：

- 浏览器访问站点时，请求 `/api/...`
- Next.js 再把 `/api/...` 转发到后端 `API_BASE_URL`
- 因此不再需要 `NEXT_PUBLIC_API_BASE_URL`

## 需要配置的 GitHub Secrets

进入仓库：`Settings -> Secrets and variables -> Actions`，添加以下 secrets。

必填：

- `DEPLOY_HOST`：服务器 IP 或主机名
- `DEPLOY_SSH_PORT`：SSH 端口，通常是 `22`
- `DEPLOY_USERNAME`：SSH 登录用户名
- `DEPLOY_PASSWORD`：SSH 登录密码
- `DEPLOY_PATH`：服务器部署目录，例如 `/srv/winlong-web`
- `WEB_PORT`：Next.js 在服务器本机监听的端口，例如 `3001`
- `API_BASE_URL`：后端服务地址，例如 `http://127.0.0.1:8001`

可选：

- `HEALTHCHECK_URL`：部署后的健康检查地址

如果不填 `HEALTHCHECK_URL`，工作流默认检查：

```text
http://127.0.0.1:3001/status
```

## 服务器前提

当前工作流假设服务器已经具备这些条件：

- 已安装 Docker
- 后端 API 已经在服务器上运行，且 `API_BASE_URL` 可从前端进程所在机器访问

如果你还需要 Caddy、Nginx 或其他反向代理，请在服务器上单独维护，不再由这个 deploy workflow 管理。

## 健康检查

部署脚本会在前端进程启动后执行：

```bash
curl --fail --silent --show-error --retry 5 --retry-delay 2 http://127.0.0.1:3001/status
```

如果你配置了 `HEALTHCHECK_URL`，则会改为检查该地址。

## 相关文件

- 前端同源代理配置：`[next.config.mjs](/Users/yansongbai/Documents/Documents - WOODYYAN-MC2/projects/winlong/apps/web/next.config.mjs)`
- 前端 API 访问逻辑：`[api.ts](/Users/yansongbai/Documents/Documents - WOODYYAN-MC2/projects/winlong/apps/web/src/lib/api.ts)`
- 自动部署工作流：`[deploy-web.yml](/Users/yansongbai/Documents/Documents - WOODYYAN-MC2/projects/winlong/.github/workflows/deploy-web.yml)`
