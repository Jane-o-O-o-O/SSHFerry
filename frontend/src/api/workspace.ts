import type { AxiosProgressEvent } from 'axios';

import type {
  WorkspaceDeleteResponse,
  WorkspaceListResponse,
  WorkspaceResetResponse,
  WorkspaceStatResponse,
  WorkspaceUploadResponse,
} from './types';
import { http } from './http';

export async function listWorkspaceItems(path?: string): Promise<WorkspaceListResponse> {
  const { data } = await http.get<WorkspaceListResponse>('/api/workspace/items', {
    params: path ? { path } : undefined,
  });
  return data;
}

export async function statWorkspacePath(path?: string): Promise<WorkspaceStatResponse> {
  const { data } = await http.get<WorkspaceStatResponse>('/api/workspace/items/stat', {
    params: path ? { path } : undefined,
  });
  return data;
}

export async function uploadWorkspaceFiles(payload: {
  targetPath?: string;
  files: File[];
  relativePaths?: string[];
  signal?: AbortSignal;
  onUploadProgress?: (event: AxiosProgressEvent) => void;
}): Promise<WorkspaceUploadResponse> {
  const formData = new FormData();
  payload.files.forEach((file) => {
    formData.append('files', file);
  });
  if (payload.targetPath) {
    formData.append('target_path', payload.targetPath);
  }
  payload.relativePaths?.forEach((relativePath) => {
    formData.append('relative_paths', relativePath);
  });
  const { data } = await http.post<WorkspaceUploadResponse>('/api/workspace/uploads', formData, {
    signal: payload.signal,
    onUploadProgress: payload.onUploadProgress,
    timeout: 0,
  });
  return data;
}

export async function deleteWorkspaceItems(paths: string[]): Promise<WorkspaceDeleteResponse> {
  const { data } = await http.delete<WorkspaceDeleteResponse>('/api/workspace/items', {
    data: { paths },
  });
  return data;
}

export async function resetWorkspaceData(): Promise<WorkspaceResetResponse> {
  const { data } = await http.post<WorkspaceResetResponse>('/api/workspace/reset');
  return data;
}
