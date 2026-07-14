'use client';

import { useMemo } from 'react';

// ===== Type Definitions =====

export interface DailyFortuneData {
  date: string; // ISO date string
  energyLevel: 'auspicious' | 'neutral' | 'caution' | 'danger';
  energyLabel: string;
  energyDescription: string;
  goodActivities: string[];
  badActivities: string[];
  specialWarning?: string;
  luckyColors?: string[];
  luckyDirection?: string;
}

interface DailyFortuneProps {
  data: DailyFortuneData;
  className?: string;
}

// ===== Constants =====

const ENERGY_CONFIG: Record<
  DailyFortuneData['energyLevel'],
  {
    label: string;
    bg: string;
    text: string;
    border: string;
    badgeBg: string;
    badgeText: string;
    emoji: string;
  }
> = {
  auspicious: {
    label: '大吉',
    bg: 'bg-gradient-to-br from-amber-950/40 to-amber-900/20',
    text: 'text-amber-100',
    border: 'border-amber-600/40',
    badgeBg: 'bg-amber-500/20',
    badgeText: 'text-amber-300',
    emoji: '☀️',
  },
  neutral: {
    label: '平顺',
    bg: 'bg-gradient-to-br from-stone-950/40 to-stone-900/20',
    text: 'text-stone-100',
    border: 'border-stone-600/40',
    badgeBg: 'bg-stone-500/20',
    badgeText: 'text-stone-300',
    emoji: '🌤️',
  },
  caution: {
    label: '注意',
    bg: 'bg-gradient-to-br from-orange-950/40 to-orange-900/20',
    text: 'text-orange-100',
    border: 'border-orange-600/40',
    badgeBg: 'bg-orange-500/20',
    badgeText: 'text-orange-300',
    emoji: '🌧️',
  },
  danger: {
    label: '避凶',
    bg: 'bg-gradient-to-br from-red-950/40 to-red-900/20',
    text: 'text-red-100',
    border: 'border-red-600/40',
    badgeBg: 'bg-red-500/20',
    badgeText: 'text-red-300',
    emoji: '⛈️',
  },
};

const DAY_OF_WEEK = ['日', '一', '二', '三', '四', '五', '六'];

function formatDate(isoStr: string): { dateStr: string; dayOfWeek: string; lunarHint: string } {
  const d = new Date(isoStr);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const dow = DAY_OF_WEEK[d.getDay()];
  return {
    dateStr: `${year}年${month}月${day}日`,
    dayOfWeek: `星期${dow}`,
    lunarHint: `农历${['正','二','三','四','五','六','七','八','九','十','冬','腊'][d.getMonth()]}月`,
  };
}

// ===== Sub-components =====

function ActivityList({
  items,
  type,
}: {
  items: string[];
  type: 'good' | 'bad';
}) {
  if (items.length === 0) return null;

  const icon = type === 'good' ? '✓' : '✗';
  const colorClass =
    type === 'good'
      ? 'text-emerald-400'
      : 'text-red-400';

  return (
    <ul className="space-y-1.5">
      {items.map((item, idx) => (
        <li key={idx} className="flex items-start gap-2 text-sm">
          <span className={`flex-shrink-0 mt-0.5 text-xs font-bold ${colorClass}`}>
            {icon}
          </span>
          <span className="text-stone-300">{item}</span>
        </li>
      ))}
    </ul>
  );
}

function WarningBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-xl bg-red-950/30 border border-red-800/40 p-3">
      <span className="flex-shrink-0 text-red-400 text-base mt-0.5">⚠</span>
      <div>
        <span className="text-xs font-semibold text-red-400 uppercase tracking-wider">特别提醒</span>
        <p className="text-sm text-red-200/80 mt-0.5">{message}</p>
      </div>
    </div>
  );
}

// ===== Main Component =====

export default function DailyFortune({ data, className = '' }: DailyFortuneProps) {
  const energy = ENERGY_CONFIG[data.energyLevel] || ENERGY_CONFIG.neutral;
  const formattedDate = useMemo(() => formatDate(data.date), [data.date]);

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <div
        className={`
          relative overflow-hidden rounded-2xl border shadow-2xl
          ${energy.bg} ${energy.border} ${energy.text}
          shadow-amber-900/10
        `}
      >
        {/* Decorative top bar */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/60 to-transparent" />

        {/* Header: Date + Energy Badge */}
        <div className="px-5 pt-5 pb-3 flex items-center justify-between">
          <div>
            <p className="text-xs text-stone-500 tracking-wide uppercase">
              今日运势
            </p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-lg font-bold text-stone-100">
                {formattedDate.dateStr}
              </span>
              <span className="text-sm text-stone-400">{formattedDate.dayOfWeek}</span>
            </div>
            <p className="text-[10px] text-stone-600 mt-0.5">{formattedDate.lunarHint}</p>
          </div>

          {/* Energy Badge */}
          <div
            className={`
              flex flex-col items-center justify-center w-16 h-16 rounded-full
              ${energy.badgeBg} border ${energy.border}
              shadow-inner
            `}
          >
            <span className="text-xl">{energy.emoji}</span>
            <span className={`text-xs font-bold ${energy.badgeText}`}>
              {energy.label}
            </span>
          </div>
        </div>

        {/* Energy Description */}
        <div className="px-5 pb-3">
          <p className="text-sm text-stone-400 italic leading-relaxed">
            "{data.energyDescription}"
          </p>
        </div>

        {/* Divider */}
        <div className="px-5">
          <div className="h-px bg-gradient-to-r from-transparent via-stone-700/50 to-transparent" />
        </div>

        {/* Activities */}
        <div className="px-5 py-3 grid grid-cols-2 gap-4">
          {/* Good (宜) */}
          <div>
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <span className="w-1 h-3 rounded-full bg-emerald-500/60" />
              宜
            </h4>
            <ActivityList items={data.goodActivities} type="good" />
          </div>

          {/* Bad (忌) */}
          <div>
            <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <span className="w-1 h-3 rounded-full bg-red-500/60" />
              忌
            </h4>
            <ActivityList items={data.badActivities} type="bad" />
          </div>
        </div>

        {/* Special Warning */}
        {data.specialWarning && (
          <div className="px-5 pb-3">
            <WarningBanner message={data.specialWarning} />
          </div>
        )}

        {/* Lucky Extras */}
        {data.luckyColors || data.luckyDirection ? (
          <>
            <div className="px-5">
              <div className="h-px bg-gradient-to-r from-transparent via-stone-700/50 to-transparent" />
            </div>
            <div className="px-5 py-3 flex gap-4 text-xs text-stone-500">
              {data.luckyColors && (
                <div className="flex items-center gap-1.5">
                  <span>🎨 幸运色:</span>
                  <span className="text-stone-300">{data.luckyColors.join(' · ')}</span>
                </div>
              )}
              {data.luckyDirection && (
                <div className="flex items-center gap-1.5">
                  <span>🧭 吉方:</span>
                  <span className="text-stone-300">{data.luckyDirection}</span>
                </div>
              )}
            </div>
          </>
        ) : null}

        {/* Decorative bottom bar */}
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/40 to-transparent" />
      </div>
    </div>
  );
}
