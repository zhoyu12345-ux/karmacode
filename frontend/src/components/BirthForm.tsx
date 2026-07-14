'use client';

import { useState } from 'react';

export interface BirthData {
  birthDate: string;
  birthHour: number;
  birthMinute: number;
  gender: 'male' | 'female';
  longitude: number;
  latitude: number;
}

interface BirthFormProps {
  onSubmit: (data: BirthData) => void;
  isLoading?: boolean;
}

const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  'Beijing': { lat: 39.9, lng: 116.4 },
  'Shanghai': { lat: 31.2, lng: 121.5 },
  'New York': { lat: 40.7, lng: -74.0 },
  'London': { lat: 51.5, lng: -0.1 },
  'Tokyo': { lat: 35.7, lng: 139.7 },
  'Sydney': { lat: -33.9, lng: 151.2 },
  'Los Angeles': { lat: 34.1, lng: -118.2 },
  'Singapore': { lat: 1.3, lng: 103.8 },
  'Paris': { lat: 48.9, lng: 2.3 },
  'Seoul': { lat: 37.6, lng: 127.0 },
};

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = [0, 15, 30, 45];

export default function BirthForm({ onSubmit, isLoading }: BirthFormProps) {
  const [birthDate, setBirthDate] = useState('1990-01-01');
  const [birthHour, setBirthHour] = useState(8);
  const [birthMinute, setBirthMinute] = useState(0);
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [city, setCity] = useState('Beijing');
  const [customLng, setCustomLng] = useState('');
  const [customLat, setCustomLat] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const coords = CITY_COORDS[city] || {
      lat: parseFloat(customLat) || 30,
      lng: parseFloat(customLng) || 120,
    };

    onSubmit({
      birthDate,
      birthHour,
      birthMinute,
      gender,
      longitude: coords.lng,
      latitude: coords.lat,
    });
  };

  return (
    <div className="chinese-card p-6 space-y-5 scroll-unfold">
      <h2 className="font-serif text-xl text-ink dark:text-ricePaper flex items-center gap-2">
        <span>🎋</span> Enter Your Birth Details
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Birth Date */}
        <div>
          <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
            📅 Birth Date
          </label>
          <input
            type="date"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            required
            max={new Date().toISOString().split('T')[0]}
            className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                       text-sm text-ink dark:text-ricePaper font-serif
                       focus:ring-2 focus:ring-gold/50 focus:border-gold transition-all"
          />
        </div>

        {/* Birth Time */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
              🕐 Hour (0-23)
            </label>
            <select
              value={birthHour}
              onChange={(e) => setBirthHour(Number(e.target.value))}
              className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                         text-sm text-ink dark:text-ricePaper font-serif"
            >
              {HOURS.map((h) => (
                <option key={h} value={h}>
                  {String(h).padStart(2, '0')}:00
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
              Minute
            </label>
            <select
              value={birthMinute}
              onChange={(e) => setBirthMinute(Number(e.target.value))}
              className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                         text-sm text-ink dark:text-ricePaper font-serif"
            >
              {MINUTES.map((m) => (
                <option key={m} value={m}>{String(m).padStart(2, '0')}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Gender */}
        <div>
          <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
            ⚧ Gender
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setGender('male')}
              className={`py-2.5 rounded-lg text-sm font-medium border-2 transition-all duration-300
                ${gender === 'male'
                  ? 'border-blueChine bg-blueChine/10 text-blueChine'
                  : 'border-ink/10 dark:border-ricePaper/10 text-ink/40 dark:text-ricePaper/40 hover:border-blueChine/30'
                }`}
            >
              ♂ Male
            </button>
            <button
              type="button"
              onClick={() => setGender('female')}
              className={`py-2.5 rounded-lg text-sm font-medium border-2 transition-all duration-300
                ${gender === 'female'
                  ? 'border-vermillion bg-vermillion/10 text-vermillion'
                  : 'border-ink/10 dark:border-ricePaper/10 text-ink/40 dark:text-ricePaper/40 hover:border-vermillion/30'
                }`}
            >
              ♀ Female
            </button>
          </div>
        </div>

        {/* Birth Place */}
        <div>
          <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
            📍 Birth City
          </label>
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                       text-sm text-ink dark:text-ricePaper font-serif mb-2"
          >
            {Object.keys(CITY_COORDS).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
            <option value="custom">Other (custom coordinates)</option>
          </select>

          {city === 'custom' && (
            <div className="grid grid-cols-2 gap-3 animate-scroll-unfold">
              <input
                type="number"
                placeholder="Longitude (e.g. 116.4)"
                value={customLng}
                onChange={(e) => setCustomLng(e.target.value)}
                step="0.1"
                className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2
                           text-xs text-ink dark:text-ricePaper"
              />
              <input
                type="number"
                placeholder="Latitude (e.g. 39.9)"
                value={customLat}
                onChange={(e) => setCustomLat(e.target.value)}
                step="0.1"
                className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2
                           text-xs text-ink dark:text-ricePaper"
              />
            </div>
          )}
        </div>

        {/* True Solar Time Note */}
        <div className="text-[10px] text-ink/30 dark:text-ricePaper/30 italic">
          ⏱ Your birth time will be adjusted to True Solar Time based on your birth location.
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-gold hover:bg-gold/90 text-ink font-medium rounded-lg
                     transition-all duration-300 transform hover:scale-[1.02]
                     disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                     shadow-lg shadow-gold/20 text-sm"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="bagua-loading bagua-loading-sm" />
              Calculating Your Cosmic Blueprint...
            </span>
          ) : (
            '🔮 Reveal My BaZi Chart'
          )}
        </button>
      </form>
    </div>
  );
}
