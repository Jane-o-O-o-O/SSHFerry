import { create } from 'zustand';

import type { TaskItem } from '../api/types';

export type TaskSocketStatus = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'polling' | 'error';

interface ClientTaskControl {
  abort?: () => void;
}

interface TasksState {
  items: TaskItem[];
  total: number;
  remoteItems: TaskItem[];
  clientItems: TaskItem[];
  clientControls: Record<string, ClientTaskControl>;
  socketStatus: TaskSocketStatus;
  socketError: string | null;
  setRemoteSnapshot: (items: TaskItem[], total: number) => void;
  upsertClientTask: (task: TaskItem, control?: ClientTaskControl) => void;
  patchClientTask: (taskId: string, patch: Partial<TaskItem>) => void;
  clearClientFinished: () => void;
  clearClientTasks: () => void;
  cancelClientTask: (taskId: string) => boolean;
  setSocketStatus: (status: TaskSocketStatus) => void;
  setSocketError: (message: string | null) => void;
}

function mergeItems(remoteItems: TaskItem[], clientItems: TaskItem[]): TaskItem[] {
  return [...clientItems, ...remoteItems];
}

function upsertTask(items: TaskItem[], task: TaskItem): TaskItem[] {
  const index = items.findIndex((item) => item.task_id === task.task_id);
  if (index === -1) {
    return [...items, task];
  }
  return items.map((item, itemIndex) => (itemIndex === index ? task : item));
}

export const useTasksStore = create<TasksState>((set, get) => ({
  items: [],
  total: 0,
  remoteItems: [],
  clientItems: [],
  clientControls: {},
  socketStatus: 'idle',
  socketError: null,
  setRemoteSnapshot: (remoteItems) =>
    set((state) => ({
      remoteItems,
      items: mergeItems(remoteItems, state.clientItems),
      total: remoteItems.length + state.clientItems.length,
    })),
  upsertClientTask: (task, control) =>
    set((state) => {
      const clientItems = upsertTask(state.clientItems, task);
      const clientControls = control ? { ...state.clientControls, [task.task_id]: control } : state.clientControls;
      return {
        clientItems,
        clientControls,
        items: mergeItems(state.remoteItems, clientItems),
        total: state.remoteItems.length + clientItems.length,
      };
    }),
  patchClientTask: (taskId, patch) =>
    set((state) => {
      const current = state.clientItems.find((item) => item.task_id === taskId);
      if (!current) {
        return state;
      }
      const nextTask = { ...current, ...patch };
      const clientItems = upsertTask(state.clientItems, nextTask);
      const clientControls = { ...state.clientControls };
      if (nextTask.is_finished) {
        delete clientControls[taskId];
      }
      return {
        clientItems,
        clientControls,
        items: mergeItems(state.remoteItems, clientItems),
        total: state.remoteItems.length + clientItems.length,
      };
    }),
  clearClientFinished: () =>
    set((state) => {
      const clientItems = state.clientItems.filter((item) => !item.is_finished);
      const activeIds = new Set(clientItems.map((item) => item.task_id));
      const clientControls = Object.fromEntries(
        Object.entries(state.clientControls).filter(([taskId]) => activeIds.has(taskId)),
      );
      return {
        clientItems,
        clientControls,
        items: mergeItems(state.remoteItems, clientItems),
        total: state.remoteItems.length + clientItems.length,
      };
    }),
  clearClientTasks: () =>
    set((state) => ({
      clientItems: [],
      clientControls: {},
      items: mergeItems(state.remoteItems, []),
      total: state.remoteItems.length,
    })),
  cancelClientTask: (taskId) => {
    const control = get().clientControls[taskId];
    const task = get().clientItems.find((item) => item.task_id === taskId);
    if (!control || !task || task.is_finished) {
      return false;
    }

    control.abort?.();
    set((state) => {
      const clientItems = state.clientItems.map<TaskItem>((item) =>
        item.task_id === taskId
          ? {
              ...item,
              status: 'canceled' as const,
              interrupted: true,
              paused: false,
              speed: 0,
              end_time: item.end_time ?? Date.now() / 1000,
              is_finished: true,
            }
          : item,
      );
      const clientControls = { ...state.clientControls };
      delete clientControls[taskId];
      return {
        clientItems,
        clientControls,
        items: mergeItems(state.remoteItems, clientItems),
        total: state.remoteItems.length + clientItems.length,
      };
    });
    return true;
  },
  setSocketStatus: (status) => set({ socketStatus: status }),
  setSocketError: (message) => set({ socketError: message }),
}));
