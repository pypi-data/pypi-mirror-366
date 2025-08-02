import { createSignal, createEffect, onCleanup } from "solid-js";

// API configuration
const getApiConfig = () => {
  const port = window.VITE_API_PORT || 8080;
  const host = window.VITE_API_HOST || "localhost";
  return {
    baseURL: `http://${host}:${port}`,
    headers: {
      'Content-Type': 'application/json',
    },
  };
};

// Generic API client
export class ApiClient {
  constructor() {
    this.config = getApiConfig();
  }

  async request(endpoint, options = {}) {
    const url = `${this.config.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.config.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return { data: await response.json(), error: null };
      } else {
        return { data: await response.text(), error: null };
      }
    } catch (error) {
      console.error('API request failed:', error);
      return { data: null, error: error.message };
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Singleton API client
export const apiClient = new ApiClient();

// Hook for API GET requests with automatic reactivity
export function createApiResource(endpoint, options = {}) {
  const [data, setData] = createSignal(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal(null);

  const fetchData = async () => {
    // Support function endpoints
    const resolvedEndpoint = typeof endpoint === 'function' ? endpoint() : endpoint;
    if (!resolvedEndpoint) {
      setLoading(false);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    const result = await apiClient.get(resolvedEndpoint);
    
    if (result.error) {
      setError(result.error);
      setData(null);
    } else {
      setData(result.data);
      setError(null);
    }
    
    setLoading(false);
  };

  // Auto-refresh functionality with reduced intervals
  let intervalId;
  if (options.autoRefresh && options.refreshInterval) {
    createEffect(() => {
      fetchData();
      intervalId = setInterval(fetchData, options.refreshInterval);
      
      onCleanup(() => {
        if (intervalId) clearInterval(intervalId);
      });
    });
  } else {
    createEffect(fetchData);
  }

  const refresh = () => fetchData();

  return {
    data,
    loading,
    error,
    refresh,
  };
}

// Hook for API mutations (POST, PUT, DELETE)
export function createApiMutation(mutationFn) {
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal(null);
  const [data, setData] = createSignal(null);

  const mutate = async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await mutationFn(...args);
      setData(result);
      setError(null);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    mutate,
    data,
    loading,
    error,
  };
}

// Jobs API
export function createJobsResource() {
  return createApiResource('/jobs', { 
    autoRefresh: true, 
    refreshInterval: 3000
  });
}

export function createJobResource(jobId) {
  return createApiResource(() => {
    const id = typeof jobId === 'function' ? jobId() : jobId;
    return id ? `/jobs/${id}` : null;
  });
}

// Applications API  
export function createApplicationsResource() {
  return createApiResource('/serve_applications', {
    autoRefresh: true,
    refreshInterval: 3000
  });
}

export function createApplicationResource(appId) {
  return createApiResource(() => {
    const id = typeof appId === 'function' ? appId() : appId;
    return id ? `/serve_applications/${id}` : null;
  });
}

// Status and health API
export function createStatusResource() {
  return createApiResource('/status');
}

export function createBackendHealthResource() {
  return createApiResource('/health/backend', {
    autoRefresh: true,
    refreshInterval: 5000
  });
}

export function createAgentHealthResource() {
  return createApiResource('/health/agent', {
    autoRefresh: true,
    refreshInterval: 5000
  });
}

export function createAuthTokenResource() {
  return createApiResource('/auth/token');
}

// User API - requires token and backend host
export async function fetchUserInfo(token, backendHost) {
  if (!token || !backendHost) return null;
  
  try {
    const response = await fetch(`${backendHost}/users/me/`, {
      method: 'GET',
      headers: {
        'Synapse-Access-Token': token,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const userData = await response.json();
      return {
        name: userData.name || userData.username || "Unknown",
        email: userData.email || "No email",
      };
    }
    return null;
  } catch (error) {
    console.error('Error fetching user info:', error);
    return null;
  }
}

// Plugin configuration API
export function createConfigResource() {
  return createApiResource('/config');
}

export function createConfigMutation() {
  return createApiMutation(async (config) => {
    // Ensure proper data structure for backend
    const configPayload = {
      config: config
    };
    
    const result = await apiClient.put('/config', configPayload);
    if (result.error) throw new Error(result.error);
    return result.data;
  });
}

// Plugin validation API
export function createValidationMutation() {
  return createApiMutation(async (config) => {
    // Ensure proper data structure for backend
    const configPayload = {
      config: config
    };
    
    const result = await apiClient.post('/config/validate', configPayload);
    if (result.error) throw new Error(result.error);
    return result.data;
  });
}

// Job log streaming
export function createJobLogsStream(jobId) {
  const [logs, setLogs] = createSignal([]);
  const [streaming, setStreaming] = createSignal(false);
  const [error, setError] = createSignal(null);

  let reader = null;

  const parseLogLine = (line) => {
    const timestampMatch = line.match(
      /^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})?)/
    );
    const levelMatch = line.match(
      /\[(ERROR|WARN|WARNING|INFO|DEBUG)\]|\b(ERROR|WARN|WARNING|INFO|DEBUG)\b/i
    );

    let timestamp = undefined;
    let level = undefined;
    let message = line;

    if (timestampMatch) {
      timestamp = timestampMatch[1];
      message = line.substring(timestampMatch[0].length).trim();
    }

    if (levelMatch) {
      level = (levelMatch[1] || levelMatch[2])?.toLowerCase();
      message = message.replace(
        /\[(ERROR|WARN|WARNING|INFO|DEBUG)\]|\b(ERROR|WARN|WARNING|INFO|DEBUG)\b/i,
        ""
      ).trim();
    }

    return { message, level, timestamp };
  };

  const startStreaming = async () => {
    if (streaming() || !jobId) return;

    try {
      setStreaming(true);
      setError(null);

      const config = getApiConfig();
      const response = await fetch(`${config.baseURL}/jobs/${jobId}/logs`);

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const decoder = new TextDecoder();
      reader = response.body.getReader();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          
          // Handle SSE format (data: prefix)
          if (line.startsWith('data: ')) {
            const content = line.substring(6).trim();
            
            // Check if this is an error message from the server
            if (content.includes('Agent client error') || 
                content.includes('Agent connection error') ||
                content.includes('Agent error:') ||
                content.includes('Unexpected error:')) {
              setError(content);
              // Still add as a log entry so user can see the error
              setLogs(prev => [...prev, parseLogLine(content)]);
            } else {
              // Normal log line
              setLogs(prev => [...prev, parseLogLine(content)]);
            }
          } else {
            // Handle non-SSE format (backward compatibility)
            setLogs(prev => [...prev, parseLogLine(line)]);
          }
        }
      }

      if (buffer.trim()) {
        setLogs(prev => [...prev, parseLogLine(buffer)]);
      }
    } catch (err) {
      setError(err.message);
      console.error("Error streaming logs:", err);
    } finally {
      setStreaming(false);
    }
  };

  const stopStreaming = () => {
    if (reader) {
      reader.cancel();
      reader = null;
    }
    setStreaming(false);
  };

  const clearLogs = () => {
    setLogs([]);
  };

  onCleanup(stopStreaming);

  return {
    logs,
    streaming,
    error,
    startStreaming,
    stopStreaming,
    clearLogs,
  };
}

// Utility functions
export function getJobStatusVariant(status) {
  switch (status?.toLowerCase()) {
    case "succeeded":
      return "success";
    case "failed":
    case "cancelled":
      return "error";
    case "running":
      return "info";
    case "pending":
      return "warning";
    default:
      return "default";
  }
}

export function formatTimestamp(timeStr) {
  if (!timeStr) return "N/A";
  try {
    const date = new Date(timeStr);
    return date.toLocaleString("sv-SE").replace("T", " ");
  } catch {
    return timeStr;
  }
}

export function formatJobDuration(startTime, endTime) {
  if (!startTime) return "N/A";

  const start = new Date(startTime);
  const end = endTime ? new Date(endTime) : new Date();
  const durationMs = end.getTime() - start.getTime();

  const seconds = Math.floor(durationMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}