# 部署教程

本文档以一台 Linux 服务器部署为例，目标是把 FastAPI 服务部署为：

- PostgreSQL 作为生产数据库
- `uv` 管理依赖和运行命令
- Alembic 执行数据库迁移
- `systemd` 托管后端进程
- Nginx 作为反向代理

以下命令默认项目目录为 `/srv/testfastapi`，服务域名示例为 `api.example.com`。实际部署时请替换为你的路径和域名。

## 1. 服务器准备

建议环境：

- Python 3.14+
- PostgreSQL 15+
- Nginx
- Git
- uv

Ubuntu/Debian 示例：

```bash
sudo apt update
sudo apt install -y git nginx postgresql postgresql-contrib
curl -LsSf https://astral.sh/uv/install.sh | sh
```

确认 `uv` 可用：

```bash
uv --version
```

如果命令不存在，重新登录 SSH，或把 uv 安装脚本提示的路径加入 `PATH`。

## 2. 拉取代码

```bash
sudo mkdir -p /srv/testfastapi
sudo chown "$USER":"$USER" /srv/testfastapi
git clone <your-repo-url> /srv/testfastapi
cd /srv/testfastapi
```

安装依赖：

```bash
uv sync --frozen
```

如果服务器环境暂时不要求锁文件完全一致，可以使用：

```bash
uv sync
```

## 3. 创建生产数据库

进入 PostgreSQL：

```bash
sudo -u postgres psql
```

创建用户和数据库：

```sql
CREATE USER testfastapi WITH PASSWORD 'replace-with-strong-password';
CREATE DATABASE testfastapi OWNER testfastapi;
GRANT ALL PRIVILEGES ON DATABASE testfastapi TO testfastapi;
\q
```

生产数据库连接串格式：

```text
postgresql+psycopg://testfastapi:replace-with-strong-password@127.0.0.1:5432/testfastapi
```

## 4. 配置环境变量

项目通过 `.env` 读取配置。生产环境请在项目根目录创建 `.env`：

```bash
cd /srv/testfastapi
cp .env.example .env
```

如果项目还没有 `.env.example`，直接创建 `.env`：

```bash
touch .env
chmod 600 .env
```

推荐内容：

```dotenv
APP_NAME=testFastApi
DEBUG=false
DATABASE_URL=postgresql+psycopg://testfastapi:replace-with-strong-password@127.0.0.1:5432/testfastapi
TEST_DATABASE_URL=sqlite+pysqlite:///:memory:
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=["https://your-frontend.example.com"]
```

生成 `SECRET_KEY`：

```bash
openssl rand -hex 32
```

注意：

- `DEBUG` 必须是 `true` 或 `false`，不要写成 `release`。
- `ALGORITHM` 建议显式配置为 `HS256`。
- `CORS_ORIGINS` 是 JSON 数组字符串，前端域名上线后再填入。

## 5. 执行数据库迁移

在项目根目录执行：

```bash
cd /srv/testfastapi
uv run alembic upgrade head
```

检查当前迁移头：

```bash
uv run alembic current
uv run alembic heads
```

如果迁移失败，先不要启动服务；优先检查 `DATABASE_URL`、数据库用户权限、数据库是否存在。

## 6. 本机启动验证

先用前台方式启动一次：

```bash
uv run fastapi run app/main.py --host 127.0.0.1 --port 8000
```

另开一个终端检查健康接口：

```bash
curl http://127.0.0.1:8000/api/v1/health
```

也可以打开接口文档：

```text
http://127.0.0.1:8000/docs
```

确认无误后停止前台进程。

## 7. 配置 systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/testfastapi.service
```

写入：

```ini
[Unit]
Description=testFastApi FastAPI service
After=network.target postgresql.service

[Service]
Type=simple
WorkingDirectory=/srv/testfastapi
EnvironmentFile=/srv/testfastapi/.env
ExecStart=/usr/bin/env uv run fastapi run app/main.py --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

给运行用户项目访问权限：

```bash
sudo chown -R www-data:www-data /srv/testfastapi
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable testfastapi
sudo systemctl start testfastapi
sudo systemctl status testfastapi
```

查看日志：

```bash
sudo journalctl -u testfastapi -f
```

## 8. 配置 Nginx 反向代理

创建站点配置：

```bash
sudo nano /etc/nginx/sites-available/testfastapi
```

写入：

```nginx
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/testfastapi /etc/nginx/sites-enabled/testfastapi
sudo nginx -t
sudo systemctl reload nginx
```

检查外部访问：

```bash
curl http://api.example.com/api/v1/health
```

## 9. 配置 HTTPS

使用 Certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
```

续期检查：

```bash
sudo certbot renew --dry-run
```

## 10. 发布新版本

每次发布建议按这个顺序：

```bash
cd /srv/testfastapi
git pull
uv sync --frozen
uv run alembic upgrade head
sudo systemctl restart testfastapi
sudo systemctl status testfastapi
```

发布后检查：

```bash
curl https://api.example.com/api/v1/health
sudo journalctl -u testfastapi -n 100 --no-pager
```

## 11. 回滚建议

如果发布后接口异常：

```bash
cd /srv/testfastapi
git log --oneline -n 5
git checkout <previous-commit>
uv sync --frozen
sudo systemctl restart testfastapi
```

数据库迁移回滚要谨慎。先查看迁移历史：

```bash
uv run alembic history
uv run alembic current
```

确认可以回滚后再执行：

```bash
uv run alembic downgrade -1
```

生产环境数据库回滚前务必先备份。

## 12. 数据库备份

手动备份：

```bash
pg_dump "postgresql://testfastapi:replace-with-strong-password@127.0.0.1:5432/testfastapi" > backup-$(date +%F-%H%M%S).sql
```

恢复：

```bash
psql "postgresql://testfastapi:replace-with-strong-password@127.0.0.1:5432/testfastapi" < backup.sql
```

建议后续接入定时备份，并把备份文件同步到对象存储或另一台服务器。

## 13. 常见问题

### 配置启动时报 `debug` 解析失败

检查 `.env`：

```dotenv
DEBUG=false
```

不要写：

```dotenv
DEBUG=release
```

### 迁移连接不上数据库

检查：

- `DATABASE_URL` 是否正确
- PostgreSQL 是否运行：`sudo systemctl status postgresql`
- 数据库是否存在：`sudo -u postgres psql -l`
- 用户密码是否正确

### Nginx 可以访问，但接口返回 502

检查后端服务：

```bash
sudo systemctl status testfastapi
sudo journalctl -u testfastapi -n 100 --no-pager
curl http://127.0.0.1:8000/api/v1/health
```

### CORS 报错

确认 `.env` 中的 `CORS_ORIGINS` 包含前端实际域名，例如：

```dotenv
CORS_ORIGINS=["https://app.example.com"]
```

修改后重启：

```bash
sudo systemctl restart testfastapi
```

## 14. 上线前检查清单

- `.env` 已配置生产数据库和强随机 `SECRET_KEY`
- `DEBUG=false`
- `ALGORITHM=HS256`
- `uv run alembic upgrade head` 已执行成功
- `systemd` 服务能自动重启
- Nginx 反向代理配置通过 `nginx -t`
- HTTPS 证书已配置
- `/api/v1/health` 可访问
- 数据库已安排备份
- 发布和回滚流程已演练
