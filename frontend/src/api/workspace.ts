import type {
  WorkspaceDeleteResponse,
  WorkspaceListResponse,
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
  const { data } = await http.post<WorkspaceUploadResponse>('/api/workspace/uploads', formData);
  return data;
}

export async function deleteWorkspaceItems(paths: string[]): Promise<WorkspaceDeleteResponse> {
  const { data } = await http.delete<WorkspaceDeleteResponse>('/api/workspace/items', {
    data: { paths },
  });
  return data;
}