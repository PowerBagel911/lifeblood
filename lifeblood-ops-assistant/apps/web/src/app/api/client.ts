/**
 * API client for Lifeblood Operations Assistant backend
 */

import { AskRequest, AskResponse } from '../../types';

// For Docker production: nginx proxies /api to backend
// For local dev: direct connection to backend on port 8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (window.location.port === '3000' ? '/api' : 'http://localhost:8000');

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public traceId?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class LifebloodAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async ask(question: string, mode: AskRequest['mode'], top_k: number = 5): Promise<AskResponse> {
    const url = `${this.baseUrl}/ask`;
    
    const requestBody: AskRequest = {
      question,
      mode,
      top_k
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        let errorMessage = `Request failed with status ${response.status}`;
        let traceId: string | undefined;

        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (errorData.detail.message) {
              errorMessage = errorData.detail.message;
              traceId = errorData.detail.trace_id;
            }
          }
        } catch {
          // Failed to parse error JSON, use default message
        }

        throw new APIError(errorMessage, response.status, traceId);
      }

      const data: AskResponse = await response.json();
      return data;

    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }

      // Handle network errors, JSON parsing errors, etc.
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new APIError(
          'Unable to connect to the backend. Please make sure the API server is running.',
          0
        );
      }

      throw new APIError(
        error instanceof Error ? error.message : 'An unexpected error occurred',
        0
      );
    }
  }

  async ingest(): Promise<{ indexed_docs: number; indexed_chunks: number; trace_id: string }> {
    const url = `${this.baseUrl}/ingest`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        let errorMessage = `Ingestion failed with status ${response.status}`;
        
        try {
          const errorData = await response.json();
          if (errorData.detail?.message) {
            errorMessage = errorData.detail.message;
          }
        } catch {
          // Use default message
        }

        throw new APIError(errorMessage, response.status);
      }

      const data = await response.json();
      return data;

    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }

      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new APIError('Unable to connect to the backend.', 0);
      }

      throw new APIError(
        error instanceof Error ? error.message : 'Ingestion failed',
        0
      );
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    const url = `${this.baseUrl}/healthz`;

    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new APIError(`Health check failed with status ${response.status}`, response.status);
      }

      return await response.json();

    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }

      throw new APIError('Backend is not accessible', 0);
    }
  }
}

// Default client instance
export const apiClient = new LifebloodAPIClient();

// Export for convenience
export { APIError };
