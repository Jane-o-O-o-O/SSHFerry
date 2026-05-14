import type { ActivitySocketMessage, LogSocketMessage, TaskSocketMessage } from './types';

const TASK_SOCKET_PATH = '/api/ws/tasks';
const ACTIVITY_SOCKET_PATH = '/api/ws/activity';
const LOG_SOCKET_PATH = '/api/ws/logs';
const DRAG_MIME = 'application/x-sshferry-transfer';

function getDefaultSocketBase(): string {
  if (typeof window === 'undefined') {
    return 'ws://127.0.0.1:18080';
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}`;
}

function buildSocketUrl(path: string): string {
  const base = import.meta.env.VITE_BACKEND_WS_URL || getDefaultSocketBase();
  const url = new URL(path, `${base.replace(/\/$/, '')}/`);
  return url.toString();
}

function parseSocketMessage<T>(raw: string): T | null {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function getTaskSocketUrl(): string {
  return buildSocketUrl(TASK_SOCKET_PATH);
}

export function getActivitySocketUrl(): string {
  return buildSocketUrl(ACTIVITY_SOCKET_PATH);
}

export function getLogSocketUrl(): string {
  return buildSocketUrl(LOG_SOCKET_PATH);
}

export function parseTaskSocketMessage(raw: string): TaskSocketMessage | null {
  return parseSocketMessage<TaskSocketMessage>(raw);
}

export function parseActivitySocketMessage(raw: string): ActivitySocketMessage | null {
  return parseSocketMessage<ActivitySocketMessage>(raw);
}

export function parseLogSocketMessage(raw: string): LogSocketMessage | null {
  return parseSocketMessage<LogSocketMessage>(raw);
}

export function getTransferDragMime(): string {
  return DRAG_MIME;
}
