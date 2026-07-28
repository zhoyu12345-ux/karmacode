'use client';

import { useState, useEffect } from 'react';
import { calculateBazi, calculateDailyFortune, streamReading, DailyFortuneData } from '@/lib/api';
import { BirthData } from '@/components/BirthModal';

interface DailySignProps {
  birthData: BirthData | null;
}

function getLunarDate(): string {
  const now = new Date();
  // 简化农历显示
  const lunarMonths = ['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','冬月','腊月'];
  const lunarDays = ['初一','初二','初三','初四','初五','初六','初七','初八','初九','初十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十'];
  const m = now.getMonth();
  const d = Math.min(now.getDate()-1, 29);
  return `${lunarMonths[m]}${lunarDays[d]}`;
}

function getDayStemBranch(): string {
  const now = new Date();
  const stems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
  const branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
  // 简化的日干支计算
  const base = new Date(2026,6,28);
  const diff = Math.floor((now.getTime()-base.getTime())/(1000*60*60*24));
  const stemIdx = ((diff%10)+10)%10;
  const branchIdx = ((diff%12)+12)%12;
  return stems[stemIdx]+branches[branchIdx];
}

export default function DailySign({ birthData }: DailySignProps) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [sign, setSign] = useState('');
  const [dailyData, setDailyData] = useState<DailyFortuneData | null>(null);
  const [shown, setShown] = useState(false);
  const [lunarDate, setLunarDate] = useState('');
  const [dayStemBranch, setDayStemBranch] = useState('');

  useEffect(() => {
    setLunarDate(getLunarDate());
    setDayStemBranch(getDayStemBranch());
  }, []);

  const handleReveal = async () => {
    if (!birthData || isSpinning) return;
    setIsSpinning(true);
    setSign('');

    try {
      const today = new Date().toISOString().split('T')[0];
      const daily = await calculateDailyFortune(birthData, today);
      setDailyData(daily);

      const stream = streamReading(birthData, 'daily', today);
      let text = '';
      for await (const chunk of stream) { text += chunk; }
      setSign(text);
    } catch(e) {
      setSign('今日宜静。关闭对外界的过度关注，把注意力回到呼吸上。在安静中，你会找到答案。');
    }

    setTimeout(() => {
      setIsSpinning(false);
      setShown(true);
    }, 2800);
  };

  return (
    <div className="space-y-8">
      {/* 罗盘 */}
      <div className="text-center">
        <div onClick={handleReveal}
          className={`relative w-40 h-40 mx-auto cursor-pointer select-none transition-transform hover:scale-105 ${isSpinning?'pointer-events-none':''}`}>
          <div className={`absolute inset-0 rounded-full border border-gold/50 ${isSpinning?'animate-spin'}`}
            style={{animationDuration:'2.5s'}}/>
          <div className={`absolute inset-2 rounded-full border border-gold/30 ${isSpinning?'animate-spin'}`}
            style={{animationDuration:'1.8s',animationDirection:'reverse'}}/>
          <div className="absolute inset-4 rounded-full border border-gold/10"/>
          <div className="absolute inset-6 rounded-full bg-ink/[0.02] dark:bg-ricePaper/[0.02] flex items-center justify-center">
            <div className={`text-2xl ${isSpinning?'animate-pulse':''}`}>☯</div>
          </div>
          <div className="absolute inset-12 rounded-full flex items-center justify-center">
            <span className="text-[10px] text-gold/60 font-serif tracking-widest">{isSpinning?'...':'轻触'}</span>
          </div>
        </div>
        <p className="text-xs text-ink/20 mt-4 font-serif">
          每日运势分析，是东方智慧的凝练，更是你掌握当下、规划未来的参照。<br/>
          它解读每日运势的潜在脉络，揭示机遇与挑战的走向。<br/>
          每日查看运势分析，觉察自我状态，做出更明智的决策。
        </p>
      </div>

      {/* 日签结果 */}
      {shown && sign && (
        <div className="max-w-lg mx-auto scroll-unfold">
          <div className="text-center mb-6">
            <p className="text-ink/30 text-xs font-serif">
              {new Date().toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric',weekday:'long'})}
              &nbsp;·&nbsp;农历{lunarDate}&nbsp;·&nbsp;{dayStemBranch}日
            </p>
          </div>

          <h2 className="text-center font-serif text-base text-ink/60 mb-6 tracking-widest">
            今日卦象
          </h2>

          <div className="font-serif text-sm leading-loose text-ink/70 whitespace-pre-wrap tracking-wide">
            {sign}
          </div>

          {dailyData && dailyData.is_tiankedichong && (
            <div className="mt-6 p-3 bg-vermillion/5 border border-vermillion/10 rounded text-xs text-vermillion/70 font-serif text-center">
              今日天克地冲，不宜做重大决策。多休息，少折腾。
            </div>
          )}
        </div>
      )}
    </div>
  );
}
