-- ============================================================
-- KarmaCode - Supabase Database Schema
-- AI 八字命理平台数据库
-- ============================================================

-- 用户扩展表 (用户认证由 Supabase Auth 自动管理)
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 保存的命盘
CREATE TABLE saved_charts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  name TEXT DEFAULT 'My Chart',
  birth_date DATE NOT NULL,
  birth_hour INT NOT NULL,
  birth_minute INT DEFAULT 0,
  gender TEXT CHECK (gender IN ('male', 'female')),
  longitude FLOAT DEFAULT 120.0,
  latitude FLOAT DEFAULT 30.0,
  chart_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 解读历史
CREATE TABLE reading_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  chart_id UUID REFERENCES saved_charts,
  reading_type TEXT CHECK (reading_type IN ('love', 'wealth', 'daily', 'general', 'compatibility')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 支付记录
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  stripe_session_id TEXT UNIQUE,
  amount DECIMAL(10,2) NOT NULL,
  currency TEXT DEFAULT 'usd',
  status TEXT DEFAULT 'pending',
  product_type TEXT DEFAULT 'book_of_destiny',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- RLS (Row Level Security) 策略
-- ============================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- profiles: 用户只能查看和更新自己的资料
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- saved_charts: 用户只能访问自己的命盘
CREATE POLICY "Users can view own charts"
  ON saved_charts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own charts"
  ON saved_charts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own charts"
  ON saved_charts FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own charts"
  ON saved_charts FOR DELETE
  USING (auth.uid() = user_id);

-- reading_history: 用户只能访问自己的解读历史
CREATE POLICY "Users can view own readings"
  ON reading_history FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own readings"
  ON reading_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own readings"
  ON reading_history FOR DELETE
  USING (auth.uid() = user_id);

-- payments: 用户只能查看自己的支付记录
CREATE POLICY "Users can view own payments"
  ON payments FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================================
-- 索引
-- ============================================================

CREATE INDEX idx_saved_charts_user_id ON saved_charts(user_id);
CREATE INDEX idx_reading_history_user_id ON reading_history(user_id);
CREATE INDEX idx_reading_history_chart_id ON reading_history(chart_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_stripe_session_id ON payments(stripe_session_id);

-- ============================================================
-- 触发器: 新用户自动创建 profile
-- ============================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 当新用户注册时自动触发
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();
