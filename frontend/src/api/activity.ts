import type { ActivityListResponse } from './types';
import { http } from './http';

export async function listActivity(limit = 200): Promise<ActivityListResponse> {
  const { data } = await http.get<ActivityListResponse>('/api/activity', {
    params: { limit },
  });
  return data;
}
