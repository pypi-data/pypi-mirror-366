import { createSignal, createEffect, onCleanup, Show } from "solid-js";
import { createStatusResource, fetchUserInfo } from "../utils/api";
import { StatusIcon, RefreshIcon, CheckIcon, AlertCircleIcon } from "./icons";

export default function ServerStatusBar() {
  const [user, setUser] = createSignal(null);
  const [backendHealth, setBackendHealth] = createSignal({ status: "checking" });
  const [agentHealth, setAgentHealth] = createSignal({ status: "checking" });
  const [isManualRefresh, setIsManualRefresh] = createSignal(false);

  // Get status data for version and config info
  const { data: status } = createStatusResource();

  const checkBackendStatus = async () => {
    try {
      const response = await fetch("/health/backend");
      if (response.ok) {
        const healthData = await response.json();
        setBackendHealth({
          status: healthData.status,
          latency: healthData.latency,
          url: healthData.url,
          httpStatus: healthData.httpStatus,
          error: healthData.error
        });
      } else {
        setBackendHealth({
          status: "down",
          error: `HTTP ${response.status}: ${response.statusText}`
        });
      }
    } catch (error) {
      setBackendHealth({
        status: "down",
        error: `Connection failed: ${error.message}`
      });
    }
  };

  const checkAgentStatus = async () => {
    try {
      const response = await fetch("/health/agent");
      if (response.ok) {
        const healthData = await response.json();
        setAgentHealth({
          status: healthData.status,
          latency: healthData.latency,
          url: healthData.url,
          httpStatus: healthData.httpStatus,
          error: healthData.error
        });
      } else {
        setAgentHealth({
          status: "down",
          error: `HTTP ${response.status}: ${response.statusText}`
        });
      }
    } catch (error) {
      setAgentHealth({
        status: "down",
        error: `Connection failed: ${error.message}`
      });
    }
  };

  const checkStatus = async () => {
    setIsManualRefresh(false);
    await Promise.all([checkBackendStatus(), checkAgentStatus()]);
  };

  const manualRefresh = async () => {
    setIsManualRefresh(true);
    await checkStatus();
  };

  const initializeAuth = async () => {
    try {
      // Get token from devtools server
      const tokenResponse = await fetch("/auth/token");
      if (tokenResponse.ok) {
        const tokenData = await tokenResponse.json();
        
        if (tokenData.token) {
          // Get backend host from status
          const statusData = status();
          if (statusData?.backend?.host) {
            // Fetch user info using token and backend host
            const userInfo = await fetchUserInfo(tokenData.token, statusData.backend.host);
            if (userInfo) {
              setUser(userInfo);
            }
          } else {
            console.warn("No backend host configured for authentication");
          }
        }
      }
    } catch (error) {
      console.error("Error initializing auth:", error);
    }
  };

  const getStatusIcon = (health) => {
    switch (health.status) {
      case "healthy":
        return <div class="w-2 h-2 rounded-full bg-emerald-500"></div>;
      case "down":
        return <div class="w-2 h-2 rounded-full bg-red-500"></div>;
      case "checking":
        return <div class="loading loading-spinner loading-sm"></div>;
      default:
        return <div class="w-2 h-2 rounded-full bg-slate-400"></div>;
    }
  };

  const getStatusText = (health) => {
    switch (health.status) {
      case "healthy":
        return "Online";
      case "down":
        return "Offline";
      case "checking":
        return "Checking...";
      default:
        return "Unknown";
    }
  };

  const getHostFromUrl = (url) => {
    if (!url) return "";
    try {
      const urlObj = new URL(url);
      return urlObj.hostname + (urlObj.port ? `:${urlObj.port}` : "");
    } catch {
      return url;
    }
  };

  // Initialize auth when status is available
  createEffect(() => {
    if (status()) {
      initializeAuth();
    }
  });

  // Check status immediately and every 60 seconds (reduced polling)
  createEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    onCleanup(() => clearInterval(interval));
  });

  return (
    <div class="bg-white border-b border-slate-200 px-6 py-3">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-8">
          {/* Backend Status */}
          <div class="flex items-center gap-3">
            {getStatusIcon(backendHealth())}
            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-slate-800">Backend</span>
                <span class="text-sm text-slate-600">{getStatusText(backendHealth())}</span>
                <Show when={backendHealth().latency}>
                  <span class="text-sm text-slate-500">({backendHealth().latency}ms)</span>
                </Show>
              </div>
              <div class="text-sm text-slate-500">
                <Show when={backendHealth().url}>
                  <span>{getHostFromUrl(backendHealth().url)}</span>
                </Show>
                <Show when={backendHealth().httpStatus}>
                  <span class="ml-2">[HTTP {backendHealth().httpStatus}]</span>
                </Show>
                <Show when={backendHealth().error}>
                  <span class="ml-2 text-red-500">{backendHealth().error}</span>
                </Show>
              </div>
            </div>
          </div>

          {/* Agent Status */}
          <div class="flex items-center gap-3">
            {getStatusIcon(agentHealth())}
            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-slate-800">Agent</span>
                <span class="text-sm text-slate-600">{getStatusText(agentHealth())}</span>
                <Show when={agentHealth().latency}>
                  <span class="text-sm text-slate-500">({agentHealth().latency}ms)</span>
                </Show>
                <Show when={status()?.agent?.name}>
                  <span class="text-sm text-blue-600">[{status().agent.name}]</span>
                </Show>
              </div>
              <div class="text-sm text-slate-500">
                <Show when={status()?.agent?.id}>
                  <span>(ID: {status().agent.id})</span>
                </Show>
                <Show when={agentHealth().url}>
                  <span>{getHostFromUrl(agentHealth().url)}</span>
                </Show>
                <Show when={agentHealth().httpStatus}>
                  <span class="ml-2">[{agentHealth().httpStatus}]</span>
                </Show>
              </div>
            </div>
          </div>
          
          <button 
            class="btn btn-sm btn-ghost"
            onClick={manualRefresh}
            disabled={isManualRefresh()}
            title="Refresh status"
          >
            <Show when={!isManualRefresh()}>
              <RefreshIcon class="w-3 h-3" />
            </Show>
            <Show when={isManualRefresh()}>
              <div class="loading loading-spinner loading-sm"></div>
            </Show>
          </button>
        </div>
        
        <div class="flex items-center gap-4">
          {/* User Info */}
          <Show when={user()}>
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 bg-slate-200 rounded-full flex items-center justify-center">
                <span class="text-sm font-medium text-slate-600">
                  {user().name.charAt(0).toUpperCase()}
                </span>
              </div>
              <span class="text-sm font-medium text-slate-700">
                {user().name} ({user().email})
              </span>
            </div>
          </Show>
          <Show when={!user()}>
            <span class="text-sm text-amber-600">Not authenticated</span>
          </Show>
        </div>
      </div>
    </div>
  );
}