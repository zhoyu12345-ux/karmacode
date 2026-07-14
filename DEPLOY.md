# KarmaCode 部署指南

## 整体架构

```
用户 → Vercel (React前端) → Render (FastAPI后端) → Claude API
                              ↓
                         Supabase (数据库/Auth)
                              ↓
                         Stripe (支付)
```

## 第一步：GitHub 推送

```bash
cd E:\test\karmacode

# 创建 GitHub 仓库并推送
gh repo create karmacode --public --source=. --push
# 或者手动：
# 1. 在 github.com 新建仓库 karmacode
# 2. git remote add origin https://github.com/你的用户名/karmacode.git
# 3. git branch -M main
# 4. git push -u origin main
```

---

## 第二步：Supabase（数据库 + 认证）

### 2.1 创建项目
1. 打开 https://supabase.com 注册/登录
2. 点击 "New Project"
3. 输入名称: `karmacode`
4. 设置数据库密码（记下来）
5. 选择区域: West US (离 Vercel 近)
6. 等待创建完成（约2分钟）

### 2.2 导入数据库
1. 进入 SQL Editor
2. 复制 `supabase/schema.sql` 全部内容
3. 粘贴并执行 (Run)

### 2.3 设置认证
1. 进入 Authentication → Providers
2. 启用 **Email** (默认已启用)
3. 可选: 启用 **Google** (需要 Google Cloud OAuth 凭据)

### 2.4 获取连接信息
进入 Settings → API，复制以下值：

| 变量 | 值 | 用途 |
|------|-----|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Project URL | 前端连接 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon public key | 前端连接 |
| `SUPABASE_URL` | Project URL | 后端连接 |
| `SUPABASE_KEY` | service_role key | 后端操作 |

---

## 第三步：Stripe（支付）

### 3.1 注册
1. 打开 https://stripe.com 注册
2. 切换到 **Test Mode**（开发阶段）

### 3.2 获取密钥
进入 Developers → API keys：

| 变量 | 值 |
|------|-----|
| `STRIPE_SECRET_KEY` | Secret key (sk_test_xxx) |
| `STRIPE_PUBLISHABLE_KEY` | Publishable key (pk_test_xxx) |

### 3.3 设置 Webhook
1. 进入 Developers → Webhooks → Add endpoint
2. URL: `https://你的后端域名/api/payment/webhook`
3. Events: `checkout.session.completed`
4. 复制 Signing secret → `STRIPE_WEBHOOK_SECRET`

---

## 第四步：Claude API

1. 打开 https://console.anthropic.com
2. 创建 API Key
3. 复制 → `ANTHROPIC_API_KEY`

---

## 第五步：Render（后端部署）

### 5.1 创建 Web Service
1. 打开 https://render.com 注册/登录
2. 点击 New → Web Service
3. 连接 GitHub 仓库 `karmacode`
4. 配置:

```
Name: karmacode-api
Root Directory: backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 5.2 环境变量
在 Render 的 Environment 设置中添加:

```
ANTHROPIC_API_KEY=sk-ant-xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
FRONTEND_URL=https://karmacode.vercel.app
ENV=production
USE_MOCK_CLAUDE=false
```

### 5.3 部署
点击 "Create Web Service"，等待构建完成。
记下 Render 分配的域名（如 `karmacode-api.onrender.com`）。

---

## 第六步：Vercel（前端部署）

### 6.1 部署
1. 打开 https://vercel.com 注册/登录
2. 点击 "Add New" → "Project"
3. 导入 GitHub 仓库 `karmacode`
4. 配置:

```
Framework: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
```

### 6.2 环境变量
在 Vercel 的 Environment Variables 中添加:

```
NEXT_PUBLIC_API_URL=https://karmacode-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

### 6.3 部署
点击 "Deploy"，等待完成。
访问 Vercel 分配的域名（如 `karmacode.vercel.app`）。

---

## 第七步：验证

1. 访问 `https://karmacode.vercel.app` — 首页是否正常
2. 输入生日 → 排盘正常
3. 切换男女 → 解读不同
4. 访问 `/love`, `/wealth`, `/daily` → 页面正常
5. 点击 "Unlock" → Stripe Checkout 正常（测试模式）
6. 支付后 → 完整命之书可见

---

## 可选：自定义域名

在 Vercel 设置中添加自定义域名（如 `karmacode.com`），并在 Render 更新 `FRONTEND_URL`。

---

## 成本预估

| 服务 | 免费额度 | 超出后 |
|------|----------|--------|
| Vercel | 100GB带宽/月 | $20/月 Pro |
| Render | 750小时/月 (刚好够1个实例) | $7/月起 |
| Supabase | 500MB数据库, 5万月活用户 | $25/月 Pro |
| Stripe | 无月费 | 2.9% + $0.30/笔 |
| Claude API | 无免费额度 | 按token计费 |
