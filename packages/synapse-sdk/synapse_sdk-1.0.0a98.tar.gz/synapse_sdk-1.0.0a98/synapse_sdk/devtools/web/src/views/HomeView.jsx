import { Show, For } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { createJobsResource, getJobStatusVariant, formatTimestamp } from "../utils/api";
import { RefreshIcon } from "../components/icons";

export default function HomeView() {
  const navigate = useNavigate();
  const { data: jobs, loading, error, refresh } = createJobsResource();

  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case "SUCCEEDED":
        return "badge-outline badge-success";
      case "FAILED":
        return "badge-outline badge-error";
      case "RUNNING":
        return "badge-outline badge-info";
      case "PENDING":
      case "SUBMITTED":
        return "badge-outline badge-warning";
      case "STOPPED":
      case "CANCELLED":
        return "badge-outline badge-neutral";
      default:
        return "badge-outline badge-neutral";
    }
  };

  const navigateToJobDetail = (submissionId) => {
    navigate(`/job/${submissionId}`);
  };

  return (
    <div class="p-6">
      {/* Header */}
      <div class="mb-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-semibold text-slate-900 mb-1">Jobs</h1>
            <p class="text-sm text-slate-600">
              Monitor and manage Ray job executions
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
              All Jobs ({jobs()?.length || 0})
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
                <h3 class="font-medium">Error loading jobs</h3>
                <div class="text-sm">{error()}</div>
              </div>
            </div>
          </Show>

          {/* Loading State */}
          <Show when={loading() && (!jobs() || jobs().length === 0)}>
            <div class="flex flex-col items-center justify-center py-12">
              <div class="loading loading-spinner loading-md mb-4"></div>
              <p class="text-slate-500">Loading jobs...</p>
            </div>
          </Show>

          {/* Empty State */}
          <Show when={!loading() && (!jobs() || jobs().length === 0) && !error()}>
            <div class="flex flex-col items-center justify-center py-12">
              <div class="text-slate-400 mb-4">
                <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 class="text-lg font-medium text-slate-900 mb-2">No jobs found</h3>
              <p class="text-slate-500">Jobs will appear here once they are submitted</p>
            </div>
          </Show>

          {/* Jobs Table */}
          <Show when={jobs() && jobs().length > 0}>
            <div class="overflow-x-auto">
              <table class="table table-sm w-full">
                <thead>
                  <tr class="border-slate-200">
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Job ID</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Type</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Status</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Message</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">Start Time</th>
                    <th class="bg-slate-50 text-slate-600 font-medium text-sm">End Time</th>
                  </tr>
                </thead>
                <tbody>
                  <For each={jobs()}>
                    {(job) => (
                      <tr 
                        class="hover:bg-slate-50 cursor-pointer border-slate-100"
                        onClick={() => navigateToJobDetail(job.submission_id)}
                      >
                        <td class="py-3">
                          <div class="flex flex-col gap-1">
                            <span class="font-mono text-sm font-medium text-blue-600">
                              {job.submission_id}
                            </span>
                            <Show when={job.job_id}>
                              <span class="font-mono text-sm text-slate-500">
                                {job.job_id}
                              </span>
                            </Show>
                          </div>
                        </td>
                        <td>
                          <span class="badge badge-outline badge-neutral badge-sm font-mono">
                            {job.type}
                          </span>
                        </td>
                        <td>
                          <span class={`badge badge-sm ${getStatusClass(job.status)}`}>
                            {job.status}
                          </span>
                        </td>
                        <td class="max-w-sm">
                          <div class="truncate text-sm">
                            {job.status === "SUCCEEDED" ? "" : job.message || ""}
                          </div>
                        </td>
                        <td class="text-sm text-slate-600">
                          {formatTimestamp(job.start_time)}
                        </td>
                        <td class="text-sm text-slate-600">
                          {formatTimestamp(job.end_time)}
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
      <Show when={jobs() && jobs().length > 0}>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Total Jobs</div>
            <div class="stat-value text-lg text-slate-900">{jobs().length}</div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Succeeded</div>
            <div class="stat-value text-lg text-emerald-600">
              {jobs().filter(job => job.status === "SUCCEEDED").length}
            </div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Failed</div>
            <div class="stat-value text-lg text-red-600">
              {jobs().filter(job => job.status === "FAILED").length}
            </div>
          </div>
          <div class="stat bg-white border border-slate-200 rounded-lg">
            <div class="stat-title text-sm text-slate-600">Running</div>
            <div class="stat-value text-lg text-blue-600">
              {jobs().filter(job => ["RUNNING", "PENDING"].includes(job.status)).length}
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
}