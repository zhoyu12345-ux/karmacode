# KarmaCode 阿里云部署方案

## 架构对比

| 组件 | 原方案 | 阿里云方案 | 推荐 |
|------|--------|-----------|------|
| **前端** | Vercel (免费) | ECS + Nginx 或 OSS + CDN | ✅ Vercel（全球CDN，海外用户快） |
| **后端** | Render ($7/月) | **ECS** (~¥100/月) | ✅ 阿里云 ECS（国内访问快，便宜） |
| **数据库** | Supabase (免费) | ApsaraDB RDS (~¥300/月) | ✅ Supabase（免费额度够用） |
| **认证** | Supabase Auth | 自建 JWT | ✅ Supabase Auth（免开发） |
| **支付** | Stripe | Stripe | ✅ Stripe（海外用户习惯） |

---

## 推荐方案：阿里云 ECS + Vercel + Supabase + Stripe

```
海外用户 → Vercel（全球CDN）→ 前端 React
                ↓ API 请求
        阿里云 ECS（新加坡/美西）→ FastAPI 后端
                ↓
         Supabase（美西）→ 数据库 + 认证
                ↓
         Stripe → 支付
```

**为什么不全用阿里云？**
- Vercel 免费全球CDN，比阿里云全站加速效果更好
- Supabase 免费500MB数据库 + 5万月活，初期完全够了
- 只把后端放阿里云，性价比最高

---

## 第一步：购买阿里云 ECS

### 1.1 选配置
```
地域：新加坡 或 美西硅谷（海外用户优先）
实例：ecs.e-c1m2.large（2 vCPU, 4GB 内存）
系统：Ubuntu 22.04
带宽：按流量计费（100Mbps峰值）
磁盘：40GB ESSD
价格：约 ¥70-120/月
```

> 新用户去 aliyun.com 领优惠券，通常有免费试用

### 1.2 安全组设置
在 ECS 控制台 → 安全组 → 添加规则：

| 端口 | 来源 | 用途 |
|------|------|------|
| 22 | 你的IP | SSH |
| 80 | 0.0.0.0/0 | HTTP |
| 443 | 0.0.0.0/0 | HTTPS |
| 8000 | 0.0.0.0/0 | API（或用Nginx转发） |

---

## 第二步：连接服务器并部署

### 2.1 SSH 连接
```bash
ssh root@你的ECS公网IP
```

### 2.2 安装基础环境
```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python 3.11
apt install python3.11 python3.11-venv python3-pip nginx -y

# 安装 Git
apt install git -y
```

### 2.3 拉取代码
```bash
cd /opt
git clone https://github.com/你的用户名/karmacode.git
cd karmacode/backend
```

### 2.4 安装 Python 依赖（使用阿里云镜像）
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2.5 创建环境变量
```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-你的key
SUPABASE_URL=https://你的项目.supabase.co
SUPABASE_KEY=你的service_role_key
STRIPE_SECRET_KEY=sk_test_你的key
STRIPE_WEBHOOK_SECRET=whsec_你的key
FRONTEND_URL=https://karmacode.vercel.app
ENV=production
USE_MOCK_CLAUDE=false
EOF
```

### 2.6 创建 Systemd 服务（保证后台运行）
```bash
cat > /etc/systemd/system/karmacode.service << 'EOF'
[Unit]
Description=KarmaCode API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/karmacode/backend
EnvironmentFile=/opt/karmacode/backend/.env
ExecStart=/opt/karmacode/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable karmacode
systemctl start karmacode

# 检查状态
systemctl status karmacode
```

### 2.7 配置 Nginx 反向代理
```bash
cat > /etc/nginx/sites-available/karmacode << 'EOF'
server {
    listen 80;
    server_name api.你的域名.com;

    # API
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
EOF

ln -s /etc/nginx/sites-available/karmacode /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

## 第三步：HTTPS + 域名

### 3.1 域名解析（阿里云域名控制台）
```
api.你的域名.com → A记录 → ECS公网IP
```

### 3.2 免费 SSL 证书
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx -y

# 自动配置 HTTPS
certbot --nginx -d api.你的域名.com
```

---

## 第四步：前端部署（Vercel）

跟之前一样，只需改一个环境变量：

```
NEXT_PUBLIC_API_URL=https://api.你的域名.com
```

部署后前端会向阿里云 ECS 发 API 请求。

---

## 备选：前端也放阿里云

如果你想把前端也放阿里云（不用 Vercel）：

### 构建前端
```bash
# 在 ECS 上
cd /opt/karmacode/frontend
apt install nodejs npm -y
npm install --registry=https://registry.npmmirror.com
npm run build
```

### Nginx 配置同时服务前端和后端
```bash
cat > /etc/nginx/sites-available/karmacode << 'EOF'
server {
    listen 80;
    server_name karmacode.你的域名.com;

    # 前端静态文件
    root /opt/karmacode/frontend/out;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 转发到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

---

## 成本对比

| 方案 | 月费 | 说明 |
|------|------|------|
| **全 Render+Vercel+Supabase** | ~$7 | Render 750小时刚好够 |
| **阿里云 ECS + Vercel + Supabase** | ~¥100 | ECS 后端 + 免费前端 |
| **全阿里云** | ~¥300 | ECS + RDS + 带宽 |

---

## 总结建议

**初期用方案 A**（0成本，最快上线）:
- Vercel 前端 → 免费
- Render 后端 → 免费（750小时/月）
- Supabase → 免费

**有用户后用方案 B**（¥100/月，稳定）:
- Vercel 前端 → 免费
- **阿里云 ECS 后端** → 不限时，不会休眠
- Supabase → 免费

等日活过万再考虑 RDS 和全站迁移。
