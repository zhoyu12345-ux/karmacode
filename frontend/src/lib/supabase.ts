/**
 * KarmaCode - Supabase 客户端
 * 数据库 CRUD 操作，带 localStorage 降级方案
 */

import { createClient } from '@supabase/supabase-js';

// Generic database type (to be replaced with generated types after supabase link)
type Database = Record<string, any>;

// ============================================================
// 环境变量
// ============================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// ============================================================
// 类型定义
// ============================================================

export interface Profile {
  id: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
}

export interface SavedChart {
  id: string;
  user_id: string;
  name: string;
  birth_date: string;
  birth_hour: number;
  birth_minute: number;
  gender: 'male' | 'female' | null;
  longitude: number;
  latitude: number;
  chart_data: Record<string, unknown>;
  created_at: string;
}

export interface ReadingHistory {
  id: string;
  user_id: string;
  chart_id: string | null;
  reading_type: 'love' | 'wealth' | 'daily' | 'general' | 'compatibility';
  content: string;
  created_at: string;
}

export interface Payment {
  id: string;
  user_id: string;
  stripe_session_id: string | null;
  amount: number;
  currency: string;
  status: string;
  product_type: string;
  created_at: string;
}

/** 保存命盘时的输入参数 */
export interface SaveChartInput {
  name?: string;
  birth_date: string;
  birth_hour: number;
  birth_minute?: number;
  gender?: 'male' | 'female';
  longitude?: number;
  latitude?: number;
  chart_data: Record<string, unknown>;
}

// ============================================================
// Supabase 客户端（仅在配置了环境变量时初始化）
// ============================================================

let supabaseClient: ReturnType<typeof createClient<Database>> | null = null;

function getSupabase() {
  if (!supabaseUrl || !supabaseAnonKey) {
    return null;
  }
  if (!supabaseClient) {
    supabaseClient = createClient<Database>(supabaseUrl, supabaseAnonKey);
  }
  return supabaseClient;
}

export const supabase = getSupabase();

// ============================================================
// localStorage 降级方案
// ============================================================

const LS_KEYS = {
  charts: 'karmacode_saved_charts',
  readings: 'karmacode_reading_history',
  profile: 'karmacode_profile',
} as const;

function lsGet<T>(key: string): T[] {
  if (typeof window === 'undefined') return [];
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function lsSet<T>(key: string, data: T[]): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    console.warn('Failed to save to localStorage');
  }
}

function lsGetOne<T extends { id: string }>(key: string): T | null {
  if (typeof window === 'undefined') return null;
  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

function lsSetOne<T>(key: string, data: T): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    console.warn('Failed to save to localStorage');
  }
}

// ============================================================
// Profiles
// ============================================================

export async function getProfile(userId: string): Promise<Profile | null> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();

    if (error) {
      console.error('Failed to get profile:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  return lsGetOne<Profile>(LS_KEYS.profile);
}

export async function updateProfile(
  userId: string,
  updates: Partial<Pick<Profile, 'full_name' | 'avatar_url'>>
): Promise<Profile | null> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('profiles')
      .update(updates)
      .eq('id', userId)
      .select()
      .single();

    if (error) {
      console.error('Failed to update profile:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  const existing = lsGetOne<Profile>(LS_KEYS.profile);
  const updated: Profile = {
    id: userId,
    full_name: updates.full_name ?? existing?.full_name ?? null,
    avatar_url: updates.avatar_url ?? existing?.avatar_url ?? null,
    created_at: existing?.created_at ?? new Date().toISOString(),
  };
  lsSetOne(LS_KEYS.profile, updated);
  return updated;
}

// ============================================================
// Saved Charts - 保存的命盘
// ============================================================

export async function saveChart(
  userId: string,
  chartData: Record<string, unknown>,
  birthInfo: Omit<SaveChartInput, 'chart_data'>
): Promise<SavedChart | null> {
  const newChart = {
    user_id: userId,
    name: birthInfo.name || 'My Chart',
    birth_date: birthInfo.birth_date,
    birth_hour: birthInfo.birth_hour,
    birth_minute: birthInfo.birth_minute ?? 0,
    gender: birthInfo.gender ?? null,
    longitude: birthInfo.longitude ?? 120.0,
    latitude: birthInfo.latitude ?? 30.0,
    chart_data: chartData,
  };

  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('saved_charts')
      .insert(newChart)
      .select()
      .single();

    if (error) {
      console.error('Failed to save chart:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  const charts = lsGet<SavedChart>(LS_KEYS.charts);
  const saved: SavedChart = {
    id: crypto.randomUUID(),
    ...newChart,
    created_at: new Date().toISOString(),
  };
  charts.push(saved);
  lsSet(LS_KEYS.charts, charts);
  return saved;
}

export async function getUserCharts(userId: string): Promise<SavedChart[]> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('saved_charts')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Failed to get charts:', error);
      return [];
    }
    return data;
  }

  // 降级: localStorage
  const charts = lsGet<SavedChart>(LS_KEYS.charts);
  return charts
    .filter((c) => c.user_id === userId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

export async function getChartById(chartId: string): Promise<SavedChart | null> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('saved_charts')
      .select('*')
      .eq('id', chartId)
      .single();

    if (error) {
      console.error('Failed to get chart:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  const charts = lsGet<SavedChart>(LS_KEYS.charts);
  return charts.find((c) => c.id === chartId) ?? null;
}

export async function deleteChart(chartId: string): Promise<boolean> {
  const client = getSupabase();
  if (client) {
    const { error } = await client
      .from('saved_charts')
      .delete()
      .eq('id', chartId);

    if (error) {
      console.error('Failed to delete chart:', error);
      return false;
    }
    return true;
  }

  // 降级: localStorage
  const charts = lsGet<SavedChart>(LS_KEYS.charts);
  const filtered = charts.filter((c) => c.id !== chartId);
  lsSet(LS_KEYS.charts, filtered);
  return true;
}

export async function updateChartName(
  chartId: string,
  name: string
): Promise<SavedChart | null> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('saved_charts')
      .update({ name })
      .eq('id', chartId)
      .select()
      .single();

    if (error) {
      console.error('Failed to update chart name:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  const charts = lsGet<SavedChart>(LS_KEYS.charts);
  const idx = charts.findIndex((c) => c.id === chartId);
  if (idx === -1) return null;
  charts[idx].name = name;
  lsSet(LS_KEYS.charts, charts);
  return charts[idx];
}

// ============================================================
// Reading History - 解读历史
// ============================================================

export async function saveReading(
  userId: string,
  chartId: string | null,
  readingType: ReadingHistory['reading_type'],
  content: string
): Promise<ReadingHistory | null> {
  const newReading = {
    user_id: userId,
    chart_id: chartId,
    reading_type: readingType,
    content,
  };

  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('reading_history')
      .insert(newReading)
      .select()
      .single();

    if (error) {
      console.error('Failed to save reading:', error);
      return null;
    }
    return data;
  }

  // 降级: localStorage
  const readings = lsGet<ReadingHistory>(LS_KEYS.readings);
  const saved: ReadingHistory = {
    id: crypto.randomUUID(),
    ...newReading,
    created_at: new Date().toISOString(),
  };
  readings.push(saved);
  lsSet(LS_KEYS.readings, readings);
  return saved;
}

export async function getReadingHistory(
  userId: string,
  readingType?: ReadingHistory['reading_type']
): Promise<ReadingHistory[]> {
  const client = getSupabase();
  if (client) {
    let query = client
      .from('reading_history')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (readingType) {
      query = query.eq('reading_type', readingType);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Failed to get reading history:', error);
      return [];
    }
    return data;
  }

  // 降级: localStorage
  let readings = lsGet<ReadingHistory>(LS_KEYS.readings);
  readings = readings
    .filter((r) => r.user_id === userId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  if (readingType) {
    readings = readings.filter((r) => r.reading_type === readingType);
  }

  return readings;
}

export async function deleteReading(readingId: string): Promise<boolean> {
  const client = getSupabase();
  if (client) {
    const { error } = await client
      .from('reading_history')
      .delete()
      .eq('id', readingId);

    if (error) {
      console.error('Failed to delete reading:', error);
      return false;
    }
    return true;
  }

  // 降级: localStorage
  const readings = lsGet<ReadingHistory>(LS_KEYS.readings);
  const filtered = readings.filter((r) => r.id !== readingId);
  lsSet(LS_KEYS.readings, filtered);
  return true;
}

export async function getReadingsByChart(
  userId: string,
  chartId: string
): Promise<ReadingHistory[]> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('reading_history')
      .select('*')
      .eq('user_id', userId)
      .eq('chart_id', chartId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Failed to get readings by chart:', error);
      return [];
    }
    return data;
  }

  // 降级: localStorage
  const readings = lsGet<ReadingHistory>(LS_KEYS.readings);
  return readings
    .filter((r) => r.user_id === userId && r.chart_id === chartId)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

// ============================================================
// Payments - 支付记录
// ============================================================

export async function getUserPayments(userId: string): Promise<Payment[]> {
  const client = getSupabase();
  if (client) {
    const { data, error } = await client
      .from('payments')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Failed to get payments:', error);
      return [];
    }
    return data;
  }

  // 支付记录不做 localStorage 降级（涉及资金安全）
  return [];
}

export async function getPaymentBySessionId(
  sessionId: string
): Promise<Payment | null> {
  const client = getSupabase();
  if (!client) return null;

  const { data, error } = await client
    .from('payments')
    .select('*')
    .eq('stripe_session_id', sessionId)
    .single();

  if (error) {
    console.error('Failed to get payment by session:', error);
    return null;
  }
  return data;
}
