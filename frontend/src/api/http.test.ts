import axios from 'axios';
import { describe, expect, it } from 'vitest';

import { getErrorMessage } from './http';

describe('getErrorMessage', () => {
  it('uses backend detail from axios responses before generic error text', () => {
    const error = new axios.AxiosError(
      'Request failed with status code 401',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        status: 401,
        statusText: 'Unauthorized',
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: { detail: 'Invalid username or password.' },
      },
    );

    expect(getErrorMessage(error, 'Login failed')).toBe('Invalid username or password.');
  });
});
