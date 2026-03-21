import { create } from 'zustand';

import type { AuthUserResponse, HealthResponse } from '../api/types';

type AuthStatus = 'idle' | 'bootstrapping' | 'authenticated' | 'anonymous' | 'error';

interface AuthState {
  status: AuthStatus;
  user: AuthUserResponse | null;
  health: HealthResponse | null;
  initError: string | null;
  authNotice: string | null;
  setBootstrapping: () => void;
  setAuthenticated: (payload: { health: HealthResponse; user: AuthUserResponse }) => void;
  setAnonymous: (payload: { health: HealthResponse; notice?: string | null }) => void;
  setInitError: (message: string) => void;
  markUnauthenticated: (notice?: string | null) => void;
  clearAuthNotice: () => void;
  reset: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: 'idle',
  user: null,
  health: null,
  initError: null,
  authNotice: null,
  setBootstrapping: () =>
    set((state) =>
      state.status === 'authenticated' ? state : { ...state, status: 'bootstrapping', initError: null },
    ),
  setAuthenticated: ({ health, user }) =>
    set({
      status: 'authenticated',
      user,
      health,
      initError: null,
      authNotice: null,
    }),
  setAnonymous: ({ health, notice = null }) =>
    set({
      status: 'anonymous',
      user: null,
      health,
      initError: null,
      authNotice: notice,
    }),
  setInitError: (message) =>
    set((state) => ({
      status: 'error',
      user: null,
      health: state.health,
      initError: message,
      authNotice: state.authNotice,
    })),
  markUnauthenticated: (notice = null) =>
    set((state) => ({
      status: 'anonymous',
      user: null,
      health: state.health,
      initError: null,
      authNotice: notice,
    })),
  clearAuthNotice: () => set((state) => ({ ...state, authNotice: null })),
  reset: () =>
    set({
      status: 'idle',
      user: null,
      health: null,
      initError: null,
      authNotice: null,
    }),
}));
