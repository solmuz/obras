import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, TokenResponse } from '@/types';
import { apiClient } from '@/services/api';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setTokens: (accessToken: string, refreshToken: string) => {
        apiClient.setToken(accessToken, refreshToken);
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
          error: null,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      logout: () => {
        apiClient.clearToken();
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clear: () => {
        apiClient.clearToken();
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
          isLoading: false,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
