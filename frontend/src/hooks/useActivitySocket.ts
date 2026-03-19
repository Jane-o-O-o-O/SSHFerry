import { useEffect } from 'react';

import { ApiError } from '../api/http';
import { listActivity } from '../api/activity';
import { getActivitySocketUrl, parseActivitySocketMessage } from '../api/ws';
import { translate } from '../i18n';
import { useActivityStore } from '../store/activity';
import { useAuthStore } from '../store/auth';
import { useUiStore } from '../store/ui';

const POLL_INTERVAL_MS = 4000;
const RECONNECT_DELAY_MS = 2200;
const MAX_RECONNECT_BEFORE_POLLING = 3;

function getActivityFeatureError(error: unknown): string | null {
  if (error instanceof ApiError && error.status === 404) {
    return translate('activity.backendRestartRequired');
  }
  return null;
}

export function useActivitySocket() {
  const authReady = useAuthStore((state) => state.status === 'authenticated');
  const setSnapshot = useActivityStore((state) => state.setSnapshot);
  const setSocketStatus = useActivityStore((state) => state.setSocketStatus);
  const setSocketError = useActivityStore((state) => state.setSocketError);
  const pushToast = useUiStore((state) => state.pushToast);

  useEffect(() => {
    if (!authReady) {
      return undefined;
    }

    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let pollTimer: number | null = null;
    let reconnectAttempts = 0;
    let disposed = false;
    let unsupportedBackend = false;

    const stopPolling = () => {
      if (pollTimer) {
        window.clearInterval(pollTimer);
        pollTimer = null;
      }
    };

    const stopWithMissingFeature = (message: string) => {
      unsupportedBackend = true;
      setSocketStatus('error');
      setSocketError(message);
      stopPolling();
      if (socket && socket.readyState < WebSocket.CLOSING) {
        socket.close();
      }
      pushToast({
        tone: 'warning',
        title: translate('activity.title'),
        message,
      });
    };

    const pollActivity = async () => {
      try {
        const snapshot = await listActivity();
        setSnapshot(snapshot.items, snapshot.total, snapshot.sequence);
      } catch (error) {
        const featureError = getActivityFeatureError(error);
        if (featureError) {
          stopWithMissingFeature(featureError);
          return;
        }
        setSocketError(error instanceof Error ? error.message : translate('activity.pollFailed'));
      }
    };

    const startPolling = () => {
      if (unsupportedBackend) {
        return;
      }
      setSocketStatus('polling');
      void pollActivity();
      if (!pollTimer) {
        pollTimer = window.setInterval(() => {
          void pollActivity();
        }, POLL_INTERVAL_MS);
      }
    };

    const connect = () => {
      if (disposed || unsupportedBackend) {
        return;
      }

      setSocketStatus(reconnectAttempts > 0 ? 'reconnecting' : 'connecting');
      socket = new WebSocket(getActivitySocketUrl());

      socket.onopen = () => {
        reconnectAttempts = 0;
        stopPolling();
        setSocketStatus('connected');
        setSocketError(null);
      };

      socket.onmessage = (event) => {
        const payload = parseActivitySocketMessage(event.data);
        if (!payload) {
          return;
        }

        if (payload.type === 'activity_snapshot') {
          setSnapshot(payload.items, payload.total, payload.sequence);
          return;
        }

        setSocketError(payload.detail);
        pushToast({
          tone: 'warning',
          title: translate('activity.channelErrorTitle'),
          message: payload.detail,
        });
      };

      socket.onclose = () => {
        if (disposed || unsupportedBackend) {
          return;
        }
        reconnectAttempts += 1;
        if (reconnectAttempts >= MAX_RECONNECT_BEFORE_POLLING) {
          startPolling();
        }
        reconnectTimer = window.setTimeout(connect, RECONNECT_DELAY_MS);
      };

      socket.onerror = () => {
        if (!unsupportedBackend) {
          setSocketStatus('error');
          setSocketError(translate('activity.websocketError'));
        }
      };
    };

    void (async () => {
      try {
        const snapshot = await listActivity();
        if (disposed) {
          return;
        }
        setSnapshot(snapshot.items, snapshot.total, snapshot.sequence);
        connect();
      } catch (error) {
        if (disposed) {
          return;
        }
        const featureError = getActivityFeatureError(error);
        if (featureError) {
          stopWithMissingFeature(featureError);
          return;
        }
        setSocketError(error instanceof Error ? error.message : translate('activity.pollFailed'));
        connect();
      }
    })();

    return () => {
      disposed = true;
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }
      stopPolling();
      if (socket && socket.readyState < WebSocket.CLOSING) {
        socket.close();
      }
      setSocketStatus('idle');
    };
  }, [authReady, pushToast, setSnapshot, setSocketError, setSocketStatus]);
}
