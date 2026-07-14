'use client';

import { useState, useCallback } from 'react';
import BirthForm, { BirthData } from '@/components/BirthForm';
import ChartDisplay from '@/components/ChartDisplay';
import ReadingStream from '@/components/ReadingStream';
import Paywall from '@/components/Paywall';
import { calculateBazi, streamReading, ChartData } from '@/lib/api';

export default function WealthPage() {
  const [chart, setChart] = useState<ChartData | null>(null);
  const [reading, setReading] = useState<string>('');
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

    try {
      const chartData = await calculateBazi(data);
      setChart(chartData);

      // Auto-start wealth reading
      setIsReading(true);

      const stream = streamReading(data, 'wealth');
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
  }, [showPaywall]);

  const handleContinueReading = useCallback(async () => {
    if (!birthData) return;
    setShowPaywall(false);
    setIsReading(true);

    try {
      const stream = streamReading(birthData, 'wealth');
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
  }, [birthData, reading]);

  return (
    <main className="min-h-screen bg-ricePaper dark:bg-darkInk transition-colors duration-500">
      {/* Hero Section — Gold / Copper Theme */}
      <section className="relative overflow-hidden bg-gradient-to-b from-amber-950 via-amber-900 to-ink/95 dark:from-amber-950 dark:via-amber-900/80 dark:to-darkInk text-ricePaper py-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 border border-amber-400/40 rounded-full" />
          <div className="absolute bottom-10 right-10 w-96 h-96 border border-amber-300/20 rounded-full" />
          {/* Ancient coin decorative SVG */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] opacity-15">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              {/* Outer circle — coin rim */}
              <circle cx="100" cy="100" r="90" fill="none" stroke="currentColor" strokeWidth="1" className="text-amber-400" />
              {/* Inner circle */}
              <circle cx="100" cy="100" r="60" fill="none" stroke="currentColor" strokeWidth="0.6" className="text-amber-400" />
              {/* Square hole */}
              <rect x="80" y="80" width="40" height="40" fill="none" stroke="currentColor" strokeWidth="0.8" className="text-amber-400" />
              {/* Characters on coin */}
              <text x="100" y="70" textAnchor="middle" fontSize="14" className="text-amber-400" fill="currentColor">富</text>
              <text x="100" y="140" textAnchor="middle" fontSize="14" className="text-amber-400" fill="currentColor">贵</text>
            </svg>
          </div>
          {/* Floating coin decorations */}
          <div className="absolute top-20 left-1/4 text-amber-400/30 text-4xl">🪙</div>
          <div className="absolute bottom-20 right-1/4 text-amber-300/20 text-3xl">💰</div>
          <div className="absolute top-1/3 right-1/3 text-amber-400/20 text-2xl">💎</div>
        </div>

        <div className="relative max-w-4xl mx-auto text-center px-4">
          <h1 className="font-serif text-5xl md:text-7xl font-bold mb-6 tracking-wider">
            <span className="text-amber-300">Wealth</span>
            <span className="text-amber-100"> & </span>
            <span className="text-amber-300">Career</span>
          </h1>
          <p className="text-xl md:text-2xl text-amber-200/60 mb-4 font-light">
            财富事业
          </p>
          <p className="text-amber-200/40 max-w-xl mx-auto text-sm leading-relaxed">
            Unveil your prosperity blueprint through BaZi analysis. Discover your wealth
            potential, career path alignment, and the cosmic timing for financial success
            rooted in ancient Eastern wisdom.
          </p>

          <div className="mt-8 flex justify-center gap-4 text-xs text-amber-200/30">
            <span>💰 正财偏财</span>
            <span>·</span>
            <span>📈 事业运程</span>
            <span>·</span>
            <span>🏛️ 贵人相助</span>
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

            {isReading && !reading && (
              <div className="flex items-center justify-center py-20">
                <div className="animate-bagua-spin w-12 h-12 rounded-full border-2 border-amber-400 border-t-transparent" />
                <span className="ml-4 text-ink/50 dark:text-ricePaper/50">
                  Consulting the ancient wisdom of prosperity...
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
                <div className="text-6xl mb-6">💰</div>
                <h2 className="font-serif text-2xl text-ink/60 dark:text-ricePaper/60 mb-3">
                  Discover Your Wealth Blueprint
                </h2>
                <p className="text-ink/40 dark:text-ricePaper/40 max-w-md leading-relaxed">
                  Enter your birth details on the left to reveal your prosperity path.
                  Understand your wealth potential, career alignment, and the noble
                  supporters who will guide your journey.
                </p>
                <div className="mt-8 grid grid-cols-3 gap-6 text-center">
                  {[
                    { icon: '💰', label: 'Direct Wealth', desc: 'Your earning capacity' },
                    { icon: '📈', label: 'Career Path', desc: 'Professional alignment' },
                    { icon: '⭐', label: 'Noble Support', desc: 'Key benefactors' },
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
