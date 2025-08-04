import { Show, For, createSignal, createEffect, onMount, onCleanup } from "solid-js";
import { createJobLogsStream } from "../utils/api";
import Prism from "prismjs";
import "prismjs/themes/prism-tomorrow.css";

export default function LogViewer(props) {
  const [autoScroll, setAutoScroll] = createSignal(true);
  const [highlightedLine, setHighlightedLine] = createSignal(null);
  
  let logContainerRef;
  
  const { 
    logs, 
    streaming, 
    error, 
    startStreaming, 
    stopStreaming, 
    clearLogs 
  } = createJobLogsStream(props.submissionId);

  // Auto-scroll functionality
  createEffect(() => {
    if (autoScroll() && logContainerRef && logs().length > 0) {
      logContainerRef.scrollTop = logContainerRef.scrollHeight;
    }
  });

  // Check if user scrolled up manually
  const handleScroll = () => {
    if (!logContainerRef) return;
    
    const { scrollTop, scrollHeight, clientHeight } = logContainerRef;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
    
    if (autoScroll() && !isAtBottom) {
      setAutoScroll(false);
    }
  };

  const toggleAutoScroll = () => {
    setAutoScroll(!autoScroll());
    if (autoScroll()) {
      scrollToBottom();
    }
  };

  const scrollToBottom = () => {
    if (logContainerRef) {
      logContainerRef.scrollTop = logContainerRef.scrollHeight;
    }
  };

  const copyLogs = () => {
    const logText = logs()
      .map(log => {
        const timestamp = log.timestamp ? `[${formatTimestamp(log.timestamp)}] ` : '';
        const level = log.level ? `[${log.level.toUpperCase()}] ` : '';
        return `${timestamp}${level}${log.message}`;
      })
      .join('\n');
    
    navigator.clipboard.writeText(logText).then(() => {
      // Could add a toast notification here
    });
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return timestamp;
    }
  };

  const formatLogMessage = (message) => {
    // Escape HTML first
    let formatted = message
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Handle ANSI escape codes and convert to HTML
    formatted = formatted
      // Reset
      .replace(/\x1b\[0m/g, "</span>")
      // Colors
      .replace(/\x1b\[31m/g, '<span class="ansi-red">')
      .replace(/\x1b\[32m/g, '<span class="ansi-green">')
      .replace(/\x1b\[33m/g, '<span class="ansi-yellow">')
      .replace(/\x1b\[34m/g, '<span class="ansi-blue">')
      .replace(/\x1b\[35m/g, '<span class="ansi-magenta">')
      .replace(/\x1b\[36m/g, '<span class="ansi-cyan">')
      .replace(/\x1b\[37m/g, '<span class="ansi-white">')
      .replace(/\x1b\[90m/g, '<span class="ansi-gray">')
      .replace(/\x1b\[91m/g, '<span class="ansi-bright-red">')
      .replace(/\x1b\[92m/g, '<span class="ansi-bright-green">')
      .replace(/\x1b\[93m/g, '<span class="ansi-bright-yellow">')
      .replace(/\x1b\[94m/g, '<span class="ansi-bright-blue">')
      .replace(/\x1b\[95m/g, '<span class="ansi-bright-magenta">')
      .replace(/\x1b\[96m/g, '<span class="ansi-bright-cyan">')
      .replace(/\x1b\[97m/g, '<span class="ansi-bright-white">')
      // Bold
      .replace(/\x1b\[1m/g, '<span class="ansi-bold">')
      // Remove any remaining ANSI codes
      .replace(/\x1b\[[0-9;]*m/g, "");

    // Try to detect and highlight JSON
    if (message.trim().match(/^\s*[{\[].*[}\]]\s*$/s)) {
      try {
        const trimmed = message.trim();
        const parsed = JSON.parse(trimmed);
        const jsonString = JSON.stringify(parsed, null, 2);
        formatted = Prism.highlight(jsonString, Prism.languages.json, "json");
      } catch {
        // Not valid JSON, continue with original formatting
      }
    }

    // Highlight URLs
    formatted = formatted.replace(
      /(https?:\/\/[^\s<>&"']+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="log-url">$1</a>'
    );

    // Highlight file paths
    formatted = formatted.replace(
      /([a-zA-Z0-9_\-./]+\.(py|js|ts|vue|json|yaml|yml|txt|log|sh|md))/g,
      '<span class="log-filepath">$1</span>'
    );

    // Highlight common patterns
    formatted = formatted
      // Error patterns
      .replace(
        /\b(ERROR|FATAL|EXCEPTION|TRACEBACK)\b/gi,
        '<span class="pattern-error">$1</span>'
      )
      // Warning patterns
      .replace(
        /\b(WARNING|WARN|DEPRECATED)\b/gi,
        '<span class="pattern-warning">$1</span>'
      )
      // Success patterns
      .replace(
        /\b(SUCCESS|PASSED|OK|COMPLETE)\b/gi,
        '<span class="pattern-success">$1</span>'
      )
      // Info patterns
      .replace(
        /\b(INFO|DEBUG|TRACE)\b/gi,
        '<span class="pattern-info">$1</span>'
      );

    return formatted;
  };

  const getLogLevelClass = (level) => {
    if (!level) return "";

    switch (level.toLowerCase()) {
      case "error":
        return "log-level-error";
      case "warn":
      case "warning":
        return "log-level-warn";
      case "info":
        return "log-level-info";
      case "debug":
        return "log-level-debug";
      default:
        return "";
    }
  };

  const highlightLine = (index) => {
    setHighlightedLine(highlightedLine() === index ? null : index);
  };

  onMount(() => {
    startStreaming();
  });

  onCleanup(() => {
    stopStreaming();
  });

  return (
    <div class="github-log-viewer">
      {/* Header */}
      <div class="log-header">
        <div class="log-title">
          <svg class="octicon" viewBox="0 0 16 16" width="16" height="16">
            <path d="M8 16a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2c.55 0 1.02.26 1.3.62.27.35.7.38 1.1.38.4 0 .83-.03 1.1-.38.28-.36.75-.62 1.3-.62a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H8z" />
          </svg>
          <span>Logs</span>
        </div>
        <div class="log-controls">
          <button
            onClick={toggleAutoScroll}
            class={`control-btn ${autoScroll() ? 'active' : ''}`}
          >
            Auto-scroll
          </button>
          <button onClick={clearLogs} class="control-btn">Clear</button>
          <button onClick={copyLogs} class="control-btn">Copy</button>
        </div>
      </div>

      {/* Error State */}
      <Show when={error()}>
        <div class="alert alert-error mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error()}</span>
        </div>
      </Show>

      {/* Container */}
      <div class="log-container" ref={logContainerRef} onScroll={handleScroll}>
        <Show when={logs().length === 0 && !error()}>
          <div class="log-empty">
            <div class="empty-state">
              <svg class="empty-icon" viewBox="0 0 24 24" width="24" height="24">
                <path d="M3 3v18h18V3H3zm16 16H5V5h14v14zM7 7h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z" />
              </svg>
              <p>No logs available</p>
              <p class="empty-subtitle">Logs will appear here when available</p>
            </div>
          </div>
        </Show>
        
        <Show when={logs().length > 0}>
          <div class="log-content">
            <For each={logs()}>
              {(log, index) => (
                <div
                  class={`log-line ${getLogLevelClass(log.level)} ${
                    highlightedLine() === index() ? 'highlighted' : ''
                  }`}
                  onClick={() => highlightLine(index())}
                >
                  <span class="line-number">{index() + 1}</span>
                  <Show when={log.timestamp}>
                    <span class="log-timestamp">
                      {formatTimestamp(log.timestamp)}
                    </span>
                  </Show>
                  <Show when={log.level}>
                    <span class="log-level-badge">
                      {log.level.toUpperCase().charAt(0)}
                    </span>
                  </Show>
                  <span class="log-message" innerHTML={formatLogMessage(log.message)} />
                </div>
              )}
            </For>
          </div>
        </Show>
      </div>

      {/* Footer */}
      <div class="log-footer">
        <span class="log-count">{logs().length} lines</span>
        <Show when={streaming()}>
          <span class="streaming-status">
            <div class="streaming-dot"></div>
            Streaming...
          </span>
        </Show>
      </div>
    </div>
  );
}