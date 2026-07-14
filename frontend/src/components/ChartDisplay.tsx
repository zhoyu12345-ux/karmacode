'use client';

import { ChartData as ApiChartData } from '@/lib/api';

interface ChartDisplayProps {
  chart: ApiChartData;
}

const ELEMENT_COLORS: Record<string, string> = {
  Wood: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-300',
  Fire: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-300',
  Earth: 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900/30 dark:text-amber-300',
  Metal: 'bg-gray-200 text-gray-800 border-gray-300 dark:bg-gray-700/30 dark:text-gray-300',
  Water: 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-300',
};

export default function ChartDisplay({ chart }: ChartDisplayProps) {
  const pillars = chart.pillars;
  const pillarOrder = ['year', 'month', 'day', 'hour'] as const;
  const pillarLabels = { year: 'Year', month: 'Month', day: 'Day', hour: 'Hour' };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-serif text-lg text-ink dark:text-ricePaper">
          🀄 Your BaZi Chart
        </h3>
        <span className="text-xs text-ink/40 dark:text-ricePaper/40 font-medium">
          {chart.birth_info.animal} · {chart.day_master.char} Master
        </span>
      </div>

      {/* Four Pillars Grid */}
      <div className="grid grid-cols-4 gap-3">
        {pillarOrder.map((key) => {
          const pillar = pillars[key];
          const isDay = key === 'day';
          return (
            <div
              key={key}
              className={`text-center p-3 rounded-lg border-2 transition-all duration-300
                ${isDay
                  ? 'border-gold bg-gold/10 shadow-lg shadow-gold/10 scale-105'
                  : 'border-ink/10 dark:border-ricePaper/10 bg-white/50 dark:bg-white/5'
                }`}
            >
              <div className="text-[10px] uppercase tracking-wider text-ink/40 dark:text-ricePaper/40 mb-1">
                {pillarLabels[key]}
                {isDay && ' ★'}
              </div>
              <div className="font-serif text-xl font-bold text-ink dark:text-ricePaper">
                {pillar.stem.char}
              </div>
              <div className="font-serif text-sm text-ink/60 dark:text-ricePaper/60">
                {pillar.branch.char}
              </div>
              <div className={`mt-1.5 text-[10px] px-1.5 py-0.5 rounded-full inline-block
                ${ELEMENT_COLORS[pillar.stem.element_en] || 'bg-gray-100 text-gray-600'}`}>
                {pillar.stem.element_en}
              </div>
              {pillar.nayin && (
                <div className="text-[9px] text-ink/30 dark:text-ricePaper/30 mt-1">
                  {pillar.nayin}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Day Master Info */}
      <div className="p-3 rounded-lg bg-gold/5 border border-gold/20 flex items-center gap-3">
        <div className="text-2xl font-serif font-bold text-gold">
          {chart.day_master.char}
        </div>
        <div>
          <div className="text-sm font-medium text-ink dark:text-ricePaper">
            Day Master: {chart.day_master.element_en} {chart.day_master.yinyang}
          </div>
          <div className="text-xs text-ink/40 dark:text-ricePaper/40">
            Your core self — {chart.day_master.en} ({chart.day_master.char})
          </div>
        </div>
      </div>

      {/* Five Elements Bar */}
      <div className="space-y-1.5">
        <div className="text-xs text-ink/40 dark:text-ricePaper/40 font-medium">
          Five Element Balance
        </div>
        <div className="flex h-3 rounded-full overflow-hidden bg-ink/5 dark:bg-ricePaper/5">
          {Object.entries(chart.wuxing_count.counts_en).map(([element, count]) => {
            const total = 8;
            const width = (count / total) * 100;
            const colorMap: Record<string, string> = {
              Wood: 'bg-green-500',
              Fire: 'bg-red-500',
              Earth: 'bg-amber-500',
              Metal: 'bg-gray-400',
              Water: 'bg-blue-500',
            };
            return (
              <div
                key={element}
                className={`${colorMap[element]} transition-all`}
                style={{ width: `${width}%` }}
                title={`${element}: ${count}/${total}`}
              />
            );
          })}
        </div>
        <div className="flex justify-between text-[10px] text-ink/30 dark:text-ricePaper/30">
          {Object.entries(chart.wuxing_count.counts_en).map(([e, c]) => (
            <span key={e}>{e} {c}</span>
          ))}
        </div>
      </div>

      {/* Major Luck Timeline */}
      <div className="space-y-1.5">
        <div className="text-xs text-ink/40 dark:text-ricePaper/40 font-medium">
          Major Luck Cycles (大运) · Starts at age {chart.dayun.start_age}
        </div>
        <div className="flex overflow-x-auto gap-2 pb-2">
          {chart.dayun.cycles.slice(0, 5).map((cycle) => (
            <div
              key={cycle.order}
              className="flex-shrink-0 text-center p-2 rounded-lg bg-white/50 dark:bg-white/5 border border-ink/5 dark:border-ricePaper/5 min-w-[80px]"
            >
              <div className="text-[10px] text-ink/30 dark:text-ricePaper/30">
                {cycle.age}
              </div>
              <div className="font-serif text-sm text-ink dark:text-ricePaper mt-0.5">
                {cycle.stem}{cycle.branch}
              </div>
              <div className="text-[10px] text-ink/40 dark:text-ricePaper/40">
                {cycle.element_en}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Stars */}
      <div className="flex flex-wrap gap-1.5">
        {chart.shensha['桃花_Peach_Blossom']?.present_in?.length > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300">
            🌸 Peach Blossom
          </span>
        )}
        {chart.shensha['天乙贵人_TianYi_Nobleman']?.present_in?.length > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
            ⭐ Nobleman
          </span>
        )}
        {chart.shensha['羊刃_YangBlade']?.present_in?.length > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
            ⚔️ Yang Blade
          </span>
        )}
        {chart.shensha['红鸾_RedLuan_Marriage']?.present_in?.length > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300">
            💍 Red Luan
          </span>
        )}
      </div>
    </div>
  );
}
