import { Show, createSignal } from "solid-js";
import Prism from "prismjs";
import "prismjs/themes/prism.css";
import "prismjs/components/prism-json";
import "prismjs/components/prism-bash";
import "prismjs/components/prism-python";

export default function MessageViewer(props) {
  const [isExpanded, setIsExpanded] = createSignal(false);
  
  const message = () => props.message || '';
  const isLongMessage = () => message().length > 500;
  
  const displayMessage = () => {
    if (isExpanded() || !isLongMessage()) {
      return message();
    }
    return message().substring(0, 500) + '...';
  };
  
  const copyMessage = () => {
    navigator.clipboard.writeText(message()).then(() => {
      // Could add a toast notification here
    });
  };

  const formatMessage = (msg) => {
    if (!msg) return "";

    // Escape HTML first
    let formatted = msg
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
    if (msg.trim().match(/^\s*[{\[].*[}\]]\s*$/s)) {
      try {
        const trimmed = msg.trim();
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
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="message-url">$1</a>'
    );

    // Highlight file paths
    formatted = formatted.replace(
      /([a-zA-Z0-9_\-./]+\.(py|js|ts|vue|json|yaml|yml|txt|log|sh|md))/g,
      '<span class="message-filepath">$1</span>'
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

  // Check if message looks like JSON
  const isJsonMessage = () => {
    const trimmed = message().trim();
    return (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
           (trimmed.startsWith('[') && trimmed.endsWith(']'));
  };

  // Check if message looks like a stack trace
  const isStackTrace = () => {
    return message().includes('Traceback') || 
           message().includes('    at ') ||
           message().includes('File "') ||
           /^\s*File ".*", line \d+/.test(message());
  };

  const getMessageClass = () => {
    if (isStackTrace()) {
      return 'bg-red-50 border-red-200';
    } else if (isJsonMessage()) {
      return 'bg-slate-50 border-slate-200';
    } else {
      return 'bg-slate-50 border-slate-200';
    }
  };

  return (
    <div class={`message-viewer rounded-lg border overflow-hidden ${getMessageClass()}`}>
      <div class="relative">
        <div 
          class="message-content p-4 text-slate-900 whitespace-pre-wrap break-words max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100 font-mono text-sm leading-relaxed"
          innerHTML={formatMessage(displayMessage())}
        />
        
        <Show when={isLongMessage() && !isExpanded()}>
          <div class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent"></div>
        </Show>
      </div>
    </div>
  );
}