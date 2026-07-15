import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://karmacode.onrender.com',
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://knryvpqbwapnnayjewec.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_live_51Tt5xNJ0SpkVBZYP3m5H3mlCRWQlDFoYw0C4sQ8SPWsxa1XEp14lwZII1wlcMqYb0eo2AhoVfSnM4gqXz5aysiF900lm41ogVy',
  },
};

export default nextConfig;
