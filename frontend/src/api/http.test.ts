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

  it('formats FastAPI validation details from axios responses', () => {
    const error = new axios.AxiosError(
      'Request failed with status code 422',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        status: 422,
        statusText: 'Unprocessable Entity',
        headers: {},
        config: { headers: new axios.AxiosHeaders() },
        data: {
          detail: [
            {
              loc: ['body', 'username'],
              msg: 'Username must be 3-32 characters.',
              type: 'value_error',
            },
          ],
        },
      },
    );

    expect(getErrorMessage(error, 'Signup failed')).toBe('Username must be 3-32 characters.');
  });
});
