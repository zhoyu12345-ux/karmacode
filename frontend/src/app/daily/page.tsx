'use client';

import { useState, useCallback, useMemo } from 'react';
import BirthForm, { BirthData } from '@/components/BirthForm';
import ChartDisplay from '@/components/ChartDisplay';
import DailyFortune, { DailyFortuneData } from '@/components/DailyFortune';
import ReadingStream from '@/components/ReadingStream';
import Paywall from '@/components/Paywall';
import { calculateBazi, calculateDailyFortune, streamReading, ChartData } from '@/lib/api';

// ===== Helper: Get today's date as YYYY-MM-DD =====
function getTodayISO(): string {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

// ===== Helper: Map API daily fortune to component's expected shape =====
function mapDailyFortune(apiData: {
  date: string;
  flow_day: { stem: string; branch: string };
  daily_shishen: string;
  is_tiankedichong: boolean;
  is_fuyin: boolean;
  suggestions: { auspicious: string[]; caution: string[] };
  energy_level: string;
}): DailyFortuneData {
  const energyLevelMap: Record<string, DailyFortuneData['energyLevel']> = {
    auspicious: 'auspicious',
    favorable: 'auspicious',
    good: 'auspicious',
    neutral: 'neutral',
    caution: 'caution',
    warning: 'caution',
    danger: 'danger',
    bad: 'danger',
  };

  const energyLabelMap: Record<string, string> = {
    auspicious: '大吉 · Auspicious',
    neutral: '平顺 · Neutral',
    caution: '注意 · Caution',
    danger: '避凶 · Warning',
  };

  const energyDescriptionMap: Record<string, string> = {
    auspicious: 'The cosmic energies align favorably today. A wonderful day for important endeavors, social activities, and new beginnings.',
    neutral: 'A balanced day with stable energies. Proceed with your regular activities — neither particularly favorable nor unfavorable.',
    caution: 'Exercise mindful awareness today. Some friction in the cosmic flow suggests patience and careful decision-making.',
    danger: 'Challenging energies prevail today. Best to lay low, avoid major decisions, and focus on rest and reflection.',
  };

  const energyLevel = energyLevelMap[apiData.energy_level] || 'neutral';

  const warnings: string[] = [];
  if (apiData.is_tiankedichong) {
    warnings.push('Heaven-Earth Clash (天克地冲) detected — a day of significant cosmic friction. Avoid confrontations and major decisions.');
  }
  if (apiData.is_fuyin) {
    warnings.push('Fu Yin (伏吟) pattern present — repetitive energies may bring stagnation or revisiting past issues.');
  }

  return {
    date: apiData.date,
    energyLevel,
    energyLabel: energyLabelMap[energyLevel] || energyLabelMap.neutral,
    energyDescription: energyDescriptionMap[energyLevel] || energyDescriptionMap.neutral,
    goodActivities: apiData.suggestions.auspicious || [],
    badActivities: apiData.suggestions.caution || [],
    specialWarning: warnings.length > 0 ? warnings.join(' ') : undefined,
  };
}

export default function DailyPage() {
  const [chart, setChart] = useState<ChartData | null>(null);
  const [reading, setReading] = useState<string>('');
  const [dailyFortuneData, setDailyFortuneData] = useState<DailyFortuneData | null>(null);
  const [targetDate, setTargetDate] = useState<string>(getTodayISO());
  const [isCalculating, setIsCalculating] = useState(false);
  const [isReading, setIsReading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [readingChars, setReadingChars] = useState(0);

  const handleBirthSubmit = useCallback(async (data: BirthData) => {
    setIsCalculating(true);
    setError(null);
    setReading('');
    setBirthData(data);
    setDailyFortuneData(null);

    try {
      // 1. Calculate BaZi chart
      const chartData = await calculateBazi(data);
      setChart(chartData);

      // 2. Calculate daily fortune for the selected date
      const fortuneApiData = await calculateDailyFortune(data, targetDate);
      const fortuneMapped = mapDailyFortune(fortuneApiData);
      setDailyFortuneData(fortuneMapped);

      // 3. Auto-start daily reading
      setIsReading(true);

      const stream = streamReading(data, 'daily', targetDate);
      let text = '';
      let chars = 0;

      for await (const chunk of stream) {
        text += chunk;
        chars += chunk.length;
        setReading(text);
        setReadingChars(chars);

        // Free tier: show ~30% content then trigger paywall
        if (chars > 800 && !showPaywall) {
          setShowPaywall(true);
          break;
        }
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsCalculating(false);
      setIsReading(false);
    }
  }, [targetDate, showPaywall]);

  const handleContinueReading = useCallback(async () => {
    if (!birthData) return;
    setShowPaywall(false);
    setIsReading(true);

    try {
      const stream = streamReading(birthData, 'daily', targetDate);
      let text = reading;

      for await (const chunk of stream) {
        text += chunk;
        setReading(text);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsReading(false);
    }
  }, [birthData, targetDate, reading]);

  // Handle switching the target date (recalculate fortune + reading)
  const handleDateChange = useCallback(async (newDate: string) => {
    setTargetDate(newDate);
    if (!birthData) return;

    setIsCalculating(true);
    setError(null);
    setReading('');
    setDailyFortuneData(null);

    try {
      // Recalculate daily fortune
      const fortuneApiData = await calculateDailyFortune(birthData, newDate);
      const fortuneMapped = mapDailyFortune(fortuneApiData);
      setDailyFortuneData(fortuneMapped);

      // Start new reading
      setIsReading(true);

      const stream = streamReading(birthData, 'daily', newDate);
      let text = '';

      for await (const chunk of stream) {
        text += chunk;
        setReading(text);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsCalculating(false);
      setIsReading(false);
    }
  }, [birthData]);

  const todayStr = getTodayISO();

  return (
    <main className="min-h-screen bg-ricePaper dark:bg-darkInk transition-colors duration-500">
      {/* Hero Section — Purple / Mystic Theme */}
      <section className="relative overflow-hidden bg-gradient-to-b from-purple-950 via-indigo-950 to-ink/95 dark:from-purple-950 dark:via-indigo-950/80 dark:to-darkInk text-ricePaper py-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 border border-purple-400/40 rounded-full" />
          <div className="absolute bottom-10 right-10 w-96 h-96 border border-indigo-400/20 rounded-full" />
          {/* Moon / stars decorative SVG */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] opacity-15">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              {/* Crescent moon */}
              <path
                d="M130 20 A70 70 0 1 1 60 180 A90 90 0 1 0 130 20Z"
                fill="currentColor"
                stroke="none"
                className="text-purple-300"
              />
              {/* Small stars */}
              <circle cx="30" cy="50" r="2" className="text-purple-300" fill="currentColor" />
              <circle cx="170" cy="40" r="1.5" className="text-purple-300" fill="currentColor" />
              <circle cx="50" cy="150" r="1" className="text-purple-300" fill="currentColor" />
              <circle cx="160" cy="160" r="2" className="text-purple-300" fill="currentColor" />
            </svg>
          </div>
          {/* Floating star decorations */}
          <div className="absolute top-20 left-1/4 text-purple-400/30 text-4xl">✨</div>
          <div className="absolute bottom-20 right-1/4 text-indigo-400/20 text-3xl">🌟</div>
          <div className="absolute top-1/3 right-1/3 text-purple-300/20 text-2xl">🔮</div>
        </div>

        <div className="relative max-w-4xl mx-auto text-center px-4">
          <h1 className="font-serif text-5xl md:text-7xl font-bold mb-6 tracking-wider">
            <span className="text-purple-300">Daily</span>
            <span className="text-purple-100"> </span>
            <span className="text-purple-300">Fortune</span>
          </h1>
          <p className="text-xl md:text-2xl text-purple-200/60 mb-4 font-light">
            每日运势
          </p>
          <p className="text-purple-200/40 max-w-xl mx-auto text-sm leading-relaxed">
            Navigate each day with cosmic wisdom. Your daily BaZi forecast reveals
            auspicious activities, cautionary guidance, and the subtle energies
            shaping your day.
          </p>
          <div className="mt-8 flex justify-center gap-4 text-xs text-purple-200/30">
            <span>🔮 流日干支</span>
            <span>·</span>
            <span>📅 黄历宜忌</span>
            <span>·</span>
            <span>⭐ 每日吉凶</span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-5 gap-8">
          {/* Left Column: Input + Chart + Date Picker */}
          <div className="lg:col-span-2">
            <div className="sticky top-8 space-y-6">
              {/* Date Picker — shown at top */}
              <div className="chinese-card p-4">
                <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-2">
                  📅 Select Date
                </label>
                <div className="flex gap-2">
                  <input
                    type="date"
                    value={targetDate}
                    onChange={(e) => handleDateChange(e.target.value)}
                    max={todayStr}
                    className="flex-1 rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                               text-sm text-ink dark:text-ricePaper font-serif
                               focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all"
                  />
                  {targetDate !== todayStr && (
                    <button
                      onClick={() => handleDateChange(todayStr)}
                      className="px-3 py-2 rounded-lg border border-purple-400/30 bg-purple-400/10
                                 text-purple-400 text-xs font-medium hover:bg-purple-400/20 transition-all"
                    >
                      Today
                    </button>
                  )}
                </div>
                {targetDate === todayStr && (
                  <p className="text-[10px] text-purple-400/50 mt-1.5">
                    Showing today&apos;s fortune (auto-filled)
                  </p>
                )}
              </div>

              <BirthForm onSubmit={handleBirthSubmit} isLoading={isCalculating} />

              {chart && (
                <div className="chinese-card p-4">
                  <ChartDisplay chart={chart} />
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Daily Fortune Card + Reading */}
          <div className="lg:col-span-3">
            {error && (
              <div className="bg-vermillion/10 border border-vermillion/30 rounded-lg p-4 mb-6 text-vermillion text-sm">
                ⚠️ {error}
              </div>
            )}

            {/* Daily Fortune Card */}
            {dailyFortuneData && (
              <div className="mb-6">
                <DailyFortune data={dailyFortuneData} />
              </div>
            )}

            {isReading && !reading && (
              <div className="flex items-center justify-center py-20">
                <div className="animate-bagua-spin w-12 h-12 rounded-full border-2 border-purple-400 border-t-transparent" />
                <span className="ml-4 text-ink/50 dark:text-ricePaper/50">
                  Consulting the ancient wisdom for this day...
                </span>
              </div>
            )}

            {reading && (
              <div className="chinese-card">
                <ReadingStream content={reading} isStreaming={isReading} />
              </div>
            )}

            {!chart && !isCalculating && !error && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="text-6xl mb-6">🔮</div>
                <h2 className="font-serif text-2xl text-ink/60 dark:text-ricePaper/60 mb-3">
                  Your Daily Cosmic Guide
                </h2>
                <p className="text-ink/40 dark:text-ricePaper/40 max-w-md leading-relaxed">
                  Enter your birth details on the left to reveal today&apos;s fortune.
                  Discover what the day holds — auspicious activities, things to avoid,
                  and personalized guidance from your BaZi chart.
                </p>
                <div className="mt-8 grid grid-cols-3 gap-6 text-center">
                  {[
                    { icon: '📅', label: 'Daily Stem', desc: 'Flow day analysis' },
                    { icon: '✅', label: 'Auspicious', desc: 'What to embrace' },
                    { icon: '⚠️', label: 'Cautions', desc: 'What to avoid' },
                  ].map((item) => (
                    <div key={item.label} className="space-y-2">
                      <div className="text-3xl">{item.icon}</div>
                      <div className="text-xs text-ink/40 dark:text-ricePaper/40">{item.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Paywall Modal */}
      {showPaywall && (
        <Paywall
          isOpen={showPaywall}
          onUnlock={handleContinueReading}
          onClose={() => setShowPaywall(false)}
        />
      )}
    </main>
  );
}
