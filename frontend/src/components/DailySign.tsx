'use client';

import { useState } from 'react';
import { calculateBazi, calculateDailyFortune, streamReading, ChartData, DailyFortuneData } from '@/lib/api';
import { BirthData } from '@/components/BirthModal';

interface DailySignProps {
  birthData: BirthData | null;
}

export default function DailySign({ birthData }: DailySignProps) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [sign, setSign] = useState<string>('');
  const [dailyData, setDailyData] = useState<DailyFortuneData | null>(null);
  const [shown, setShown] = useState(false);

  const handleReveal = async () => {
    if (!birthData || isSpinning) return;
    setIsSpinning(true);
    setSign('');

    try {
      const chart = await calculateBazi(birthData);
      const today = new Date().toISOString().split('T')[0];
      const daily = await calculateDailyFortune(birthData, today);
      setDailyData(daily);

      // 生成日签文案
      const stream = streamReading(birthData, 'daily', today);
      let text = '';
      for await (const chunk of stream) { text += chunk; }
      setSign(text);
    } catch(e) {
      setSign('Today, the stars whisper: trust your inner compass. The universe aligns in small, quiet ways — pay attention to the subtle signs. ✨');
    }

    setTimeout(() => {
      setIsSpinning(false);
      setShown(true);
    }, 2500);
  };

  return (
    <div className="space-y-6">
      {/* 罗盘区域 */}
      <div className="text-center">
        <div
          onClick={handleReveal}
          className={`relative w-48 h-48 mx-auto cursor-pointer select-none transition-transform duration-300 hover:scale-105 ${isSpinning ? 'pointer-events-none' : ''}`}
        >
          {/* Outer ring */}
          <div className={`absolute inset-0 rounded-full border-2 border-gold ${isSpinning ? 'animate-spin' : ''}`}
            style={{animationDuration: isSpinning ? '2s' : '0s'}}>
            {/* Compass markers */}
            {['N','E','S','W'].map((d,i) => (
              <span key={d} className="absolute text-xs text-gold font-bold"
                style={{top:i===0?'8px':i===2?'auto':'50%',bottom:i===2?'8px':'auto',left:i===3?'8px':i===1?'auto':'50%',right:i===1?'8px':'auto',transform:'translate(-50%,-50%)'}}>
                {d}
              </span>
            ))}
          </div>
          {/* Middle ring */}
          <div className={`absolute inset-4 rounded-full border border-gold/30 ${isSpinning ? 'animate-spin' : ''}`}
            style={{animationDuration: isSpinning ? '1.5s' : '0s',animationDirection:'reverse'}}/>
          {/* Inner Bagua */}
          <div className="absolute inset-8 rounded-full bg-ink/5 dark:bg-ricePaper/5 flex items-center justify-center">
            <div className={`text-3xl ${isSpinning ? 'animate-pulse' : ''}`}>☯</div>
          </div>
          {/* Center */}
          <div className="absolute inset-12 rounded-full bg-gold/10 flex items-center justify-center">
            <span className="text-xs text-gold font-serif">{isSpinning ? '...' : 'TAP'}</span>
          </div>
        </div>
        <p className="text-xs text-ink/30 dark:text-ricePaper/30 mt-3 font-serif">
          {isSpinning ? 'The compass turns...' : shown ? 'Your sign has been revealed' : 'Tap the compass to reveal today\'s sign'}
        </p>
      </div>

      {/* 日签结果卡片 */}
      {shown && sign && (
        <div className="chinese-card p-6 scroll-unfold">
          <div className="text-center mb-4">
            <div className="text-gold text-sm font-medium mb-1">
              {new Date().toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'})}
            </div>
            {dailyData && (
              <div className="inline-block px-3 py-1 rounded-full text-xs border border-gold/30 text-gold">
                {dailyData.energy_level === 'high' ? '⚡ Intense Day' : dailyData.energy_level === 'low' ? '🌙 Quiet Day' : '☀️ Balanced Day'}
              </div>
            )}
          </div>
          <div className="font-serif text-sm leading-relaxed text-ink/70 dark:text-ricePaper/70 whitespace-pre-wrap">
            {sign}
          </div>
          {dailyData && (
            <div className="mt-4 pt-4 border-t border-ink/5 dark:border-ricePaper/5 grid grid-cols-2 gap-2 text-xs text-ink/40">
              <div>🎨 Lucky Color: <span className="text-ink dark:text-ricePaper">{['Crimson','Gold','Jade','Azure','Amber'][Math.floor(Math.random()*5)]}</span></div>
              <div>🔢 Lucky Number: <span className="text-ink dark:text-ricePaper">{Math.floor(Math.random()*9)+1}</span></div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
