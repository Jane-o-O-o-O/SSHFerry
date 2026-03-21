import { create } from 'zustand';

import type { ActivityItem } from '../api/types';
import type { TaskSocketStatus } from './tasks';

interface ActivityState {
  items: ActivityItem[];
  total: number;
  sequence: number;
  socketStatus: TaskSocketStatus;
  socketError: string | null;
  setSnapshot: (items: ActivityItem[], total: number, sequence: number) => void;
  setSocketStatus: (status: TaskSocketStatus) => void;
  setSocketError: (message: string | null) => void;
}

export const useActivityStore = create<ActivityState>((set) => ({
  items: [],
  total: 0,
  sequence: 0,
  socketStatus: 'idle',
  socketError: null,
  setSnapshot: (items, total, sequence) => set({ items, total, sequence }),
  setSocketStatus: (status) => set({ socketStatus: status }),
  setSocketError: (message) => set({ socketError: message }),
}));
