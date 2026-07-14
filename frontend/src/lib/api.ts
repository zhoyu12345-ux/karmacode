/**
 * KarmaCode - API Client
 * 与 FastAPI 后端通信
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface BirthData {
  birthDate: string;
  birthHour: number;
  birthMinute: number;
  gender: 'male' | 'female';
  longitude: number;
  latitude: number;
}

export interface ChartData {
  birth_info: {
    solar_date: string;
    solar_time: string;
    lunar_date: string;
    gender: string;
    animal: string;
    true_solar_hour: number;
  };
  pillars: Record<string, {
    stem: { char: string; en: string; element: string; element_en: string; yinyang: string };
    branch: { char: string; en: string; element: string; animal: string };
    nayin: string;
    hidden_stems: string[];
  }>;
  day_master: {
    char: string;
    en: string;
    element: string;
    element_en: string;
    yinyang: string;
  };
  shishen: Record<string, { name: string; en: string }>;
  dayun: {
    start_age: number;
    direction: string;
    cycles: Array<{
      order: number;
      age: string;
      age_start: number;
      stem: string;
      branch: string;
      element: string;
      element_en: string;
      nayin: string;
    }>;
  };
  shensha: Record<string, any>;
  wuxing_count: {
    counts: Record<string, number>;
    counts_en: Record<string, number>;
    dominant: string;
    dominant_en: string;
  };
}

export interface DailyFortuneData {
  date: string;
  flow_day: { stem: string; branch: string };
  daily_shishen: string;
  is_tiankedichong: boolean;
  is_fuyin: boolean;
  suggestions: { auspicious: string[]; caution: string[] };
  energy_level: string;
}

// ============================================================
// 八字排盘 API
// ============================================================

export async function calculateBazi(data: BirthData): Promise<ChartData> {
  const response = await fetch(`${API_BASE}/api/bazi/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      birth_date: data.birthDate,
      birth_hour: data.birthHour,
      birth_minute: data.birthMinute,
      gender: data.gender,
      longitude: data.longitude,
      latitude: data.latitude,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to calculate BaZi chart');
  }

  const result = await response.json();
  return result.data;
}

// ============================================================
// 每日运势 API
// ============================================================

export async function calculateDailyFortune(
  birthData: BirthData,
  targetDate: string
): Promise<DailyFortuneData> {
  const response = await fetch(`${API_BASE}/api/bazi/daily-fortune`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      birth_date: birthData.birthDate,
      birth_hour: birthData.birthHour,
      birth_minute: birthData.birthMinute,
      gender: birthData.gender,
      target_date: targetDate,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to calculate daily fortune');
  }

  const result = await response.json();
  return result.data;
}

// ============================================================
// AI 解读 API (流式)
// ============================================================

export type ReadingType = 'love' | 'wealth' | 'daily' | 'general';

export async function* streamReading(
  birthData: BirthData,
  readingType: ReadingType,
  targetDate?: string
): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE}/api/reading/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      birth_date: birthData.birthDate,
      birth_hour: birthData.birthHour,
      birth_minute: birthData.birthMinute,
      gender: birthData.gender,
      reading_type: readingType,
      stream: true,
      target_date: targetDate || null,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate reading');
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        try {
          const parsed = JSON.parse(data);
          if (parsed.text) yield parsed.text;
        } catch {
          // Skip unparseable chunks
        }
      }
    }
  }
}
