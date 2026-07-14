'use client';

import { useState, useCallback } from 'react';
import BirthForm, { BirthData } from '@/components/BirthForm';
import ChartDisplay from '@/components/ChartDisplay';
import ReadingStream from '@/components/ReadingStream';
import Paywall from '@/components/Paywall';
import { calculateBazi, streamReading, ChartData } from '@/lib/api';

export default function LovePage() {
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

      // Auto-start love reading
      setIsReading(true);

      const stream = streamReading(data, 'love');
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
      const stream = streamReading(birthData, 'love');
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
      {/* Hero Section — Rose Gold Theme */}
      <section className="relative overflow-hidden bg-gradient-to-b from-rose-950 via-rose-900 to-ink/95 dark:from-rose-950 dark:via-rose-900/80 dark:to-darkInk text-ricePaper py-20">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 border border-rose-300/40 rounded-full" />
          <div className="absolute bottom-10 right-10 w-96 h-96 border border-rose-400/20 rounded-full" />
          {/* Heart-shaped decorative SVG */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] opacity-15">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              <path
                d="M100 180 C40 140, 10 90, 40 50 C60 20, 100 50, 100 50 C100 50, 140 20, 160 50 C190 90, 160 140, 100 180Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.8"
                className="text-rose-300"
              />
            </svg>
          </div>
          {/* Floating petals */}
          <div className="absolute top-20 left-1/4 text-rose-400/30 text-4xl">🌸</div>
          <div className="absolute bottom-20 right-1/4 text-rose-400/20 text-3xl">💕</div>
          <div className="absolute top-1/3 right-1/3 text-rose-300/20 text-2xl">💖</div>
        </div>

        <div className="relative max-w-4xl mx-auto text-center px-4">
          <h1 className="font-serif text-5xl md:text-7xl font-bold mb-6 tracking-wider">
            <span className="text-rose-300">Love</span>
            <span className="text-rose-100"> & </span>
            <span className="text-rose-300">Marriage</span>
          </h1>
          <p className="text-xl md:text-2xl text-rose-200/60 mb-4 font-light">
            婚姻情感
          </p>
          <p className="text-rose-200/40 max-w-xl mx-auto text-sm leading-relaxed">
            Discover your romantic blueprint through the wisdom of BaZi. Understand your
            relationship patterns, marriage timing, and how to cultivate lasting love
            through ancient Chinese metaphysics.
          </p>

          {/* 合婚 Button — Future Feature */}
          <div className="mt-8">
            <button
              disabled
              className="px-8 py-3 rounded-full border-2 border-rose-400/30 bg-rose-400/10
                         text-rose-300/60 text-sm font-medium font-serif tracking-wider
                         transition-all duration-300 cursor-not-allowed
                         flex items-center gap-2 mx-auto"
              title="Coming soon — two-person BaZi comparison"
            >
              <span>💍</span>
              <span>合婚 · Coming Soon</span>
              <span className="text-[10px] text-rose-400/30">(Two-Person Compatibility)</span>
            </button>
            <p className="text-[10px] text-rose-300/20 mt-2">
              Compare two BaZi charts for marriage compatibility — a future feature
            </p>
          </div>

          <div className="mt-8 flex justify-center gap-4 text-xs text-rose-200/30">
            <span>💑 桃花运</span>
            <span>·</span>
            <span>💍 红鸾星</span>
            <span>·</span>
            <span>💖 合婚配对</span>
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
                <div className="animate-bagua-spin w-12 h-12 rounded-full border-2 border-rose-400 border-t-transparent" />
                <span className="ml-4 text-ink/50 dark:text-ricePaper/50">
                  Consulting the ancient wisdom of love...
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
                <div className="text-6xl mb-6">💑</div>
                <h2 className="font-serif text-2xl text-ink/60 dark:text-ricePaper/60 mb-3">
                  Discover Your Love Blueprint
                </h2>
                <p className="text-ink/40 dark:text-ricePaper/40 max-w-md leading-relaxed">
                  Enter your birth details on the left to uncover your romantic destiny.
                  Understand your Peach Blossom luck, marriage timing, and what the stars
                  say about your love life.
                </p>
                <div className="mt-8 grid grid-cols-3 gap-6 text-center">
                  {[
                    { icon: '🌸', label: 'Peach Blossom', desc: 'Romance timing' },
                    { icon: '💍', label: 'Red Luan Star', desc: 'Marriage indicator' },
                    { icon: '💖', label: 'Compatibility', desc: 'Cosmic match analysis' },
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
          onUnlock={handleContinueReading}
          onClose={() => setShowPaywall(false)}
        />
      )}
    </main>
  );
}
