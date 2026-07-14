'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

// ===== Type Definitions =====

interface PaywallProps {
  isOpen?: boolean;
  onClose: () => void;
  onUnlock: () => void;
  price?: string;
  title?: string;
  children?: React.ReactNode;
  className?: string;
}

// ===== Sub-components =====

function LockIcon() {
  return (
    <div className="relative w-16 h-16 mx-auto mb-4">
      <div className="absolute inset-0 rounded-full bg-amber-500/10 animate-pulse" />
      <div className="absolute inset-0 flex items-center justify-center">
        <svg
          className="w-10 h-10 text-amber-400 drop-shadow-[0_0_8px_rgba(245,158,11,0.3)]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          <circle cx="12" cy="16" r="1" fill="currentColor" />
        </svg>
      </div>
    </div>
  );
}

function BaguaSpinnerMini() {
  return (
    <div className="relative w-8 h-8 mx-auto">
      <div
        className="absolute inset-0 rounded-full border-2 border-amber-500/40 animate-bagua-spin"
        style={{
          background:
            'conic-gradient(from 0deg, transparent 0deg, rgba(217,119,6,0.2) 90deg, transparent 180deg, rgba(217,119,6,0.2) 270deg, transparent 360deg)',
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-amber-500/60" />
      </div>
    </div>
  );
}

// ===== Main Component =====

export default function Paywall({
  isOpen,
  onClose,
  onUnlock,
  price = '$9.99',
  title = '解锁完整命之书',
  children,
  className = '',
}: PaywallProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const overlayRef = useRef<HTMLDivElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
      const timer = setTimeout(() => setIsAnimating(false), 300);
      return () => clearTimeout(timer);
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === overlayRef.current) {
        onClose();
      }
    },
    [onClose]
  );

  const handleUnlock = useCallback(async () => {
    setIsProcessing(true);
    try {
      await onUnlock();
    } finally {
      setIsProcessing(false);
    }
  }, [onUnlock]);

  if (!isOpen && !isAnimating) return null;

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className={`fixed inset-0 z-50 flex items-end sm:items-center justify-center
        transition-all duration-300 ease-out
        ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}
        ${className}`}
    >
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black/80 backdrop-blur-md transition-opacity duration-300
          ${isOpen ? 'opacity-100' : 'opacity-0'}`}
      />

      {/* Blurred content behind paywall */}
      {children && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="blur-xl opacity-20 scale-110 select-none">{children}</div>
        </div>
      )}

      {/* Modal Card */}
      <div
        ref={modalRef}
        className={`
          relative w-full max-w-md mx-4
          transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]
          ${isOpen ? 'translate-y-0 sm:scale-100 opacity-100' : 'translate-y-full sm:translate-y-8 sm:scale-95 opacity-0'}
        `}
      >
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-stone-950 via-stone-900 to-stone-950 border border-amber-900/40 shadow-2xl shadow-amber-900/20">
          {/* Top decorative line */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/70 to-transparent" />

          {/* Close button */}
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 z-10 w-8 h-8 rounded-full
              bg-stone-800/80 border border-stone-700/50
              flex items-center justify-center
              text-stone-400 hover:text-stone-200 hover:border-stone-600
              transition-all duration-200"
            aria-label="关闭"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>

          {/* Content */}
          <div className="px-6 py-8 text-center">
            <LockIcon />

            <h2 className="text-2xl font-bold text-amber-100 tracking-wide mb-2">
              {title}
            </h2>

            <p className="text-sm text-stone-400 mb-2 leading-relaxed max-w-xs mx-auto">
              解锁完整命之书，查看详细命盘解读、大运流年分析和人生指引
            </p>

            {/* Features */}
            <div className="flex flex-col items-center gap-2 mb-6">
              {[
                { icon: '📖', text: '完整八字命盘解读' },
                { icon: '🔮', text: '十年大运详细分析' },
                { icon: '💫', text: '流年运势精准预测' },
                { icon: '🧘', text: '五行调和人生建议' },
              ].map((feature, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 text-sm text-stone-300 animate-fadeIn"
                  style={{ animationDelay: `${idx * 0.1}s` }}
                >
                  <span className="text-base">{feature.icon}</span>
                  <span>{feature.text}</span>
                </div>
              ))}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 mb-6">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-stone-700/50 to-transparent" />
              <span className="text-[10px] text-stone-600 uppercase tracking-widest">一次购买 永久解锁</span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-stone-700/50 to-transparent" />
            </div>

            {/* Price */}
            <div className="mb-6">
              <div className="flex items-baseline justify-center gap-1">
                <span className="text-4xl font-bold text-amber-300 tracking-tight">
                  {price}
                </span>
              </div>
              <p className="text-[10px] text-stone-600 mt-1">一次付费，终身解锁</p>
            </div>

            {/* CTA Button */}
            <button
              type="button"
              onClick={handleUnlock}
              disabled={isProcessing}
              className="relative w-full py-4 rounded-xl font-bold text-lg tracking-wider
                bg-gradient-to-r from-amber-700 via-amber-600 to-amber-700
                text-stone-900 shadow-lg shadow-amber-900/30
                hover:from-amber-600 hover:via-amber-500 hover:to-amber-600
                active:scale-[0.98] transition-all duration-300
                disabled:opacity-60 disabled:cursor-not-allowed disabled:active:scale-100
                overflow-hidden group"
            >
              <span className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <span
                  className="inline-block w-6 h-6 border-2 border-stone-800/40 rounded-full animate-bagua-spin"
                  style={{
                    background:
                      'conic-gradient(from 0deg, transparent 0deg, rgba(120,53,15,0.3) 90deg, transparent 180deg, rgba(120,53,15,0.3) 270deg, transparent 360deg)',
                  }}
                />
              </span>
              <span className="relative z-10 flex items-center justify-center gap-2">
                {isProcessing ? (
                  <>
                    <BaguaSpinnerMini />
                    <span>处理中...</span>
                  </>
                ) : (
                  <>
                    <span className="text-xl">🔓</span>
                    <span>立即解锁</span>
                  </>
                )}
              </span>
            </button>

            {/* Footer */}
            <p className="mt-4 text-[10px] text-stone-600">
              解锁即表示您同意我们的
              <button type="button" className="text-amber-600/80 hover:text-amber-500 underline underline-offset-2 mx-0.5">
                服务条款
              </button>
              和
              <button type="button" className="text-amber-600/80 hover:text-amber-500 underline underline-offset-2 mx-0.5">
                隐私政策
              </button>
            </p>
          </div>

          {/* Bottom decorative line */}
          <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/50 to-transparent" />
        </div>
      </div>
    </div>
  );
}
