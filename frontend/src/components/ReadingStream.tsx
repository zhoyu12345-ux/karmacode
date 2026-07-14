'use client';

import { useEffect, useRef } from 'react';

interface ReadingStreamProps {
  content: string;
  isStreaming: boolean;
}

export default function ReadingStream({ content, isStreaming }: ReadingStreamProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when streaming
  useEffect(() => {
    if (isStreaming && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [content, isStreaming]);

  if (!content && !isStreaming) {
    return null;
  }

  // Simple markdown-like rendering
  const renderContent = (text: string) => {
    return text
      .split('\n')
      .map((line, i) => {
        // Headers
        if (line.startsWith('## ')) {
          return (
            <h2 key={i} className="font-serif text-xl text-gold mt-6 mb-3 first:mt-0">
              {line.slice(3)}
            </h2>
          );
        }
        if (line.startsWith('### ')) {
          return (
            <h3 key={i} className="font-serif text-lg text-ink dark:text-ricePaper mt-4 mb-2">
              {line.slice(4)}
            </h3>
          );
        }

        // Bold
        let rendered = line.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-ink dark:text-ricePaper">$1</strong>');

        // Emoji lines
        if (line.match(/^[📜💑💰🌟🔮📅💎🌳🌸💫🌙☀️⚡]/)) {
          return (
            <p
              key={i}
              className="text-sm leading-relaxed text-ink/70 dark:text-ricePaper/70 my-2"
              dangerouslySetInnerHTML={{ __html: rendered }}
            />
          );
        }

        // Divider
        if (line.trim() === '---') {
          return <hr key={i} className="my-4 border-gold/20" />;
        }

        // Blockquote
        if (line.startsWith('> ')) {
          return (
            <blockquote
              key={i}
              className="border-l-3 border-gold/50 pl-4 my-3 text-sm italic text-ink/60 dark:text-ricePaper/60"
            >
              {line.slice(2)}
            </blockquote>
          );
        }

        // Empty line
        if (!line.trim()) {
          return <br key={i} />;
        }

        // Default paragraph
        return (
          <p
            key={i}
            className="text-sm leading-relaxed text-ink/70 dark:text-ricePaper/70 my-1.5"
            dangerouslySetInnerHTML={{ __html: rendered }}
          />
        );
      });
  };

  return (
    <div
      ref={containerRef}
      className="p-6 max-h-[70vh] overflow-y-auto scroll-smooth"
    >
      <div className="prose prose-sm dark:prose-invert max-w-none font-serif">
        {renderContent(content)}
      </div>

      {/* Streaming cursor */}
      {isStreaming && (
        <span className="inline-block w-2 h-4 bg-gold animate-pulse rounded-sm ml-0.5 align-middle" />
      )}

      {/* Empty state */}
      {!content && isStreaming && (
        <div className="flex items-center justify-center py-12">
          <div className="bagua-loading" />
        </div>
      )}
    </div>
  );
}
