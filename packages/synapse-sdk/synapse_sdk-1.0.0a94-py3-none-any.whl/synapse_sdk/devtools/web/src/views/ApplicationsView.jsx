import { Show, For } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { createApplicationsResource } from "../utils/api";
import { RefreshIcon, TrashIcon, CubeIcon } from "../components/icons";

export default function ApplicationsView() {
  const navigate = useNavigate();
  const { data: applications, loading, error, refresh } = createApplicationsResource();

  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case "RUNNING":
        return "badge-outline badge-success";
      case "DEPLOYING":
        return "badge-outline badge-info";
      case "DEPLOY_FAILED":
        return "badge-outline badge-error";
      case "DELETING":
        return "badge-outline badge-warning";
      default:
        return "badge-outline badge-neutral";
    }
  };

  const navigateToDetail = (appId) => {
    navigate(`/serve_application/${appId}`);
  };

  const deleteApplication = async (appId, appName) => {
    if (!confirm(`Are you sure you want to delete application "${appName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/serve_applications/${appId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        refresh(); // Refresh the list
      } else {
        alert('Failed to delete application');
      }
    } catch (error) {
      alert('Failed to delete application: ' + error.message);
    }
  };

  return (
    <div class="p-6">
      {/* Header */}
      <div class="mb-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-semibold text-slate-900 mb-1">Serve Applications</h1>
            <p class="text-sm text-slate-600">
              Monitor and manage Ray Serve applications
            </p>
          </div>
          
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2 text-sm text-slate-500">
              <RefreshIcon class="w-4 h-4 animate-spin" />
              <span>Auto (3s)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Card */}
      <div class="card bg-white shadow-professional">
        <div class="card-body p-6">
          {/* Card Header */}
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-slate-900">
              Applications ({applications()?.length || 0})
            </h2>
            <button 
              class="btn btn-sm btn-ghost" 
              onClick={refresh}
              disabled={loading()}
            >
              <RefreshIcon class="w-4 h-4" />
              Refresh
            </button>
          </div>

          {/* Error Alert */}
          <Show when={error()}>
            <div class="alert alert-error mb-4">
              <div>
                <h3 class="font-medium">Error loading applications</h3>
                <div class="text-sm">{error()}</div>
              </div>
            </div>
          </Show>

          {/* Loading State */}
          <Show when={loading() && (!applications() || applications().length === 0)}>
            <div class="flex flex-col items-center justify-center py-12">
              <div class="loading loading-spinner loading-md mb-4"></div>
              <p class="text-slate-500">Loading applications...</p>
            </div>
          </Show>

          {/* Empty State */}
          <Show when={!loading() && (!applications() || applications().length === 0) && !error()}>
            <div class="flex flex-col items-center justify-center py-12">
              <div class="text-slate-400 mb-4">
                <CubeIcon class="w-16 h-16" />
              </div>
              <h3 class="text-lg font-medium text-slate-900 mb-2">No applications found</h3>
              <p class="text-slate-500">Serve applications will appear here once deployed</p>
            </div>
          </Show>

          {/* Applications Table */}
          <Show when={applications() && applications().length > 0}>
            <div class="overflow-x-auto">
              <table class="table table-sm w-full">
                <thead>
                  <tr class="border-slate-200">
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Application</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Status</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Route Prefix</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Deployments</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Last Updated</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <For each={applications()}>
                    {(app) => (
                      <tr 
                        class="hover:bg-slate-50 cursor-pointer border-slate-100"
                        onClick={() => navigateToDetail(app.name)}
                      >
                        <td class="py-3">
                          <div class="flex flex-col">
                            <span class="font-medium text-slate-900">{app.name}</span>
                            <span class="text-sm text-slate-500">
                              {app.docs_path ? `Docs: ${app.docs_path}` : 'No docs path'}
                            </span>
                          </div>
                        </td>
                        <td>
                          <span class={`badge badge-sm ${getStatusClass(app.status)}`}>
                            {app.status}
                          </span>
                        </td>
                        <td>
                          <code class="text-sm bg-slate-100 px-2 py-1 rounded">
                            {app.route_prefix || '/'}
                          </code>
                        </td>
                        <td>
                          <span class="text-sm text-slate-700">
                            {app.deployments?.length || 0} deployment{(app.deployments?.length || 0) !== 1 ? 's' : ''}
                          </span>
                        </td>
                        <td class="text-sm text-slate-600">
                          {app.last_deployed_time_s 
                            ? new Date(app.last_deployed_time_s * 1000).toLocaleString()
                            : 'N/A'
                          }
                        </td>
                        <td>
                          <div class="flex gap-2" onClick={(e) => e.stopPropagation()}>
                            <button
                              class="btn btn-sm btn-ghost"
                              onClick={() => navigateToDetail(app.name)}
                              title="View details"
                            >
                              View
                            </button>
                            <button
                              class="btn btn-sm btn-ghost text-red-600 hover:bg-red-50"
                              onClick={() => deleteApplication(app.name, app.name)}
                              title="Delete application"
                            >
                              <TrashIcon class="w-3 h-3" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </For>
                </tbody>
              </table>
            </div>
          </Show>
        </div>
      </div>

      {/* Summary Stats */}
      <Show when={applications() && applications().length > 0}>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Total Applications</div>
            <div class="stat-value text-lg text-slate-900">{applications().length}</div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Running</div>
            <div class="stat-value text-lg text-emerald-600">
              {applications().filter(app => app.status === "RUNNING").length}
            </div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Deploying</div>
            <div class="stat-value text-lg text-blue-600">
              {applications().filter(app => app.status === "DEPLOYING").length}
            </div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Failed</div>
            <div class="stat-value text-lg text-red-600">
              {applications().filter(app => app.status === "DEPLOY_FAILED").length}
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}