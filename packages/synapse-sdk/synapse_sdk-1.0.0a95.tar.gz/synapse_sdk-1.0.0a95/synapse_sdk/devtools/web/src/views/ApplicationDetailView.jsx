import { Show, For, createMemo } from "solid-js";
import { useParams, useNavigate } from "@solidjs/router";
import { createApplicationResource, formatTimestamp } from "../utils/api";
import { ArrowLeftIcon, RefreshIcon, CubeIcon } from "../components/icons";
import Breadcrumbs from "../components/Breadcrumbs";

export default function ApplicationDetailView() {
  const params = useParams();
  const navigate = useNavigate();

  const appId = () => params.id;
  const { data, loading, error, refresh } = createApplicationResource(() => appId());

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

  const hasDeployments = createMemo(() => 
    data()?.deployments && data().deployments.length > 0
  );

  return (
    <div class="p-6">
      {/* Breadcrumbs */}
      <Breadcrumbs 
        items={[
          { label: "Serve Apps", path: "/serve_applications" },
          { label: data()?.name || appId() || "Application Details" }
        ]} 
      />

      {/* Header */}
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-4">
          <button 
            class="btn btn-sm btn-outline"
            onClick={() => navigate(-1)}
          >
            <ArrowLeftIcon class="w-4 h-4 mr-2" />
            Back
          </button>
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">Application Details</h1>
            <p class="text-sm text-slate-600">View serve application details and deployments</p>
          </div>
        </div>
        <button 
          class="btn btn-sm btn-primary"
          onClick={refresh}
          disabled={loading()}
        >
          <RefreshIcon class="w-4 h-4 mr-2" />
          {loading() ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* Error State */}
      <Show when={error()}>
        <div class="alert alert-error mb-6">
          <div>
            <h3 class="font-medium">Failed to load application details</h3>
            <div class="text-sm">{error()}</div>
          </div>
        </div>
      </Show>

      {/* Loading State */}
      <Show when={loading() && !data()}>
        <div class="flex flex-col items-center justify-center py-12">
          <div class="loading loading-spinner loading-lg mb-4"></div>
          <p class="text-slate-500">Loading application details...</p>
        </div>
      </Show>

      {/* Application Not Found */}
      <Show when={!loading() && !data() && !error()}>
        <div class="flex flex-col items-center justify-center py-12">
          <div class="text-slate-400 mb-4">
            <CubeIcon class="w-16 h-16" />
          </div>
          <h3 class="text-lg font-medium text-slate-900 mb-2">Application not found</h3>
          <p class="text-slate-500">The requested application could not be found</p>
        </div>
      </Show>

      {/* Application Details */}
      <Show when={data()}>
        <div class="space-y-6">
          {/* Application Overview */}
          <div class="card bg-white shadow-professional">
            <div class="card-body p-6">
              <h2 class="text-lg font-semibold text-slate-900 mb-4">Overview</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Application Name
                  </div>
                  <div class="font-medium text-slate-900">
                    {data().name}
                  </div>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Status
                  </div>
                  <span class={`badge badge-sm ${getStatusClass(data().status)}`}>
                    {data().status}
                  </span>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Route Prefix
                  </div>
                  <code class="text-sm bg-slate-200 px-2 py-1 rounded">
                    {data().route_prefix || '/'}
                  </code>
                </div>

                <Show when={data().docs_path}>
                  <div class="bg-slate-50 p-4 rounded-lg">
                    <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                      Docs Path
                    </div>
                    <code class="text-sm text-slate-700">
                      {data().docs_path}
                    </code>
                  </div>
                </Show>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Deployments
                  </div>
                  <div class="text-sm text-slate-700">
                    {data().deployments?.length || 0} deployment{(data().deployments?.length || 0) !== 1 ? 's' : ''}
                  </div>
                </div>

                <Show when={data().last_deployed_time_s}>
                  <div class="bg-slate-50 p-4 rounded-lg">
                    <div class="text-xs font-medium text-slate-600 uppercase tracking-wide mb-1">
                      Last Deployed
                    </div>
                    <div class="text-sm text-slate-700">
                      {new Date(data().last_deployed_time_s * 1000).toLocaleString()}
                    </div>
                  </div>
                </Show>
              </div>
            </div>
          </div>

          {/* Deployments */}
          <Show when={hasDeployments()}>
            <div class="card bg-white shadow-professional">
              <div class="card-body p-6">
                <h2 class="text-lg font-semibold text-slate-900 mb-4">Deployments</h2>
                
                <div class="overflow-x-auto">
                  <table class="table table-xs w-full">
                    <thead>
                      <tr class="border-slate-200">
                        <th class="bg-slate-50 text-slate-600 font-medium text-xs">Name</th>
                        <th class="bg-slate-50 text-slate-600 font-medium text-xs">Status</th>
                        <th class="bg-slate-50 text-slate-600 font-medium text-xs">Replicas</th>
                        <th class="bg-slate-50 text-slate-600 font-medium text-xs">Route Prefix</th>
                        <th class="bg-slate-50 text-slate-600 font-medium text-xs">Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      <For each={data().deployments}>
                        {(deployment) => (
                          <tr class="border-slate-100">
                            <td class="py-3">
                              <span class="font-medium text-slate-900">{deployment.name}</span>
                            </td>
                            <td>
                              <span class={`badge badge-sm ${getStatusClass(deployment.status)}`}>
                                {deployment.status}
                              </span>
                            </td>
                            <td>
                              <div class="flex items-center gap-2">
                                <span class="text-sm">{deployment.replica_count || 0}</span>
                                <Show when={deployment.target_replica_count !== deployment.replica_count}>
                                  <span class="text-xs text-slate-500">
                                    → {deployment.target_replica_count}
                                  </span>
                                </Show>
                              </div>
                            </td>
                            <td>
                              <code class="text-xs bg-slate-100 px-2 py-1 rounded">
                                {deployment.route_prefix || '/'}
                              </code>
                            </td>
                            <td class="max-w-xs">
                              <div class="truncate text-sm text-slate-600">
                                {deployment.message || '—'}
                              </div>
                            </td>
                          </tr>
                        )}
                      </For>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </Show>

          {/* Raw Application Data */}
          <div class="card bg-white shadow-professional">
            <div class="card-body p-6">
              <h2 class="text-lg font-semibold text-slate-900 mb-4">Raw Data</h2>
              <div class="bg-slate-50 p-4 rounded-lg">
                <pre class="text-xs text-slate-700 overflow-auto max-h-96">
                  {JSON.stringify(data(), null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}