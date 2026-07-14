'use client';

import { useState, useCallback } from 'react';

export interface BirthData {
  birthDate: string;
  birthHour: number;
  birthMinute: number;
  gender: 'male' | 'female';
  longitude: number;
  latitude: number;
  locationName: string;
}

interface BirthFormProps {
  onSubmit: (data: BirthData) => void;
  isLoading?: boolean;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = [0, 15, 30, 45];

const POPULAR_CITIES = [
  'Beijing', 'Shanghai', 'Tokyo', 'Seoul',
  'New York', 'Los Angeles', 'London', 'Paris',
  'Sydney', 'Singapore', 'Bangkok', 'Dubai',
];

export default function BirthForm({ onSubmit, isLoading }: BirthFormProps) {
  const [birthDate, setBirthDate] = useState('1990-01-01');
  const [birthHour, setBirthHour] = useState(8);
  const [birthMinute, setBirthMinute] = useState(0);
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [locationInput, setLocationInput] = useState('Beijing');
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [geocodeResult, setGeocodeResult] = useState<{lat: number; lng: number; name: string} | null>(
    { lat: 39.9, lng: 116.4, name: 'Beijing, CN' }
  );
  const [showSuggestions, setShowSuggestions] = useState(false);

  // 地理编码：输入城市名 → 经纬度
  const geocode = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setIsGeocoding(true);
    try {
      const resp = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      );
      const data = await resp.json();
      if (data.length > 0) {
        const result = {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon),
          name: data[0].display_name.split(',')[0] + ', ' + (data[0].display_name.split(',').pop() || '').trim(),
        };
        setGeocodeResult(result);
        return result;
      }
    } catch (e) {
      console.warn('Geocoding failed, using default');
    } finally {
      setIsGeocoding(false);
    }
    return null;
  }, []);

  const handleLocationBlur = async () => {
    setShowSuggestions(false);
    if (locationInput.trim()) {
      await geocode(locationInput);
    }
  };

  const handleSuggestionClick = async (city: string) => {
    setLocationInput(city);
    setShowSuggestions(false);
    await geocode(city);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const coords = geocodeResult || { lat: 39.9, lng: 116.4, name: 'Beijing, CN' };

    onSubmit({
      birthDate,
      birthHour,
      birthMinute,
      gender,
      longitude: coords.lng,
      latitude: coords.lat,
      locationName: coords.name,
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
        <div className="relative">
          <label className="block text-xs font-medium text-ink/50 dark:text-ricePaper/50 mb-1.5">
            📍 Birth City
          </label>
          <input
            type="text"
            value={locationInput}
            onChange={(e) => {
              setLocationInput(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={handleLocationBlur}
            placeholder="Type your birth city..."
            className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-2.5
                       text-sm text-ink dark:text-ricePaper font-serif
                       focus:ring-2 focus:ring-gold/50 focus:border-gold transition-all"
          />

          {/* Suggestions dropdown */}
          {showSuggestions && locationInput.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white dark:bg-ink border border-gold/20 rounded-lg shadow-lg max-h-40 overflow-y-auto">
              {POPULAR_CITIES.filter(c => c.toLowerCase().includes(locationInput.toLowerCase())).map(city => (
                <button
                  key={city}
                  type="button"
                  onMouseDown={(e) => { e.preventDefault(); handleSuggestionClick(city); }}
                  className="w-full text-left px-3 py-2 text-sm text-ink dark:text-ricePaper hover:bg-gold/10 transition-colors font-serif"
                >
                  📍 {city}
                </button>
              ))}
            </div>
          )}

          {/* Geocode result indicator */}
          {isGeocoding ? (
            <div className="flex items-center gap-1 mt-1 text-xs text-ink/40 dark:text-ricePaper/40">
              <span className="bagua-loading bagua-loading-sm" />
              Locating...
            </div>
          ) : geocodeResult ? (
            <div className="flex items-center gap-1 mt-1 text-xs text-jade">
              ✓ {geocodeResult.name} ({geocodeResult.lat.toFixed(1)}°, {geocodeResult.lng.toFixed(1)}°)
            </div>
          ) : (
            <div className="flex items-center gap-1 mt-1 text-xs text-vermillion">
              ⚠ City not found — using default coordinates
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
