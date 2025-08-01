import { Show, createSignal, createMemo, onMount } from "solid-js";
import { useParams, useNavigate } from "@solidjs/router";
import { createJobResource, createJobLogsStream, formatTimestamp } from "../utils/api";
import { ArrowLeftIcon, RefreshIcon, EyeIcon } from "../components/icons";
import LogViewer from "../components/LogViewer";
import MessageViewer from "../components/MessageViewer";
import Breadcrumbs from "../components/Breadcrumbs";

export default function JobDetailView() {
  const params = useParams();
  const navigate = useNavigate();
  const [showRuntimeEnvModal, setShowRuntimeEnvModal] = createSignal(false);

  const submissionId = () => params.id;
  const { data, loading, error, refresh } = createJobResource(() => submissionId());

  // Computed properties
  const hasRuntimeEnv = createMemo(() => 
    data()?.runtime_env && Object.keys(data().runtime_env).length > 0
  );
  
  const hasMessage = createMemo(() => 
    data()?.message && data().message.trim().length > 0
  );
  
  const hasDriverInfo = createMemo(() => 
    data()?.driver_info && Object.keys(data().driver_info).length > 0
  );
  
  const hasMetadata = createMemo(() => 
    data()?.metadata && Object.keys(data().metadata).length > 0
  );

  const getStatusBadgeClass = (status) => {
    switch (status?.toUpperCase()) {
      case "SUCCEEDED":
        return "badge-outline badge-success";
      case "FAILED":
      case "CANCELLED":
        return "badge-outline badge-error";
      case "RUNNING":
        return "badge-outline badge-info";
      case "PENDING":
        return "badge-outline badge-warning";
      default:
        return "badge-outline badge-neutral";
    }
  };

  return (
    <div class="p-6">
      {/* Breadcrumbs */}
      <Breadcrumbs 
        items={[
          { label: "Jobs", path: "/" },
          { label: data()?.job_id || submissionId() || "Job Details" }
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
            <h1 class="text-2xl font-semibold text-slate-900">Job Details</h1>
            <p class="text-sm text-slate-600">View job execution details and logs</p>
          </div>
        </div>
        {/* Refresh button removed as requested */}
      </div>

      {/* Error State */}
      <Show when={error()}>
        <div class="alert alert-error mb-6">
          <div>
            <h3 class="font-medium">Failed to load job details</h3>
            <div class="text-sm">{error()}</div>
          </div>
        </div>
      </Show>

      {/* Loading State */}
      <Show when={loading() && !data()}>
        <div class="flex flex-col items-center justify-center py-12">
          <div class="loading loading-spinner loading-lg mb-4"></div>
          <p class="text-slate-500">Loading job details...</p>
        </div>
      </Show>

      {/* Job Not Found */}
      <Show when={!loading() && !data() && !error()}>
        <div class="flex flex-col items-center justify-center py-12">
          <div class="text-slate-400 mb-4">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-slate-900 mb-2">Job not found</h3>
          <p class="text-slate-500">The requested job could not be found</p>
        </div>
      </Show>

      {/* Job Details */}
      <Show when={data()}>
        <div class="space-y-6">
          {/* Job Overview */}
          <div class="card bg-white shadow-professional">
            <div class="card-body p-6">
              <h2 class="text-lg font-semibold text-slate-900 mb-4">Overview</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Submission ID
                  </div>
                  <div class="font-mono text-sm text-blue-600 font-medium">
                    {data().submission_id}
                  </div>
                </div>

                <Show when={data().job_id}>
                  <div class="bg-slate-50 p-4 rounded-lg">
                    <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                      Job ID
                    </div>
                    <div class="font-mono text-sm text-slate-700">
                      {data().job_id}
                    </div>
                  </div>
                </Show>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Type
                  </div>
                  <div class="font-mono text-sm text-slate-700">
                    {data().type}
                  </div>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Status
                  </div>
                  <span class={`badge badge-sm ${getStatusBadgeClass(data().status)}`}>
                    {data().status}
                  </span>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                    Start Time
                  </div>
                  <div class="text-sm text-slate-700">
                    {formatTimestamp(data().start_time)}
                  </div>
                </div>

                <div class="bg-slate-50 p-4 rounded-lg">
                  <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                    End Time
                  </div>
                  <div class="text-sm text-slate-700">
                    {formatTimestamp(data().end_time)}
                  </div>
                </div>

                <Show when={hasRuntimeEnv()}>
                  <div class="bg-slate-50 p-4 rounded-lg">
                    <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                      Runtime Environment
                    </div>
                    <button 
                      class="btn btn-sm btn-ghost"
                      onClick={() => setShowRuntimeEnvModal(true)}
                    >
                      <EyeIcon class="w-3 h-3 mr-1" />
                      View Details
                    </button>
                  </div>
                </Show>
              </div>
            </div>
          </div>

          {/* Message/Error Details */}
          <Show when={hasMessage()}>
            <div class="card bg-white shadow-professional">
              <div class="card-body p-6">
                <h2 class="text-lg font-semibold text-slate-900 mb-4">Message</h2>
                <MessageViewer message={data().message} />
              </div>
            </div>
          </Show>

          {/* Driver Information */}
          <Show when={hasDriverInfo()}>
            <div class="card bg-white shadow-professional">
              <div class="card-body p-6">
                <h2 class="text-lg font-semibold text-slate-900 mb-4">Driver Information</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <Show when={data().driver_node_id}>
                    <div class="bg-slate-50 p-4 rounded-lg">
                      <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                        Node ID
                      </div>
                      <div class="font-mono text-sm text-slate-700">
                        {data().driver_node_id}
                      </div>
                    </div>
                  </Show>
                  
                  <Show when={data().driver_agent_http_address}>
                    <div class="bg-slate-50 p-4 rounded-lg">
                      <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                        HTTP Address
                      </div>
                      <div class="font-mono text-sm text-slate-700">
                        {data().driver_agent_http_address}
                      </div>
                    </div>
                  </Show>
                  
                  <Show when={data().driver_exit_code !== null}>
                    <div class="bg-slate-50 p-4 rounded-lg">
                      <div class="text-sm font-medium text-slate-600 uppercase tracking-wide mb-1">
                        Exit Code
                      </div>
                      <span class={`badge badge-outline badge-sm ${data().driver_exit_code === 0 ? 'badge-success' : 'badge-error'}`}>
                        {data().driver_exit_code}
                      </span>
                    </div>
                  </Show>
                </div>

                <Show when={Object.keys(data().driver_info).length > 0}>
                  <div>
                    <h3 class="text-sm font-medium text-slate-600 mb-3">Driver Details</h3>
                    <div class="bg-slate-50 p-4 rounded-lg">
                      <pre class="text-sm text-slate-700 overflow-auto">
                        {JSON.stringify(data().driver_info, null, 2)}
                      </pre>
                    </div>
                  </div>
                </Show>
              </div>
            </div>
          </Show>

          {/* Terminal Output */}
          <LogViewer submissionId={submissionId()} />

          {/* Metadata */}
          <Show when={hasMetadata()}>
            <div class="card bg-white shadow-professional">
              <div class="card-body p-6">
                <h2 class="text-lg font-semibold text-slate-900 mb-4">Metadata</h2>
                <div class="bg-slate-50 p-4 rounded-lg">
                  <pre class="text-sm text-slate-700 overflow-auto">
                    {JSON.stringify(data().metadata, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </Show>
        </div>
      </Show>

      {/* Runtime Environment Modal */}
      <Show when={showRuntimeEnvModal()}>
        <div class="modal modal-open">
          <div class="modal-box max-w-4xl">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">Runtime Environment</h3>
              <button 
                class="btn btn-sm btn-circle btn-ghost"
                onClick={() => setShowRuntimeEnvModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div class="bg-slate-50 p-4 rounded-lg max-h-96 overflow-auto">
              <pre class="text-sm text-slate-700">
                {JSON.stringify(data()?.runtime_env || {}, null, 2)}
              </pre>
            </div>
            
            <div class="modal-action">
              <button 
                class="btn btn-sm"
                onClick={() => setShowRuntimeEnvModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}