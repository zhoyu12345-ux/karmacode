'use client';

import { useState } from 'react';
import { ChartData } from '@/lib/api';

interface DestinyChartProps {
  chart: ChartData | null;
  isLoading: boolean;
}

const STEM_BRANCH_NAMES: Record<string,string> = {
  '甲':'Jia Yang Wood','乙':'Yi Yin Wood','丙':'Bing Yang Fire','丁':'Ding Yin Fire',
  '戊':'Wu Yang Earth','己':'Ji Yin Earth','庚':'Geng Yang Metal','辛':'Xin Yin Metal',
  '壬':'Ren Yang Water','癸':'Gui Yin Water',
  '子':'Zi Rat','丑':'Chou Ox','寅':'Yin Tiger','卯':'Mao Rabbit',
  '辰':'Chen Dragon','巳':'Si Snake','午':'Wu Horse','未':'Wei Goat',
  '申':'Shen Monkey','酉':'You Rooster','戌':'Xu Dog','亥':'Hai Pig',
};

export default function DestinyChart({ chart, isLoading }: DestinyChartProps) {
  const [expandedPillar, setExpandedPillar] = useState<string | null>(null);
  const [showPremium, setShowPremium] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="bagua-loading bagua-loading-lg" />
      </div>
    );
  }

  if (!chart) return null;

  const pillars = chart.pillars;
  const dm = chart.day_master;

  // 农历日期拆分
  const lunarParts = chart.birth_info.lunar_date.split('年');
  const lunarYear = lunarParts[0] || '';
  const lunarRest = lunarParts[1]?.replace('月','月 ').replace('日','日') || '';

  const pillarOrder = ['year','month','day','hour'] as const;
  const pillarLabels:Record<string,string> = {year:'Year 年',month:'Month 月',day:'Day 日',hour:'Hour 时'};

  return (
    <div className="space-y-6">
      {/* 日历头部 */}
      <div className="chinese-card p-6">
        <div className="text-center mb-4">
          <h2 className="font-serif text-2xl text-ink dark:text-ricePaper mb-1">
            📅 Your Birth Calendar
          </h2>
        </div>

        {/* 公历 + 农历日期行 */}
        <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gold/5 rounded-lg">
          <div className="text-center">
            <div className="text-[10px] text-ink/40 uppercase mb-1">Solar Calendar</div>
            <div className="font-serif text-lg text-ink dark:text-ricePaper">{chart.birth_info.solar_date}</div>
            <div className="text-xs text-ink/40">{chart.birth_info.solar_time}</div>
          </div>
          <div className="text-center border-l border-gold/20">
            <div className="text-[10px] text-ink/40 uppercase mb-1">Lunar Calendar</div>
            <div className="font-serif text-lg text-ink dark:text-ricePaper">{chart.birth_info.lunar_date}</div>
            <div className="text-xs text-ink/40">Year of the {chart.birth_info.animal}</div>
          </div>
        </div>

        {/* 四柱 */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          {pillarOrder.map(key => {
            const p = pillars[key];
            const isDay = key === 'day';
            const isExpanded = expandedPillar === key;
            return (
              <div key={key}
                onClick={() => setExpandedPillar(isExpanded ? null : key)}
                className={`text-center p-3 rounded-lg border-2 cursor-pointer transition-all duration-300
                  ${isDay ? 'border-gold bg-gold/10 shadow-lg shadow-gold/5' : 'border-ink/10 dark:border-ricePaper/10 bg-white/50 dark:bg-white/5'}
                  hover:border-gold/50`}>
                <div className="text-[9px] uppercase text-ink/30 mb-1">{pillarLabels[key]}</div>
                <div className="font-serif text-xl font-bold text-ink dark:text-ricePaper">{p.stem.char}</div>
                <div className="font-serif text-base text-ink/60 dark:text-ricePaper/60">{p.branch.char}</div>
                <div className={`text-[10px] mt-1 ${isDay?'text-gold':'text-ink/40'}`}>
                  {isDay ? '⭐ SELF' : ''}
                </div>

                {/* 展开详情 */}
                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-ink/5 text-left text-[10px] space-y-1 scroll-unfold">
                    <div><span className="text-ink/30">天干:</span> {p.stem.char} ({STEM_BRANCH_NAMES[p.stem.char]||''})</div>
                    <div><span className="text-ink/30">地支:</span> {p.branch.char} ({STEM_BRANCH_NAMES[p.branch.char]||''})</div>
                    <div><span className="text-ink/30">藏干:</span> {p.hidden_stems?.join(' ')||'-'}</div>
                    <div><span className="text-ink/30">纳音:</span> {p.nayin}</div>
                    <div><span className="text-ink/30">十神:</span> {chart.shishen[`${key}_stem`]?.name||chart.shishen[`${key}_branch`]?.name||'-'}</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 日主 */}
        <div className="flex items-center justify-between p-3 bg-gold/5 rounded-lg">
          <div>
            <span className="text-xs text-ink/40">Day Master &nbsp;</span>
            <span className="font-serif font-bold text-gold">{dm.char} ({dm.element_en} {dm.yinyang})</span>
          </div>
          <div className="text-[10px] text-ink/30">{dm.en}</div>
        </div>

        {/* 五行条 */}
        <div className="mt-3">
          <div className="flex h-2 rounded-full overflow-hidden bg-ink/5">
            {Object.entries(chart.wuxing_count.counts_en).map(([e,c]) => {
              const colors:Record<string,string> = {Wood:'bg-green-500',Fire:'bg-red-500',Earth:'bg-amber-500',Metal:'bg-gray-400',Water:'bg-blue-500'};
              return <div key={e} className={colors[e]||'bg-gray-300'} style={{width:`${(c/8)*100}%`}} title={`${e}:${c}`}/>;
            })}
          </div>
          <div className="flex justify-between text-[9px] text-ink/30 mt-1">
            {Object.entries(chart.wuxing_count.counts_en).map(([e,c])=><span key={e}>{e} {c}</span>)}
          </div>
        </div>
      </div>

      {/* 付费区 */}
      <div className="chinese-card p-6">
        <div className="text-center mb-4">
          <h3 className="font-serif text-lg text-ink dark:text-ricePaper">📖 Deep Analysis</h3>
          <p className="text-xs text-ink/40 mt-1">Your complete life reading</p>
        </div>

        {/* 锁定卡片 */}
        <div className="space-y-3">
          {[
            {icon:'💰',title:'Wealth & Career',desc:'Your financial destiny and professional path revealed'},
            {icon:'💑',title:'Love & Marriage',desc:'Relationship patterns, ideal partner, and marriage timing'},
            {icon:'🏥',title:'Health & Wellness',desc:'Elemental balance guide for your physical and mental wellbeing'},
            {icon:'📅',title:'Life Chapters',desc:'10-year luck cycles and annual forecasts'},
          ].map(item => (
            <div key={item.title} className="relative p-4 rounded-lg border border-ink/10 dark:border-ricePaper/10 bg-white/30 dark:bg-white/5">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{item.icon}</span>
                <div className="flex-1">
                  <div className="font-serif text-sm text-ink dark:text-ricePaper">{item.title}</div>
                  <div className="text-xs text-ink/40 mt-0.5">{item.desc}</div>
                </div>
                {!showPremium && (
                  <span className="text-xl" title="Premium content">🔒</span>
                )}
              </div>
            </div>
          ))}

          <button
            onClick={() => setShowPremium(!showPremium)}
            className="w-full py-4 bg-gold text-ink font-bold rounded-lg hover:bg-gold/90 transition-all shadow-lg shadow-gold/10 mt-4"
          >
            {showPremium ? '🔒 Lock Premium Content' : '🔓 Unlock Full Report — $9.99'}
          </button>

          {showPremium && (
            <a
              href="https://8686962729146.gumroad.com/l/cocctb"
              className="block w-full py-3 bg-ink dark:bg-ricePaper text-ricePaper dark:text-ink text-center rounded-lg font-medium hover:opacity-90 transition-all mt-2"
            >
              Purchase on Gumroad →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
