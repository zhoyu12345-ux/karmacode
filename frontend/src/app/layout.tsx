import type { Metadata } from "next";
import { Inter, Noto_Serif_SC, Playfair_Display } from "next/font/google";
import ThemeToggle from "@/components/ThemeToggle";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const notoSerifSC = Noto_Serif_SC({
  weight: ["400", "500", "600", "700", "900"],
  subsets: ["latin"],
  variable: "--font-serif-sc",
  display: "swap",
});

const playfairDisplay = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-serif-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: "KarmaCode - Discover Your Cosmic Blueprint",
  description:
    "AI-powered Chinese metaphysics for self-discovery. BaZi, Love & Career guidance.",
  keywords: [
    "KarmaCode",
    "Chinese metaphysics",
    "BaZi",
    "astrology",
    "self-discovery",
    "love guidance",
    "career guidance",
  ],
  openGraph: {
    title: "KarmaCode - Discover Your Cosmic Blueprint",
    description:
      "AI-powered Chinese metaphysics for self-discovery. BaZi, Love & Career guidance.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${notoSerifSC.variable} ${playfairDisplay.variable} h-full antialiased`}
    >
      <head>
        {/* Inline script to prevent flash of wrong theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('karmacode-theme');
                  if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col font-sans bg-ricePaper text-ink dark:bg-darkInk dark:text-ricePaper/90">
        {/* ========== Navigation ========== */}
        <header className="sticky top-0 z-50 border-b border-gold/30 bg-ricePaper/90 backdrop-blur-md dark:bg-darkInk/90 dark:border-gold/20">
          <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            {/* Logo */}
            <a
              href="/"
              className="flex items-center gap-2 text-xl font-bold tracking-wider text-vermillion dark:text-gold font-serif group ink-hover rounded-lg px-2 py-1"
            >
              <span className="text-2xl" aria-hidden="true">
                ☯
              </span>
              <span className="hidden sm:inline">KarmaCode</span>
            </a>

            {/* Nav Links */}
            <ul className="flex items-center gap-1 sm:gap-2">
              <li>
                <a
                  href="/"
                  className="px-3 py-2 text-sm font-medium text-ink/70 transition-colors hover:text-vermillion dark:text-ricePaper/60 dark:hover:text-gold rounded-md font-serif"
                >
                  Home
                </a>
              </li>
              <li>
                <a
                  href="/love"
                  className="px-3 py-2 text-sm font-medium text-ink/70 transition-colors hover:text-vermillion dark:text-ricePaper/60 dark:hover:text-gold rounded-md font-serif"
                >
                  Love
                </a>
              </li>
              <li>
                <a
                  href="/wealth"
                  className="px-3 py-2 text-sm font-medium text-ink/70 transition-colors hover:text-vermillion dark:text-ricePaper/60 dark:hover:text-gold rounded-md font-serif"
                >
                  Wealth
                </a>
              </li>
              <li>
                <a
                  href="/daily"
                  className="px-3 py-2 text-sm font-medium text-ink/70 transition-colors hover:text-vermillion dark:text-ricePaper/60 dark:hover:text-gold rounded-md font-serif"
                >
                  Daily
                </a>
              </li>
              {/* Dark Mode Toggle */}
              <li>
                <ThemeToggle />
              </li>
            </ul>
          </nav>
        </header>

        {/* ========== Main Content ========== */}
        <main className="flex-1">{children}</main>

        {/* ========== Footer ========== */}
        <footer className="border-t border-gold/30 bg-ricePaper/50 dark:bg-darkInk/50 dark:border-gold/20">
          <div className="mx-auto max-w-6xl px-6 py-8">
            <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left">
              {/* Brand */}
              <div>
                <p className="font-serif text-sm font-semibold text-ink dark:text-ricePaper/80">
                  ☯ KarmaCode
                </p>
                <p className="mt-1 text-xs text-ink/50 dark:text-ricePaper/40">
                  Discover Your Cosmic Blueprint
                </p>
              </div>

              {/* Disclaimer */}
              <p className="max-w-md text-xs leading-relaxed text-ink/40 dark:text-ricePaper/30">
                Disclaimer: KarmaCode provides AI-generated insights for
                entertainment and self-reflection purposes only. It is not a
                substitute for professional medical, legal, financial, or
                psychological advice. By using this service, you acknowledge
                that all interpretations are based on traditional Chinese
                metaphysics and modern AI analysis, and should be treated as
                guidance rather than definitive predictions.
              </p>
            </div>

            {/* Bottom bar */}
            <div className="mt-6 border-t border-gold/20 pt-4 text-center text-xs text-ink/30 dark:text-ricePaper/25">
              <p>
                &copy; {new Date().getFullYear()} KarmaCode. All rights
                reserved. Made with ☯ for seekers of wisdom.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
