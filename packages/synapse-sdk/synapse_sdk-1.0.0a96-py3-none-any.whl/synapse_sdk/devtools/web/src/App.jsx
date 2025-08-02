import { AppRouter } from "./router";
import ServerStatusBar from "./components/ServerStatusBar";
import "./index.css";

function App() {
  return (
    <div class="min-h-screen bg-slate-50" data-theme="professional">
      <ServerStatusBar />
      <AppRouter />
    </div>
  );
}

export default App;