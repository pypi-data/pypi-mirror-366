import { useLocation, useNavigate } from "@solidjs/router";
import { createSignal, Show } from "solid-js";
import { MenuIcon, CloseIcon, DocumentIcon } from "./icons";
import { createStatusResource } from "../utils/api";

export default function NavigationSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = createSignal(false);
  
  // Get status for version info
  const { data: status } = createStatusResource();

  const navigationItems = [
    {
      id: "home",
      label: "Jobs",
      path: "/",
    },
    {
      id: "applications",
      label: "Serve Application",
      path: "/serve_applications",
    },
    {
      id: "plugin",
      label: "Plugin",
      path: "/plugin",
    }
  ];

  const isActive = (path) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setIsMobileMenuOpen(false); // Close mobile menu after navigation
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        class="lg:hidden fixed top-20 left-4 z-50 btn btn-sm btn-circle btn-ghost bg-white border border-slate-200 shadow-sm"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen())}
      >
        <Show when={!isMobileMenuOpen()}>
          <MenuIcon class="w-4 h-4" />
        </Show>
        <Show when={isMobileMenuOpen()}>
          <CloseIcon class="w-4 h-4" />
        </Show>
      </button>

      {/* Mobile Overlay */}
      <Show when={isMobileMenuOpen()}>
        <div 
          class="lg:hidden fixed inset-0 bg-black bg-opacity-30 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      </Show>

      {/* Sidebar */}
      <div class={`
        w-64 bg-white border-r border-slate-200 min-h-screen flex flex-col
        lg:relative lg:translate-x-0 lg:z-auto
        ${isMobileMenuOpen() 
          ? 'fixed inset-y-0 left-0 z-50 translate-x-0' 
          : 'fixed inset-y-0 left-0 z-50 -translate-x-full lg:translate-x-0'}
        transition-transform duration-300 ease-in-out
      `}>
      {/* Header */}
      <div class="p-6 border-b border-slate-200">
        <h2 class="text-xl font-bold text-slate-900">Synapse Devtools</h2>
        <p class="text-sm text-slate-600 mt-1">Development Environment</p>
      </div>

      {/* Navigation */}
      <nav class="flex-1 p-6 py-8 overflow-y-auto">
        <ul class="space-y-2">
          {navigationItems.map((item) => {
            const active = isActive(item.path);
            
            return (
              <li key={item.id}>
                <button
                  class={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                    active
                      ? "bg-slate-100 text-slate-900 font-medium"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                  onClick={() => handleNavigation(item.path)}
                >
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-medium">{item.label}</div>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer - Fixed at bottom */}
      <div class="flex-shrink-0 p-6 border-t border-slate-200 bg-white">
        <div class="text-xs text-slate-500">
          <div class="flex items-center justify-between">
            <span>SDK {status()?.devtools?.version || "Unknown"}</span>
            <a 
              href="https://docs.synapse.sh"
              target="_blank" 
              rel="noopener noreferrer"
              class="text-slate-600 hover:text-slate-900"
              title="Documentation"
            >
              <DocumentIcon class="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
      </div>
    </>
  );
}