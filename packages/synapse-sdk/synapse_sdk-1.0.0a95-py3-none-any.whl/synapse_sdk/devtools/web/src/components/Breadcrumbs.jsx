import { For, Show } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { HomeIcon, ArrowLeftIcon } from "./icons";

export default function Breadcrumbs(props) {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <div class="flex items-center gap-2 text-sm text-slate-600 mb-4">
      <button
        class="flex items-center gap-1 hover:text-slate-900 transition-colors"
        onClick={() => handleNavigation("/")}
      >
        <HomeIcon class="w-4 h-4" />
        <span>Home</span>
      </button>
      
      <For each={props.items}>
        {(item, index) => (
          <>
            <ArrowLeftIcon class="w-3 h-3 rotate-180 text-slate-400" />
            <Show when={item.path && index() < props.items.length - 1}>
              <button
                class="hover:text-slate-900 transition-colors"
                onClick={() => handleNavigation(item.path)}
              >
                {item.label}
              </button>
            </Show>
            <Show when={!item.path || index() === props.items.length - 1}>
              <span class="text-slate-900 font-medium">{item.label}</span>
            </Show>
          </>
        )}
      </For>
    </div>
  );
}