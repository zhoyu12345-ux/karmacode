"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const isDarkMode = document.documentElement.classList.contains("dark");
    setIsDark(isDarkMode);
  }, []);

  function toggleTheme() {
    const html = document.documentElement;
    const next = !html.classList.contains("dark");
    if (next) {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
    setIsDark(next);
    try {
      localStorage.setItem("karmacode-theme", next ? "dark" : "light");
    } catch (e) {
      // localStorage not available
    }
  }

  // Avoid hydration mismatch by rendering a placeholder until mounted
  if (!mounted) {
    return (
      <button
        aria-label="Toggle theme"
        className="ml-2 rounded-full p-2 text-ink/60 dark:text-ricePaper/50"
      >
        <span className="text-sm">☯</span>
      </button>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className="ml-2 rounded-full p-2 text-ink/60 transition-colors hover:bg-gold/10 hover:text-ink dark:text-ricePaper/50 dark:hover:text-gold"
    >
      <span className="text-sm">{isDark ? "☀" : "☾"}</span>
    </button>
  );
}
