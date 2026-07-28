'use client';

import { useState, useEffect, useCallback } from 'react';
import BirthModal, { BirthData } from '@/components/BirthModal';
import DailySign from '@/components/DailySign';
import DestinyChart from '@/components/DestinyChart';
import { calculateBazi, ChartData } from '@/lib/api';

const SIDEBAR_ITEMS = [
  { id: 'daily',  icon: '🔮', label: 'Daily Sign',    desc: 'Today\'s cosmic energy' },
  { id: 'chart',  icon: '📅', label: 'Life Chart',    desc: 'Your BaZi blueprint' },
  { id: 'love',   icon: '💑', label: 'Love & Match',  desc: 'Relationship insights' },
  { id: 'wealth', icon: '💰', label: 'Wealth Path',   desc: 'Career & prosperity' },
];

export default function Home() {
  const [showBirthModal, setShowBirthModal] = useState(false);
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [activeTab, setActiveTab] = useState('daily');
  const [loveReading, setLoveReading] = useState('');
  const [wealthReading, setWealthReading] = useState('');
  const [isLoveLoading, setIsLoveLoading] = useState(false);
  const [isWealthLoading, setIsWealthLoading] = useState(false);

  // 首次加载：检查 localStorage
  useEffect(() => {
    const saved = localStorage.getItem('karmacode_birth');
    if (saved) {
      const data = JSON.parse(saved);
      setBirthData(data);
      loadChart(data);
    } else {
      setShowBirthModal(true);
    }
  }, []);

  // 计算命盘
  const loadChart = async (data: BirthData) => {
    setIsCalculating(true);
    try {
      const c = await calculateBazi(data);
      setChart(c);
    } catch(e) { console.error(e); }
    setIsCalculating(false);
  };

  // 出生信息提交
  const handleBirthSubmit = useCallback((data: BirthData) => {
    localStorage.setItem('karmacode_birth', JSON.stringify(data));
    setBirthData(data);
    setShowBirthModal(false);
    loadChart(data);
  }, []);

  // 加载恋爱解读
  const loadLoveReading = useCallback(async () => {
    if (!birthData || loveReading) return;
    setIsLoveLoading(true);
    try {
      const { streamReading } = await import('@/lib/api');
      const stream = streamReading(birthData, 'love');
      let text = '';
      for await (const chunk of stream) { text += chunk; }
      setLoveReading(text);
    } catch(e) {}
    setIsLoveLoading(false);
  }, [birthData, loveReading]);

  // 加载财富解读
  const loadWealthReading = useCallback(async () => {
    if (!birthData || wealthReading) return;
    setIsWealthLoading(true);
    try {
      const { streamReading } = await import('@/lib/api');
      const stream = streamReading(birthData, 'wealth');
      let text = '';
      for await (const chunk of stream) { text += chunk; }
      setWealthReading(text);
    } catch(e) {}
    setIsWealthLoading(false);
  }, [birthData, wealthReading]);

  // 当切换到 love/wealth 时自动加载
  useEffect(() => {
    if (activeTab === 'love') loadLoveReading();
    if (activeTab === 'wealth') loadWealthReading();
  }, [activeTab, loadLoveReading, loadWealthReading]);

  return (
    <div className="flex min-h-screen bg-ricePaper dark:bg-darkInk">
      {/* Birth Modal */}
      <BirthModal onSubmit={handleBirthSubmit} isOpen={showBirthModal} />

      {/* Left Sidebar */}
      <aside className="w-56 flex-shrink-0 border-r border-gold/20 bg-white/30 dark:bg-darkInk/50 flex flex-col">
        {/* Logo */}
        <div className="p-5 border-b border-gold/20">
          <a href="/" className="flex items-center gap-2 font-serif text-xl font-bold text-ink dark:text-ricePaper">
            <span className="text-2xl">☯</span>
            KarmaCode
          </a>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 p-3 space-y-1">
          {SIDEBAR_ITEMS.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-300 group
                ${activeTab === item.id
                  ? 'bg-gold/15 border border-gold/30 shadow-sm'
                  : 'border border-transparent hover:bg-gold/5 hover:border-gold/10'
                }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-lg">{item.icon}</span>
                <div>
                  <div className={`font-serif text-sm font-medium ${activeTab===item.id?'text-gold':'text-ink dark:text-ricePaper'}`}>
                    {item.label}
                  </div>
                  <div className="text-[10px] text-ink/30 dark:text-ricePaper/30">{item.desc}</div>
                </div>
              </div>
            </button>
          ))}
        </nav>

        {/* Bottom: Birth info + Change */}
        <div className="p-4 border-t border-gold/20 space-y-2">
          {birthData && (
            <div className="text-[10px] text-ink/40 text-center">
              <div>{birthData.birthDate}</div>
              <div>{birthData.gender==='female'?'♀':'♂'} · {birthData.locationName}</div>
            </div>
          )}
          <button
            onClick={() => setShowBirthModal(true)}
            className="w-full py-2 text-xs text-ink/40 hover:text-gold border border-gold/20 rounded-lg transition-colors font-serif"
          >
            {birthData ? '✏️ Edit Birth Info' : '🔮 Enter Birth Info'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-3xl mx-auto">

          {/* Tab: Daily Sign */}
          {activeTab === 'daily' && (
            <div className="scroll-unfold">
              <h1 className="font-serif text-2xl text-ink dark:text-ricePaper mb-2">🔮 Daily Sign</h1>
              <p className="text-sm text-ink/40 mb-6">Tap the compass to reveal today&apos;s cosmic message</p>
              <DailySign birthData={birthData} />
            </div>
          )}

          {/* Tab: Life Chart */}
          {activeTab === 'chart' && (
            <div className="scroll-unfold">
              <h1 className="font-serif text-2xl text-ink dark:text-ricePaper mb-2">📅 Life Chart</h1>
              <p className="text-sm text-ink/40 mb-6">Your BaZi cosmic blueprint</p>
              <DestinyChart chart={chart} isLoading={isCalculating} />
            </div>
          )}

          {/* Tab: Love */}
          {activeTab === 'love' && (
            <div className="scroll-unfold">
              <h1 className="font-serif text-2xl text-ink dark:text-ricePaper mb-2">💑 Love & Match</h1>
              <p className="text-sm text-ink/40 mb-6">Relationship insights based on your elements</p>
              {!birthData ? (
                <div className="chinese-card p-8 text-center text-ink/40">Enter your birth info to see your love reading</div>
              ) : isLoveLoading ? (
                <div className="flex justify-center py-12"><div className="bagua-loading"/></div>
              ) : (
                <div className="chinese-card p-6">
                  <div className="font-serif text-sm leading-relaxed text-ink/70 dark:text-ricePaper/70 whitespace-pre-wrap">
                    {loveReading || 'Loading...'}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab: Wealth */}
          {activeTab === 'wealth' && (
            <div className="scroll-unfold">
              <h1 className="font-serif text-2xl text-ink dark:text-ricePaper mb-2">💰 Wealth Path</h1>
              <p className="text-sm text-ink/40 mb-6">Career & prosperity analysis</p>
              {!birthData ? (
                <div className="chinese-card p-8 text-center text-ink/40">Enter your birth info to see your wealth reading</div>
              ) : isWealthLoading ? (
                <div className="flex justify-center py-12"><div className="bagua-loading"/></div>
              ) : (
                <div className="chinese-card p-6">
                  <div className="font-serif text-sm leading-relaxed text-ink/70 dark:text-ricePaper/70 whitespace-pre-wrap">
                    {wealthReading || 'Loading...'}
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
