"""Realtime websocket routes."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.api.deps import require_websocket_authenticated, require_websocket_owner
from backend.app.services.task_service import TaskService


TASK_SNAPSHOT_INTERVAL_SECONDS = 0.5
ACTIVITY_SNAPSHOT_INTERVAL_SECONDS = 0.5
LOG_SNAPSHOT_INTERVAL_SECONDS = 0.5
ACTIVITY_STREAM_LIMIT = 200
LOG_STREAM_LIMIT = 400
router = APIRouter(prefix='/ws', tags=['ws'])


def _activity_snapshot_message(app_state, user_id: str) -> dict[str, object]:
    snapshot = app_state.activity_service.snapshot(user_id=user_id, limit=ACTIVITY_STREAM_LIMIT)
    return {
        'type': 'activity_snapshot',
        'items': [
            {
                'sequence': item.sequence,
                'timestamp': item.timestamp,
                'level': item.level,
                'category': item.category,
                'action': item.action,
                'title': item.title,
                'message': item.message,
            }
            for item in snapshot.items
        ],
        'total': snapshot.total,
        'sequence': snapshot.sequence,
    }


def _log_snapshot_message(app_state) -> dict[str, object]:
    snapshot = app_state.log_service.snapshot(limit=LOG_STREAM_LIMIT)
    return {
        'type': 'log_snapshot',
        'items': [
            {
                'sequence': item.sequence,
                'timestamp': item.timestamp,
                'level': item.level,
                'logger': item.logger,
                'message': item.message,
                'rendered': item.rendered,
            }
            for item in snapshot.items
        ],
        'total': snapshot.total,
        'sequence': snapshot.sequence,
    }


@router.websocket('/tasks')
async def task_updates(websocket: WebSocket) -> None:
    context = require_websocket_authenticated(websocket)
    await websocket.accept()
    app_state = websocket.app.state.app_state
    service = TaskService(app_state)
    last_payload = ''

    try:
        while True:
            try:
                items = service.list_tasks(context.user.user_id)
                message = {
                    'type': 'task_snapshot',
                    'items': [item.model_dump() for item in items],
                    'total': len(items),
                }
            except Exception as exc:
                message = {
                    'type': 'error',
                    'detail': str(exc),
                }

            payload = json.dumps(message, sort_keys=True, separators=(',', ':'))
            if payload != last_payload:
                await websocket.send_json(message)
                last_payload = payload

            await asyncio.sleep(TASK_SNAPSHOT_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return


@router.websocket('/activity')
async def activity_updates(websocket: WebSocket) -> None:
    context = require_websocket_authenticated(websocket)
    await websocket.accept()
    app_state = websocket.app.state.app_state
    last_payload = ''

    try:
        while True:
            try:
                message = _activity_snapshot_message(app_state, context.user.user_id)
            except Exception as exc:
                message = {
                    'type': 'error',
                    'detail': str(exc),
                }

            payload = json.dumps(message, sort_keys=True, separators=(',', ':'))
            if payload != last_payload:
                await websocket.send_json(message)
                last_payload = payload

            await asyncio.sleep(ACTIVITY_SNAPSHOT_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return


@router.websocket('/logs')
async def log_updates(websocket: WebSocket) -> None:
    require_websocket_owner(websocket)
    await websocket.accept()
    app_state = websocket.app.state.app_state
    last_payload = ''

    try:
        while True:
            try:
                message = _log_snapshot_message(app_state)
            except Exception as exc:
                message = {
                    'type': 'error',
                    'detail': str(exc),
                }

            payload = json.dumps(message, sort_keys=True, separators=(',', ':'))
            if payload != last_payload:
                await websocket.send_json(message)
                last_payload = payload

            await asyncio.sleep(LOG_SNAPSHOT_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return
