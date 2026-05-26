'use client';

import React, { ReactNode, ReactElement } from 'react';

// ============================================================================
// ERROR BOUNDARY COMPONENT
// ============================================================================

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactElement;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback ? (
        this.props.fallback(this.state.error, this.reset)
      ) : (
        <DefaultErrorFallback error={this.state.error} onReset={this.reset} />
      );
    }

    return this.props.children;
  }
}

// ============================================================================
// DEFAULT ERROR FALLBACK
// ============================================================================

function DefaultErrorFallback({
  error,
  onReset,
}: {
  error: Error;
  onReset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">⚠️</div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Oops! Something went wrong
        </h1>
        <p className="text-slate-600 mb-2">{error.message}</p>
        <p className="text-xs text-slate-400 mb-6 font-mono bg-slate-50 p-2 rounded overflow-auto max-h-24">
          {error.stack}
        </p>
        <button
          onClick={onReset}
          className="w-full bg-sky-500 hover:bg-sky-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// API ERROR HANDLER
// ============================================================================

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export function createAPIError(
  response: Response,
  body: any
): APIError {
  const code = body?.detail?.code || `HTTP_${response.status}`;
  const message = body?.detail?.message || response.statusText;
  return new APIError(response.status, code, message);
}

// ============================================================================
// ERROR RETRY LOGIC
// ============================================================================

export interface RetryOptions {
  maxRetries?: number;
  delayMs?: number;
  backoffMultiplier?: number;
  onRetry?: (attempt: number, error: Error) => void;
}

export async function retryAsync<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    delayMs = 1000,
    backoffMultiplier = 2,
    onRetry,
  } = options;

  let lastError: Error = new Error('Unknown error');

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < maxRetries) {
        onRetry?.(attempt + 1, lastError);
        const delay = delayMs * Math.pow(backoffMultiplier, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

// ============================================================================
// SAFE ASYNC FUNCTION (with error handling)
// ============================================================================

export async function safeAsync<T, E = Error>(
  fn: () => Promise<T>
): Promise<[T | null, E | null]> {
  try {
    return [await fn(), null];
  } catch (error) {
    return [null, error as E];
  }
}

// ============================================================================
// HOOK: USE ASYNC WITH ERROR HANDLING
// ============================================================================

import { useState, useCallback, useEffect } from 'react';

export function useAsync<T, E = Error>(
  asyncFn: () => Promise<T>,
  immediate = true,
  dependencies: any[] = []
) {
  const [state, setState] = useState<{
    status: 'idle' | 'pending' | 'success' | 'error';
    data: T | null;
    error: E | null;
  }>({
    status: 'idle',
    data: null,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ status: 'pending', data: null, error: null });
    try {
      const response = await asyncFn();
      setState({ status: 'success', data: response, error: null });
      return response;
    } catch (error) {
      const err = error as E;
      setState({ status: 'error', data: null, error: err });
      throw err;
    }
  }, [asyncFn]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, ...dependencies]);

  return {
    execute,
    ...state,
    isLoading: state.status === 'pending',
    isSuccess: state.status === 'success',
    isError: state.status === 'error',
  };
}

// ============================================================================
// HOOK: USE FETCH WITH ERROR HANDLING
// ============================================================================

export function useFetch<T>(
  url: string,
  options?: RequestInit,
  skip = false
) {
  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (skip || !url) return;

    const controller = new AbortController();

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true }));
      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setState({ data, loading: false, error: null });
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          setState({
            data: null,
            loading: false,
            error,
          });
        }
      }
    };

    fetchData();

    return () => controller.abort();
  }, [url, skip, options]);

  return state;
}

// ============================================================================
// ERROR LOGGER
// ============================================================================

export interface ErrorLog {
  timestamp: string;
  message: string;
  stack?: string;
  context?: Record<string, any>;
  severity: 'error' | 'warning' | 'info';
}

const errorLogs: ErrorLog[] = [];

export function logError(
  error: Error,
  context?: Record<string, any>,
  severity: 'error' | 'warning' | 'info' = 'error'
) {
  const log: ErrorLog = {
    timestamp: new Date().toISOString(),
    message: error.message,
    stack: error.stack,
    context,
    severity,
  };

  errorLogs.push(log);

  // Keep only last 50 errors
  if (errorLogs.length > 50) {
    errorLogs.shift();
  }

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('[ErrorLog]', log);
  }

  // TODO: Send to error tracking service (Sentry, etc.)
}

export function getErrorLogs(): ErrorLog[] {
  return [...errorLogs];
}

export function clearErrorLogs() {
  errorLogs.length = 0;
}

// ============================================================================
// GLOBAL ERROR HANDLER
// ============================================================================

export function setupGlobalErrorHandler() {
  // Handle unhandled promise rejections
  if (typeof window !== 'undefined') {
    window.addEventListener('unhandledrejection', (event) => {
      logError(
        event.reason instanceof Error
          ? event.reason
          : new Error(String(event.reason)),
        { type: 'unhandledRejection' },
        'error'
      );
    });

    // Handle errors
    window.addEventListener('error', (event) => {
      logError(
        event.error instanceof Error
          ? event.error
          : new Error(event.message),
        { type: 'windowError' },
        'error'
      );
    });
  }
}
