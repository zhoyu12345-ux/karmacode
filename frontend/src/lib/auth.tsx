/**
 * KarmaCode - Auth 上下文
 * Supabase 认证: AuthProvider + useAuth Hook
 */

'use client';

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import type { Session, User, AuthError } from '@supabase/supabase-js';
import { supabase } from './supabase';

// ============================================================
// 类型定义
// ============================================================

interface AuthContextType {
  /** 当前用户 */
  user: User | null;
  /** 当前会话 */
  session: Session | null;
  /** 是否正在加载认证状态 */
  loading: boolean;
  /** 是否已登录 */
  isAuthenticated: boolean;

  /** 邮箱注册 */
  signUp: (email: string, password: string, metadata?: Record<string, unknown>) => Promise<{ error: AuthError | null }>;
  /** 邮箱登录 */
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  /** 魔法链接登录（无密码） */
  signInWithMagicLink: (email: string) => Promise<{ error: AuthError | null }>;
  /** OAuth 登录 (Google, GitHub 等) */
  signInWithOAuth: (provider: 'google' | 'github' | 'discord') => Promise<{ error: AuthError | null }>;
  /** 退出登录 */
  signOut: () => Promise<void>;
  /** 刷新用户信息 */
  refreshUser: () => Promise<void>;
}

// ============================================================
// Context
// ============================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================
// AuthProvider
// ============================================================

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // ============================================================
  // 初始化: 获取当前会话并监听认证状态变化
  // ============================================================

  useEffect(() => {
    if (!supabase) {
      // Supabase 未配置，加载完成但无用户
      setLoading(false);
      return;
    }

    // 获取当前会话
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // 监听认证状态变化
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // ============================================================
  // 注册
  // ============================================================

  const signUp = useCallback(
    async (
      email: string,
      password: string,
      metadata?: Record<string, unknown>
    ) => {
      if (!supabase) {
        return {
          error: {
            name: 'AuthError',
            message: 'Supabase is not configured.',
            status: 500,
          } as AuthError,
        };
      }

      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata,
        },
      });

      return { error };
    },
    []
  );

  // ============================================================
  // 邮箱登录
  // ============================================================

  const signIn = useCallback(async (email: string, password: string) => {
    if (!supabase) {
      return {
        error: {
          name: 'AuthError',
          message: 'Supabase is not configured.',
          status: 500,
        } as AuthError,
      };
    }

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    return { error };
  }, []);

  // ============================================================
  // 魔法链接登录
  // ============================================================

  const signInWithMagicLink = useCallback(async (email: string) => {
    if (!supabase) {
      return {
        error: {
          name: 'AuthError',
          message: 'Supabase is not configured.',
          status: 500,
        } as AuthError,
      };
    }

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    return { error };
  }, []);

  // ============================================================
  // OAuth 登录
  // ============================================================

  const signInWithOAuth = useCallback(
    async (provider: 'google' | 'github' | 'discord') => {
      if (!supabase) {
        return {
          error: {
            name: 'AuthError',
            message: 'Supabase is not configured.',
            status: 500,
          } as AuthError,
        };
      }

      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      return { error };
    },
    []
  );

  // ============================================================
  // 退出登录
  // ============================================================

  const signOut = useCallback(async () => {
    if (!supabase) {
      setUser(null);
      setSession(null);
      return;
    }

    await supabase.auth.signOut();
    setUser(null);
    setSession(null);
  }, []);

  // ============================================================
  // 刷新用户信息
  // ============================================================

  const refreshUser = useCallback(async () => {
    if (!supabase) return;

    const { data } = await supabase.auth.getSession();
    setSession(data.session);
    setUser(data.session?.user ?? null);
  }, []);

  // ============================================================
  // Context Value
  // ============================================================

  const value: AuthContextType = {
    user,
    session,
    loading,
    isAuthenticated: !!user,
    signUp,
    signIn,
    signInWithMagicLink,
    signInWithOAuth,
    signOut,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ============================================================
// useAuth Hook
// ============================================================

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return context;
}

export default AuthProvider;
