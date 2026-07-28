'use client';

import { useState } from 'react';

export interface BirthData {
  birthDate: string;
  birthHour: number;
  birthMinute: number;
  gender: 'male' | 'female';
  longitude: number;
  latitude: number;
  locationName: string;
}

interface BirthModalProps {
  onSubmit: (data: BirthData) => void;
  isOpen: boolean;
}

const POPULAR_CITIES = [
  'Beijing', 'Shanghai', 'Tokyo', 'Seoul',
  'New York', 'Los Angeles', 'London', 'Paris',
  'Sydney', 'Singapore', 'Bangkok',
];

export default function BirthModal({ onSubmit, isOpen }: BirthModalProps) {
  const [step, setStep] = useState(1);
  const [birthDate, setBirthDate] = useState('1995-01-01');
  const [birthHour, setBirthHour] = useState(12);
  const [birthMinute, setBirthMinute] = useState(0);
  const [gender, setGender] = useState<'male' | 'female'>('female');
  const [locationInput, setLocationInput] = useState('Beijing');
  const [geocodeResult, setGeocodeResult] = useState<{lat:number;lng:number;name:string}|null>({lat:39.9,lng:116.4,name:'Beijing, CN'});
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGeocoding, setIsGeocoding] = useState(false);

  if (!isOpen) return null;

  const handleGeocode = async (query: string) => {
    setIsGeocoding(true);
    try {
      const r = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
      const d = await r.json();
      if (d.length > 0) {
        setGeocodeResult({lat:parseFloat(d[0].lat),lng:parseFloat(d[0].lon),name:d[0].display_name.split(',')[0].trim()});
      }
    } catch(e) {}
    setIsGeocoding(false);
  };

  const handleSubmit = () => {
    const coords = geocodeResult || {lat:39.9,lng:116.4,name:'Beijing, CN'};
    onSubmit({
      birthDate,birthHour,birthMinute,gender,
      longitude:coords.lng,latitude:coords.lat,locationName:coords.name,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 backdrop-blur-sm">
      <div className="chinese-pattern bg-ricePaper dark:bg-darkInk max-w-lg w-full mx-4 p-8 space-y-6 scroll-unfold">
        {/* Progress */}
        <div className="flex gap-2 justify-center">
          {[1,2,3].map(i => (
            <div key={i} className={`h-1 w-12 rounded-full transition-all ${i<=step?'bg-gold':'bg-ink/10 dark:bg-ricePaper/10'}`}/>
          ))}
        </div>

        {/* Step 1: Birth Date + Time */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="font-serif text-2xl text-center text-ink dark:text-ricePaper">When were you born?</h2>
            <p className="text-xs text-center text-ink/40">Your birth moment holds the key to your cosmic blueprint</p>
            <div>
              <label className="text-xs text-ink/50 mb-1 block">Birth Date</label>
              <input type="date" value={birthDate} onChange={e=>setBirthDate(e.target.value)} max={new Date().toISOString().split('T')[0]}
                className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-4 py-3 text-ink dark:text-ricePaper font-serif"/>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-ink/50 mb-1 block">Hour</label>
                <select value={birthHour} onChange={e=>setBirthHour(+e.target.value)}
                  className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-3 text-ink dark:text-ricePaper font-serif">
                  {[...Array(24)].map((_,i)=><option key={i} value={i}>{String(i).padStart(2,'0')}:00</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-ink/50 mb-1 block">Minute</label>
                <select value={birthMinute} onChange={e=>setBirthMinute(+e.target.value)}
                  className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-3 py-3 text-ink dark:text-ricePaper font-serif">
                  {[0,15,30,45].map(m=><option key={m} value={m}>{String(m).padStart(2,'0')}</option>)}
                </select>
              </div>
            </div>
            <button onClick={()=>setStep(2)}
              className="w-full py-3 bg-gold text-ink font-medium rounded-lg hover:bg-gold/90 transition-all">
              Continue →
            </button>
          </div>
        )}

        {/* Step 2: Gender + Location */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="font-serif text-2xl text-center text-ink dark:text-ricePaper">Tell us about you</h2>
            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={()=>setGender('female')}
                className={`py-3 rounded-lg border-2 transition-all font-serif ${gender==='female'?'border-vermillion bg-vermillion/10 text-vermillion':'border-ink/10 text-ink/40'}`}>
                ♀ Female
              </button>
              <button type="button" onClick={()=>setGender('male')}
                className={`py-3 rounded-lg border-2 transition-all font-serif ${gender==='male'?'border-blueChine bg-blueChine/10 text-blueChine':'border-ink/10 text-ink/40'}`}>
                ♂ Male
              </button>
            </div>
            <div>
              <label className="text-xs text-ink/50 mb-1 block">Birth City</label>
              <input type="text" value={locationInput}
                onChange={e=>{setLocationInput(e.target.value);setShowSuggestions(true)}}
                onFocus={()=>setShowSuggestions(true)}
                onBlur={()=>{setTimeout(()=>setShowSuggestions(false),200);handleGeocode(locationInput)}}
                placeholder="Type your city..."
                className="w-full rounded-lg border border-gold/30 bg-white dark:bg-ink/50 px-4 py-3 text-ink dark:text-ricePaper font-serif"/>
              {showSuggestions && locationInput && (
                <div className="absolute z-10 mt-1 bg-white dark:bg-ink border border-gold/20 rounded-lg shadow-lg max-h-32 overflow-y-auto w-[calc(100%-2rem)]">
                  {POPULAR_CITIES.filter(c=>c.toLowerCase().includes(locationInput.toLowerCase())).map(c=>(
                    <button key={c} type="button" onMouseDown={e=>{e.preventDefault();setLocationInput(c);handleGeocode(c);setShowSuggestions(false)}}
                      className="w-full text-left px-3 py-1.5 text-sm text-ink dark:text-ricePaper hover:bg-gold/10 font-serif">📍 {c}</button>
                  ))}
                </div>
              )}
              {isGeocoding ? <div className="text-xs text-ink/40 mt-1">Locating...</div> :
               geocodeResult ? <div className="text-xs text-jade mt-1">✓ {geocodeResult.name}</div> : null}
            </div>
            <div className="flex gap-3">
              <button onClick={()=>setStep(1)} className="px-6 py-3 border border-gold/30 text-ink dark:text-ricePaper rounded-lg hover:bg-gold/10">← Back</button>
              <button onClick={()=>setStep(3)} className="flex-1 py-3 bg-gold text-ink font-medium rounded-lg hover:bg-gold/90 transition-all">Continue →</button>
            </div>
          </div>
        )}

        {/* Step 3: Confirm */}
        {step === 3 && (
          <div className="space-y-4 text-center">
            <div className="text-5xl">🔮</div>
            <h2 className="font-serif text-2xl text-ink dark:text-ricePaper">Ready to discover your blueprint?</h2>
            <div className="text-sm text-ink/50 space-y-1">
              <p>{birthDate} · {String(birthHour).padStart(2,'0')}:{String(birthMinute).padStart(2,'0')}</p>
              <p>{gender==='female'?'♀':'♂'} · {geocodeResult?.name||locationInput}</p>
            </div>
            <button onClick={handleSubmit}
              className="w-full py-4 bg-gold text-ink font-bold text-lg rounded-lg hover:bg-gold/90 transition-all shadow-lg shadow-gold/20">
              Reveal My Destiny 🔮
            </button>
            <button onClick={()=>setStep(2)} className="text-xs text-ink/30 hover:text-ink/50 underline">← Edit details</button>
          </div>
        )}
      </div>
    </div>
  );
}
