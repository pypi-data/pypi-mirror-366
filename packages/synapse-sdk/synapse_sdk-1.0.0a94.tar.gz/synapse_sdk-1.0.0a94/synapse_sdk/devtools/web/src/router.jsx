import { Router, Route } from "@solidjs/router";
import { lazy } from "solid-js";
import Layout from "./components/Layout";

// Lazy load views for better performance
const HomeView = lazy(() => import("./views/HomeView"));
const JobDetailView = lazy(() => import("./views/JobDetailView"));
const PluginView = lazy(() => import("./views/PluginView"));
const ApplicationsView = lazy(() => import("./views/ApplicationsView"));
const ApplicationDetailView = lazy(() => import("./views/ApplicationDetailView"));

export function AppRouter(props) {
  return (
    <Router>
      <Route path="/" component={() => <Layout><HomeView /></Layout>} />
      <Route path="/job/:id" component={() => <Layout><JobDetailView /></Layout>} />
      <Route path="/plugin" component={() => <Layout><PluginView /></Layout>} />
      <Route path="/serve_applications" component={() => <Layout><ApplicationsView /></Layout>} />
      <Route path="/serve_application/:id" component={() => <Layout><ApplicationDetailView /></Layout>} />
      
      {/* Legacy redirects */}
      <Route path="/applications" component={() => {
        window.location.replace("/serve_applications");
        return null;
      }} />
      <Route path="/config" component={() => {
        window.location.replace("/plugin");
        return null;
      }} />
      
      {props.children}
    </Router>
  );
}