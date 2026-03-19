"""Per-user workspace file service."""
from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import shutil
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status

from backend.app.schemas.workspace import (
    WorkspaceDeleteResponse,
    WorkspaceEntryResponse,
    WorkspaceListResponse,
    WorkspaceStatResponse,
    WorkspaceUploadResponse,
)


class WorkspaceService:
    """Manage one authenticated user's server-side workspace."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.expanduser().resolve(strict=False)

    def list_dir(self, user_id: str, raw_path: str | None = None) -> WorkspaceListResponse:
        user_root = self._ensure_user_root(user_id)
        current_path, actual_path = self._resolve_virtual_path(user_root, raw_path, require_exists=True, require_dir=True)
        items: list[WorkspaceEntryResponse] = []
        try:
            with os.scandir(actual_path) as entries:
                for entry in entries:
                    try:
                        stat_result = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    entry_path = Path(entry.path).resolve(strict=False)
                    items.append(
                        WorkspaceEntryResponse(
                            name=entry.name,
                            path=self._to_virtual_path(user_root, entry_path),
                            is_dir=entry.is_dir(follow_symlinks=False),
                            size=0 if entry.is_dir(follow_symlinks=False) else int(stat_result.st_size),
                            mtime=float(stat_result.st_mtime),
                        )
                    )
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Permission denied: {current_path}') from exc

        items.sort(key=lambda item: (not item.is_dir, item.name.lower()))
        return WorkspaceListResponse(
            current_path=current_path,
            parent_path=self._parent_virtual_path(current_path),
            items=items,
            total=len(items),
        )

    def stat_path(self, user_id: str, raw_path: str | None = None) -> WorkspaceStatResponse:
        user_root = self._ensure_user_root(user_id)
        current_path, actual_path = self._resolve_virtual_path(user_root, raw_path, require_exists=True, require_dir=False)
        try:
            stat_result = actual_path.stat()
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Permission denied: {current_path}') from exc

        file_count, dir_count, total_size = self._scan_stats(actual_path)
        return WorkspaceStatResponse(
            entry=WorkspaceEntryResponse(
                name=actual_path.name or user_id,
                path=current_path,
                is_dir=actual_path.is_dir(),
                size=0 if actual_path.is_dir() else int(stat_result.st_size),
                mtime=float(stat_result.st_mtime),
            ),
            file_count=file_count,
            dir_count=dir_count,
            total_size=total_size,
        )

    def save_uploads(
        self,
        user_id: str,
        files: list[UploadFile],
        target_path: str | None = None,
        relative_paths: list[str] | None = None,
    ) -> WorkspaceUploadResponse:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='At least one file is required.')

        user_root = self._ensure_user_root(user_id)
        normalized_target_path, target_dir = self._resolve_virtual_path(user_root, target_path, require_exists=True, require_dir=True)
        normalized_relative_paths = self._normalize_relative_paths(files, relative_paths)

        planned_targets: list[tuple[UploadFile, str, Path]] = []
        seen_destinations: set[str] = set()
        for upload, relative_path in zip(files, normalized_relative_paths, strict=True):
            destination_virtual_path = self._join_virtual_path(normalized_target_path, relative_path)
            _, destination_actual_path = self._resolve_virtual_path(
                user_root,
                destination_virtual_path,
                require_exists=False,
                require_dir=False,
            )
            destination_key = str(destination_actual_path).lower()
            if destination_key in seen_destinations:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Duplicate upload target: {destination_virtual_path}')
            if destination_actual_path.exists():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Workspace path already exists: {destination_virtual_path}')
            seen_destinations.add(destination_key)
            planned_targets.append((upload, destination_virtual_path, destination_actual_path))

        uploaded_paths: list[str] = []
        for upload, destination_virtual_path, destination_actual_path in planned_targets:
            destination_actual_path.parent.mkdir(parents=True, exist_ok=True)
            with destination_actual_path.open('wb') as handle:
                self._copy_upload(upload.file, handle)
            uploaded_paths.append(destination_virtual_path)
            upload.file.close()

        return WorkspaceUploadResponse(target_path=normalized_target_path, uploaded_paths=uploaded_paths, total=len(uploaded_paths))

    def delete_paths(self, user_id: str, raw_paths: list[str]) -> WorkspaceDeleteResponse:
        if not raw_paths:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='At least one workspace path is required.')

        user_root = self._ensure_user_root(user_id)
        normalized_targets: list[tuple[str, Path]] = []
        seen_paths: set[str] = set()
        for raw_path in raw_paths:
            normalized_path, actual_path = self._resolve_virtual_path(user_root, raw_path, require_exists=True, require_dir=False)
            if normalized_path == '/':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Workspace root cannot be deleted.')
            if normalized_path in seen_paths:
                continue
            seen_paths.add(normalized_path)
            normalized_targets.append((normalized_path, actual_path))

        normalized_targets.sort(key=lambda item: item[0].count('/'), reverse=True)
        deleted_paths: list[str] = []
        for normalized_path, actual_path in normalized_targets:
            if actual_path.is_dir():
                shutil.rmtree(actual_path)
            else:
                actual_path.unlink()
            deleted_paths.append(normalized_path)

        return WorkspaceDeleteResponse(deleted_paths=deleted_paths, total=len(deleted_paths))

    def resolve_workspace_path(self, user_id: str, raw_path: str, *, require_exists: bool) -> Path:
        user_root = self._ensure_user_root(user_id)
        _, actual_path = self._resolve_virtual_path(user_root, raw_path, require_exists=require_exists, require_dir=False)
        return actual_path

    def _ensure_user_root(self, user_id: str) -> Path:
        root = self.workspace_root / self._sanitize_user_id(user_id)
        root.mkdir(parents=True, exist_ok=True)
        return root.resolve(strict=False)

    @staticmethod
    def _sanitize_user_id(user_id: str) -> str:
        sanitized = ''.join(char if char.isalnum() or char in {'-', '_', '.'} else '-' for char in user_id.strip())
        return sanitized or 'unknown-user'

    def _resolve_virtual_path(
        self,
        user_root: Path,
        raw_path: str | None,
        *,
        require_exists: bool,
        require_dir: bool,
    ) -> tuple[str, Path]:
        normalized_path = self._normalize_virtual_path(raw_path)
        relative = normalized_path.lstrip('/')
        actual_path = (user_root / Path(relative.replace('/', os.sep))).resolve(strict=False) if relative else user_root
        if actual_path != user_root and user_root not in actual_path.parents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Illegal workspace path: {raw_path}')
        if require_exists and not actual_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Workspace path not found: {normalized_path}')
        if require_dir and actual_path.exists() and not actual_path.is_dir():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Workspace path is not a directory: {normalized_path}')
        return normalized_path, actual_path

    @staticmethod
    def _normalize_virtual_path(raw_path: str | None) -> str:
        if raw_path is None:
            return '/'
        value = raw_path.strip().replace('\\', '/')
        if not value or value == '.':
            return '/'
        candidate = PurePosixPath('/' + value.lstrip('/'))
        parts: list[str] = []
        for part in candidate.parts:
            if part in {'', '/'}:
                continue
            if part in {'.', '..'}:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Illegal workspace path: {raw_path}')
            parts.append(part)
        return '/' + '/'.join(parts) if parts else '/'

    def _normalize_relative_paths(self, files: list[UploadFile], relative_paths: list[str] | None) -> list[str]:
        if relative_paths is None:
            relative_paths = []
        if relative_paths and len(relative_paths) != len(files):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='relative_paths must match the number of files.')

        normalized: list[str] = []
        for index, upload in enumerate(files):
            raw_relative_path = relative_paths[index] if relative_paths else (upload.filename or f'upload-{index + 1}')
            relative = raw_relative_path.strip().replace('\\', '/')
            if not relative or relative.startswith('/'):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Illegal upload path: {raw_relative_path}')
            parts = [part for part in relative.split('/') if part]
            if not parts or any(part in {'.', '..'} for part in parts):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Illegal upload path: {raw_relative_path}')
            normalized.append('/'.join(parts))
        return normalized

    @staticmethod
    def _join_virtual_path(parent: str, relative_path: str) -> str:
        parent_parts = [] if parent == '/' else parent.strip('/').split('/')
        child_parts = relative_path.strip('/').split('/')
        return '/' + '/'.join([*parent_parts, *child_parts])

    @staticmethod
    def _parent_virtual_path(path: str) -> str | None:
        if path == '/':
            return None
        parent = str(PurePosixPath(path).parent)
        return parent if parent != '.' else '/'

    @staticmethod
    def _to_virtual_path(user_root: Path, actual_path: Path) -> str:
        relative = actual_path.resolve(strict=False).relative_to(user_root)
        if str(relative) == '.':
            return '/'
        return '/' + PurePosixPath(relative.as_posix()).as_posix().lstrip('/')

    @classmethod
    def _scan_stats(cls, actual_path: Path) -> tuple[int, int, int]:
        if actual_path.is_file():
            return 1, 0, int(actual_path.stat().st_size)

        file_count = 0
        dir_count = 0
        total_size = 0
        for child in actual_path.iterdir():
            if child.is_dir():
                dir_count += 1
                sub_files, sub_dirs, sub_size = cls._scan_stats(child)
                file_count += sub_files
                dir_count += sub_dirs
                total_size += sub_size
            else:
                file_count += 1
                total_size += int(child.stat().st_size)
        return file_count, dir_count, total_size

    @staticmethod
    def _copy_upload(source: BinaryIO, destination: BinaryIO) -> None:
        source.seek(0)
        shutil.copyfileobj(source, destination)