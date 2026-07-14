import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://karmacode.onrender.com',
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://knryvpqbwapnnayjewec.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_51Tt5xrR08F2WXvbDcMAASaUmxxUX9Ityne4MTD8Rnd9FTqnVSleyl8LH3xozt6LaxwVWWzN2kwyEU0iMtzfHITdC005XDgNcxT',
  },
};

export default nextConfig;
