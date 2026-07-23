'use client';

import { useState, useCallback } from 'react';
import BirthForm, { BirthData } from '@/components/BirthForm';
import ChartDisplay from '@/components/ChartDisplay';
import ReadingStream from '@/components/ReadingStream';
import Paywall from '@/components/Paywall';
import { calculateBazi, streamReading, ChartData } from '@/lib/api';
import { createCheckoutSession } from '@/lib/stripe';

type ReadingType = 'love' | 'wealth' | 'daily' | 'general';

export default function Home() {
  const [chart, setChart] = useState<ChartData | null>(null);
  const [reading, setReading] = useState<string>('');
  const [isCalculating, setIsCalculating] = useState(false);
  const [isReading, setIsReading] = useState(false);
  const [readingType, setReadingType] = useState<ReadingType>('general');
  const [showPaywall, setShowPaywall] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [birthData, setBirthData] = useState<BirthData | null>(null);
  const [readingChars, setReadingChars] = useState(0);
  const isDemoMode = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('demo') === 'true';

  const handleBirthSubmit = useCallback(async (data: BirthData) => {
    setIsCalculating(true);
    setError(null);
    setReading('');
    setBirthData(data);

    try {
      const chartData = await calculateBazi(data);
      setChart(chartData);

      // Auto-start reading
      setIsReading(true);
      setReadingType('general');

      const stream = streamReading(data, 'general');
      let text = '';
      let chars = 0;

      for await (const chunk of stream) {
        text += chunk;
        chars += chunk.length;
        setReading(text);
        setReadingChars(chars);

        // Paywall disabled for now
        if (false && !isDemoMode && chars > 800 && !showPaywall) {
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
  }, [showPaywall]);

  const handleContinueReading = useCallback(async () => {
    if (!birthData) return;

    // 生成临时用户ID (后续接 Supabase 后可替换为真实用户ID)
    const userId = 'user_' + Math.random().toString(36).substring(2, 10);

    try {
      // 跳转到 Stripe 支付页面
      await createCheckoutSession(userId);
      // 支付成功后 Stripe 会重定向回 success_url
      // 但因为我们还没设置 success_url，先继续阅读
      // TODO: 等支付成功后从 URL 参数恢复阅读状态
      setShowPaywall(false);
      setIsReading(true);

      const stream = streamReading(birthData, readingType);
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
  }, [birthData, readingType, reading]);

  const handleReadingTypeChange = useCallback(async (type: ReadingType) => {
    if (!birthData) return;
    setReadingType(type);
    setReading('');
    setIsReading(true);
    setError(null);

    try {
      const stream = streamReading(birthData, type);
      let text = '';
      for await (const chunk of stream) {
        text += chunk;
        setReading(text);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsReading(false);
    }
  }, [birthData]);

  const tabs: { id: ReadingType; label: string; icon: string }[] = [
    { id: 'general', label: 'Overview', icon: '🌏' },
    { id: 'love', label: 'Love', icon: '💑' },
    { id: 'wealth', label: 'Wealth', icon: '💰' },
    { id: 'daily', label: 'Daily', icon: '🔮' },
  ];

  return (
    <main className="min-h-screen bg-ricePaper dark:bg-darkInk transition-colors duration-500">
      {/* Demo Mode Banner */}
      {isDemoMode && (
        <div className="bg-gold text-ink text-center py-2 text-sm font-medium">
          🎬 Demo Mode — Full content unlocked for recording
        </div>
      )}

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-ink to-ink/90 dark:from-darkInk dark:to-darkInk/95 text-ricePaper py-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 border border-gold/30 rounded-full" />
          <div className="absolute bottom-10 right-10 w-96 h-96 border border-jade/20 rounded-full" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px]">
            <svg viewBox="0 0 200 200" className="w-full h-full opacity-20">
              <circle cx="100" cy="100" r="95" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-gold" />
              <circle cx="100" cy="100" r="47" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-gold" />
              <path d="M100 5 A95 95 0 0 1 100 195 A47 47 0 0 0 100 5" fill="currentColor" className="text-ink dark:text-darkInk" />
            </svg>
          </div>
        </div>

        <div className="relative max-w-4xl mx-auto text-center px-4">
          <h1 className="font-serif text-5xl md:text-7xl font-bold mb-6 tracking-wider">
            <span className="text-gold">Karma</span>
            <span className="text-ricePaper">Code</span>
          </h1>
          <p className="text-xl md:text-2xl text-ricePaper/70 mb-4 font-light">
            Discover Your Cosmic Blueprint
          </p>
          <p className="text-ricePaper/50 max-w-xl mx-auto text-sm leading-relaxed">
            Ancient Chinese metaphysics meets modern AI. Understand your BaZi (八字) —
            your cosmic DNA encoded at birth. Explore love, wealth, and daily guidance
            through the lens of Eastern wisdom.
          </p>
          <div className="mt-8 flex justify-center gap-4 text-xs text-ricePaper/40">
            <span>🀄 三命通会</span>
            <span>·</span>
            <span>☯️ 五行八卦</span>
            <span>·</span>
            <span>🔮 AI-Powered</span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-5 gap-8">
          {/* Left Column: Input + Chart */}
          <div className="lg:col-span-2">
            <div className="sticky top-8 space-y-6">
              <BirthForm onSubmit={handleBirthSubmit} isLoading={isCalculating} />

              {chart && (
                <div className="chinese-card p-4">
                  <ChartDisplay chart={chart} />
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Reading */}
          <div className="lg:col-span-3">
            {error && (
              <div className="bg-vermillion/10 border border-vermillion/30 rounded-lg p-4 mb-6 text-vermillion text-sm">
                ⚠️ {error}
              </div>
            )}

            {chart && (
              <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleReadingTypeChange(tab.id)}
                    disabled={isReading}
                    className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-all duration-300
                      ${readingType === tab.id
                        ? 'bg-gold text-ink font-medium shadow-lg shadow-gold/20'
                        : 'bg-white/50 dark:bg-white/5 text-ink/60 dark:text-ricePaper/60 hover:bg-white dark:hover:bg-white/10'
                      }`}
                  >
                    {tab.icon} {tab.label}
                  </button>
                ))}
              </div>
            )}

            {isReading && !reading && (
              <div className="flex items-center justify-center py-20">
                <div className="animate-bagua-spin w-12 h-12 rounded-full border-2 border-gold border-t-transparent" />
                <span className="ml-4 text-ink/50 dark:text-ricePaper/50">
                  Consulting the ancient wisdom...
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
                <div className="text-6xl mb-6">🀄</div>
                <h2 className="font-serif text-2xl text-ink/60 dark:text-ricePaper/60 mb-3">
                  Your Journey Begins Here
                </h2>
                <p className="text-ink/40 dark:text-ricePaper/40 max-w-md leading-relaxed">
                  Enter your birth details on the left to reveal your cosmic blueprint.
                  The ancient wisdom of BaZi awaits — your story, written in the stars
                  and decoded by modern intelligence.
                </p>
                <div className="mt-8 grid grid-cols-3 gap-6 text-center">
                  {[
                    { icon: '💑', label: 'Love & Marriage', desc: 'Find your cosmic match' },
                    { icon: '💰', label: 'Wealth Path', desc: 'Your prosperity blueprint' },
                    { icon: '🔮', label: 'Daily Wisdom', desc: 'Navigate each day' },
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

      {/* Footer */}
      <footer className="border-t border-ink/5 dark:border-ricePaper/5 py-8 mt-20">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-xs text-ink/30 dark:text-ricePaper/30 leading-relaxed">
            🔮 KarmaCode provides AI-powered BaZi readings for entertainment and self-reflection.
            <br />
            It does not constitute professional advice (medical, legal, financial, or psychological).
            <br />
            Your life choices remain entirely in your own hands. The stars may suggest — you decide.
          </p>
          <p className="text-xs text-ink/20 dark:text-ricePaper/20 mt-2">
            © 2026 KarmaCode · Powered by Claude AI · Based on 三命通会 (San Ming Tong Hui)
          </p>
        </div>
      </footer>
    </main>
  );
}
