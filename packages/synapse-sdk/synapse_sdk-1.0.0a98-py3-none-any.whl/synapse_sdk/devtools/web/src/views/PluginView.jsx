import { Show, For, createSignal, createEffect, createMemo, onMount } from "solid-js";
import { createConfigResource, createConfigMutation, createValidationMutation, apiClient } from "../utils/api";
import { SettingsIcon, FlaskIcon, RocketIcon, SaveIcon, PlayIcon, TrashIcon, CheckIcon, AlertCircleIcon, AlertTriangleIcon, InfoIcon, UploadIcon, CheckCircleIcon, RefreshIcon } from "../components/icons";

export default function PluginView() {
  // State
  const [activeTab, setActiveTab] = createSignal("config");
  const [localConfig, setLocalConfig] = createSignal({});
  const [isDirty, setIsDirty] = createSignal(false);
  const [validationResult, setValidationResult] = createSignal(null);
  const [showValidationDetails, setShowValidationDetails] = createSignal(false);
  const [saveMessage, setSaveMessage] = createSignal("");
  const [saveMessageType, setSaveMessageType] = createSignal("success");
  
  // Testing state
  const [httpConfig, setHttpConfig] = createSignal({});
  const [selectedAction, setSelectedAction] = createSignal("");
  const [httpParams, setHttpParams] = createSignal("");
  const [httpResults, setHttpResults] = createSignal([]);
  const [isExecuting, setIsExecuting] = createSignal(false);
  const [isLoadingHttpConfig, setIsLoadingHttpConfig] = createSignal(false);
  
  // Publishing state
  const [publishConfig, setPublishConfig] = createSignal({});
  const [isPublishing, setIsPublishing] = createSignal(false);
  const [publishResult, setPublishResult] = createSignal(null);

  // API resources
  const { data: config, loading: isLoading, error, refresh: refreshConfig } = createConfigResource();
  const configMutation = createConfigMutation();
  const validationMutation = createValidationMutation();

  // Computed properties
  const pluginActions = createMemo(() => {
    const config = localConfig();
    if (!config.actions) return [];
    return Object.entries(config.actions).map(([name, action]) => ({
      name,
      type: action.method || 'job',
    }));
  });

  const canPublish = createMemo(() => {
    const pubConfig = publishConfig();
    return pubConfig.host && pubConfig.accessToken;
  });

  // Methods
  const markDirty = () => {
    setIsDirty(true);
  };

  const updateLocalConfig = (field, value) => {
    setLocalConfig(prev => ({ ...prev, [field]: value }));
    markDirty();
  };

  const updateTasksConfig = (value) => {
    // Convert comma-separated string to array for config
    const tasksArray = value.split(',').map(task => task.trim()).filter(task => task.length > 0);
    updateLocalConfig('tasks', tasksArray);
  };

  const saveConfiguration = async () => {
    try {
      // Validate first
      const validation = await validationMutation.mutate(localConfig());
      setValidationResult(validation);

      if (!validation.valid) {
        setSaveMessage("Configuration has validation errors");
        setSaveMessageType("error");
        setTimeout(() => setSaveMessage(""), 5000);
        return;
      }

      await configMutation.mutate(localConfig());
      setIsDirty(false);
      setSaveMessage("Configuration saved successfully");
      setSaveMessageType("success");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (err) {
      setSaveMessage(err.message || "Failed to save configuration");
      setSaveMessageType("error");
      setTimeout(() => setSaveMessage(""), 5000);
    }
  };

  const loadHttpConfig = async () => {
    setIsLoadingHttpConfig(true);
    try {
      const authResponse = await apiClient.get('/auth/token');
      if (authResponse.data) {
        setHttpConfig({
          baseUrl: authResponse.data.host || 'Not configured',
          accessToken: authResponse.data.token || '',
          pluginCode: ''
        });
      }
    } catch (err) {
      console.error('Failed to load http config:', err);
    } finally {
      setIsLoadingHttpConfig(false);
    }
  };

  const loadActionParams = async (action) => {
    if (!action) return;
    
    try {
      const response = await apiClient.get(`/plugin/http/params/${action}`);
      if (response.data && response.data.has_example) {
        setHttpParams(JSON.stringify(response.data.example_params, null, 2));
      }
    } catch (err) {
      console.error('Failed to load action params:', err);
    }
  };

  const executeHttpRequest = async () => {
    if (!selectedAction() || isExecuting()) return;
    
    setIsExecuting(true);
    try {
      const response = await apiClient.post('/plugin/http', {
        action: selectedAction(),
        params: httpParams() ? JSON.parse(httpParams()) : {},
        debug: true,
        access_token: httpConfig().accessToken,
      });

      // Check if the response indicates a validation error
      if (response.data && !response.data.success && response.data.validation_errors) {
        const result = {
          timestamp: new Date().toISOString(),
          success: false,
          status_code: 400,
          error: response.data.error,
          validation_errors: response.data.validation_errors,
          execution_time: 0
        };
        setHttpResults(prev => [...prev, result]);
      } else {
        const result = {
          timestamp: new Date().toISOString(),
          success: response.data?.success !== false,
          status_code: response.data?.status_code || 200,
          response_data: response.data,
          execution_time: response.data?.execution_time || 0,
          error: response.error
        };
        setHttpResults(prev => [...prev, result]);
      }
    } catch (err) {
      const result = {
        timestamp: new Date().toISOString(),
        success: false,
        status_code: 500,
        error: err.message,
        execution_time: 0
      };
      setHttpResults(prev => [...prev, result]);
    } finally {
      setIsExecuting(false);
    }
  };

  const clearResults = () => {
    setHttpResults([]);
  };

  const publishPlugin = async () => {
    setIsPublishing(true);
    try {
      const response = await apiClient.post('/plugin/publish', {
        host: publishConfig().host,
        access_token: publishConfig().accessToken,
        debug: publishConfig().debug,
      });

      // Handle validation errors from the new API
      if (response.data && !response.data.success && response.data.validation_errors) {
        setPublishResult({
          success: false,
          error: response.data.error,
          validation_errors: response.data.validation_errors,
          message: response.data.message
        });
      } else {
        setPublishResult(response.data);
      }
    } catch (err) {
      setPublishResult({
        success: false,
        error: err.message || 'Failed to publish plugin'
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Auto-validation with debouncing
  let validationTimeout;
  createEffect(() => {
    const config = localConfig();
    if (Object.keys(config).length > 0) {
      if (validationTimeout) clearTimeout(validationTimeout);
      
      validationTimeout = setTimeout(async () => {
        try {
          const validation = await validationMutation.mutate(config);
          setValidationResult(validation);
        } catch (error) {
          console.debug('Auto-validation failed:', error);
        }
      }, 500);
    }
  });

  // Sync with config
  createEffect(() => {
    if (config()) {
      const configData = config().config || config(); // Handle both direct config and wrapped response
      setLocalConfig({ ...configData });
      setIsDirty(false);
      
      // Pre-fill plugin code in testing from config
      if (configData.code && !httpConfig().pluginCode) {
        setHttpConfig(prev => ({ ...prev, pluginCode: configData.code }));
      }
    }
  });

  // Load data on mount
  onMount(async () => {
    await loadHttpConfig();
    
    // Load publish config
    try {
      const authResponse = await apiClient.get('/auth/token');
      if (authResponse.data?.token && authResponse.data?.host) {
        setPublishConfig({
          host: authResponse.data.host,
          accessToken: authResponse.data.token,
          debug: true
        });
      }
    } catch (err) {
      console.error('Failed to load publish config:', err);
    }
  });

  return (
    <div class="min-h-screen bg-slate-50">
      {/* Header */}
      <header class="sticky top-0 z-50 w-full border-b border-slate-200 glass-effect">
        <div class="container mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
          <div class="flex-1">
            <h1 class="text-lg font-semibold">Plugin Development</h1>
            <p class="text-sm text-slate-500">Configure and deploy your Synapse plugin</p>
          </div>
          <Show when={isDirty()}>
            <button
              class="btn btn-sm btn-primary"
              onClick={saveConfiguration}
              disabled={configMutation.loading()}
            >
              <SaveIcon class="w-4 h-4 mr-2" />
              {configMutation.loading() ? 'Saving...' : 'Save'}
            </button>
          </Show>
        </div>
      </header>

      {/* Loading State */}
      <Show when={isLoading()}>
        <div class="flex min-h-[400px] items-center justify-center">
          <div class="text-center">
            <div class="loading loading-spinner loading-lg mb-4"></div>
            <p class="text-sm text-slate-600">Loading configuration...</p>
          </div>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class="container mx-auto max-w-6xl px-4 py-8">
          <div class="alert alert-error">
            <AlertCircleIcon class="w-4 h-4" />
            <div>
              <h3 class="font-semibold">Failed to load configuration</h3>
              <p class="text-sm">{error()}</p>
            </div>
          </div>
          <button class="btn btn-sm btn-outline mt-4" onClick={refreshConfig}>
            <RefreshIcon class="w-4 h-4 mr-2" />
            Retry
          </button>
        </div>
      </Show>

      {/* Main Content */}
      <Show when={!isLoading() && !error()}>
        <main class="px-6 py-6">
          {/* Tabs */}
          <div class="tabs tabs-bordered w-full">
            <button 
              class={`tab tab-lg ${activeTab() === 'config' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('config')}
            >
              <SettingsIcon class="w-4 h-4 mr-2" />
              Configuration
            </button>
            <button 
              class={`tab tab-lg ${activeTab() === 'httprequest' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('httprequest')}
            >
              <FlaskIcon class="w-4 h-4 mr-2" />
              HTTP Request
            </button>
            <button 
              class={`tab tab-lg ${activeTab() === 'deployment' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('deployment')}
            >
              <RocketIcon class="w-4 h-4 mr-2" />
              Deployment
            </button>
          </div>

          {/* Configuration Tab */}
          <Show when={activeTab() === 'config'}>
            <div class="mt-6 space-y-4">
              <div class="card bg-white shadow-professional">
                <div class="card-body p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-semibold text-slate-900">Basic Information</h2>
                    <Show when={config() && config().file_path}>
                      <div class="flex items-center gap-2 text-sm text-slate-600">
                        <InfoIcon class="w-4 h-4" />
                        <span>Loaded from {config().file_path}</span>
                      </div>
                    </Show>
                  </div>
                  
                  {/* Validation Status */}
                  <Show when={validationResult() || (config() && config().validation)}>
                    {(() => {
                      const validation = validationResult() || (config() && config().validation);
                      return (
                        <div class={`alert mb-6 ${validation.valid ? 'alert-success' : 'alert-error'}`}>
                          <Show when={validation.valid}>
                            <CheckIcon class="w-4 h-4" />
                          </Show>
                          <Show when={!validation.valid}>
                            <AlertCircleIcon class="w-4 h-4" />
                          </Show>
                          <div class="flex-1">
                            <div class="flex items-center justify-between">
                              <Show when={validation.valid}>
                                <span>Configuration valid ({validation.validated_fields} fields)</span>
                              </Show>
                              <Show when={!validation.valid}>
                                <span>{validation.errors?.length || 0} validation error{(validation.errors?.length || 0) > 1 ? 's' : ''}</span>
                              </Show>
                              <Show when={!validation.valid && validation.errors?.length > 0}>
                                <button
                                  class="btn btn-xs btn-ghost"
                                  onClick={() => setShowValidationDetails(!showValidationDetails())}
                                >
                                  {showValidationDetails() ? 'Hide' : 'Show'} Details
                                </button>
                              </Show>
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </Show>

                  {/* Validation Errors */}
                  <Show when={showValidationDetails()}>
                    {(() => {
                      const validation = validationResult() || (config() && config().validation);
                      const errors = validation?.errors || [];
                      
                      return errors.length > 0 && !validation?.valid ? (
                        <div class="mb-6 space-y-2">
                          <For each={errors}>
                            {(error) => (
                              <div class="flex items-start gap-2 text-sm text-red-600">
                                <AlertTriangleIcon class="mt-0.5 h-3 w-3 flex-shrink-0" />
                                <span>{error}</span>
                              </div>
                            )}
                          </For>
                        </div>
                      ) : null;
                    })()}
                  </Show>

                  {/* Form */}
                  <div class="grid gap-4 md:grid-cols-2">
                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Plugin Name</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered"
                        placeholder="Enter plugin name"
                        value={localConfig().name || ''}
                        onInput={(e) => updateLocalConfig('name', e.target.value)}
                      />
                    </div>

                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Code</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered"
                        placeholder="plugin-code"
                        value={localConfig().code || ''}
                        onInput={(e) => updateLocalConfig('code', e.target.value)}
                      />
                    </div>

                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Version</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered"
                        placeholder="1.0.0"
                        value={localConfig().version || ''}
                        onInput={(e) => updateLocalConfig('version', e.target.value)}
                      />
                    </div>

                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Category</span>
                      </label>
                      <select
                        class="select select-bordered"
                        value={localConfig().category || ''}
                        onChange={(e) => updateLocalConfig('category', e.target.value)}
                      >
                        <option value="">Select category</option>
                        <option value="neural_net">Neural Network</option>
                        <option value="export">Export</option>
                        <option value="upload">Upload</option>
                        <option value="smart_tool">Smart Tool</option>
                        <option value="post_annotation">Post Annotation</option>
                        <option value="pre_annotation">Pre Annotation</option>
                        <option value="data_validation">Data Validation</option>
                      </select>
                    </div>

                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Data Type</span>
                      </label>
                      <select
                        class="select select-bordered"
                        value={localConfig().data_type || ''}
                        onChange={(e) => updateLocalConfig('data_type', e.target.value)}
                      >
                        <option value="">Select data type</option>
                        <option value="image">Image</option>
                        <option value="text">Text</option>
                        <option value="video">Video</option>
                        <option value="pcd">Point Cloud</option>
                        <option value="audio">Audio</option>
                      </select>
                    </div>

                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Package Manager</span>
                      </label>
                      <select
                        class="select select-bordered"
                        value={localConfig().package_manager || ''}
                        onChange={(e) => updateLocalConfig('package_manager', e.target.value)}
                      >
                        <option value="">Select package manager</option>
                        <option value="pip">pip</option>
                        <option value="uv">uv</option>
                      </select>
                    </div>

                    <div class="form-control md:col-span-2">
                      <label class="label">
                        <span class="label-text">Description</span>
                      </label>
                      <textarea
                        class="textarea textarea-bordered"
                        rows="3"
                        placeholder="Describe what your plugin does"
                        value={localConfig().description || ''}
                        onInput={(e) => updateLocalConfig('description', e.target.value)}
                      />
                    </div>

                    <div class="form-control md:col-span-2">
                      <label class="label">
                        <span class="label-text">Task Types</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered"
                        placeholder="e.g., image.object_detection, text.classification"
                        value={Array.isArray(localConfig().tasks) ? localConfig().tasks.join(', ') : (localConfig().tasks || '')}
                        onInput={(e) => updateTasksConfig(e.target.value)}
                      />
                      <label class="label">
                        <span class="label-text-alt">Comma-separated task types (format: data_type.task_name)</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Show>

          {/* Http Tab */}
          <Show when={activeTab() === 'httprequest'}>
            <div class="mt-6 space-y-4">
              {/* HTTP Configuration */}
              <div class="card bg-white shadow-professional">
                <div class="card-body p-6">
                  <h3 class="text-lg font-semibold text-slate-900 mb-4">HTTP Configuration</h3>
                  
                  <Show when={isLoadingHttpConfig()}>
                    <div class="flex items-center gap-3 text-sm text-slate-600">
                      <div class="loading loading-spinner loading-sm"></div>
                      <span>Loading configuration...</span>
                    </div>
                  </Show>
                  
                  <Show when={!isLoadingHttpConfig()}>
                    <div class="grid gap-4 md:grid-cols-2">
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Backend URL</span>
                        </label>
                        <input
                          type="text"
                          class="input input-bordered bg-slate-50"
                          value={httpConfig().baseUrl || 'Not configured'}
                          readonly
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Access Token</span>
                        </label>
                        <input
                          type="password"
                          class="input input-bordered bg-slate-50"
                          value={httpConfig().accessToken ? '••••••••' : 'Not configured'}
                          readonly
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Plugin Code</span>
                          <Show when={httpConfig().pluginCode === localConfig().code}>
                          </Show>
                        </label>
                        <input
                          type="text"
                          class="input input-bordered"
                          placeholder="Enter plugin code"
                          readonly
                          value={httpConfig().pluginCode || ''}
                          onInput={(e) => setHttpConfig(prev => ({ ...prev, pluginCode: e.target.value }))}
                        />
                      </div>
                    </div>
                  </Show>
                </div>
              </div>

              {/* Action Selection */}
              <div class="card bg-white shadow-professional">
                <div class="card-body p-6">
                  <h3 class="text-lg font-semibold text-slate-900 mb-4">Select Action</h3>
                  
                  <Show when={pluginActions().length > 0}>
                    <div class="flex flex-wrap gap-2">
                      <For each={pluginActions()}>
                        {(action) => (
                          <button
                            class={`btn btn-sm ${selectedAction() === action.name ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => {
                              setSelectedAction(action.name);
                              loadActionParams(action.name);
                            }}
                          >
                            {action.name}
                            <span class="badge badge-outline badge-secondary badge-sm ml-2">{action.type}</span>
                          </button>
                        )}
                      </For>
                    </div>
                  </Show>
                  
                  <Show when={pluginActions().length === 0}>
                    <div class="flex flex-col items-center py-8 text-center">
                      <InfoIcon class="w-8 h-8 text-slate-400 mb-2" />
                      <p class="text-sm text-slate-600">No actions configured</p>
                    </div>
                  </Show>
                </div>
              </div>

              {/* HTTP Endpoint Reference */}
              <Show when={selectedAction()}>
                <div class="card bg-white shadow-professional">
                  <div class="card-body p-6">
                    <h3 class="text-lg font-semibold text-slate-900 mb-4">Endpoint Reference</h3>
                    
                    <div class="bg-slate-50 p-4 rounded-lg font-mono text-sm mb-4">
                      <div class="flex items-center gap-2 mb-2">
                        <span class="badge badge-primary badge-sm">POST</span>
                        <span class="text-slate-700">
                          {httpConfig().baseUrl || 'http://localhost:8000'}/plugins/{httpConfig().pluginCode || 'plugin_code'}/run/
                        </span>
                      </div>
                      
                      <div class="text-xs text-slate-600 space-y-1">
                        <div><strong>Headers:</strong></div>
                        <div class="ml-4">Content-Type: application/json</div>
                        <div class="ml-4">Accept: application/json; indent=4</div>
                        <Show when={httpConfig().accessToken}>
                          <div class="ml-4">SYNAPSE-Access-Token: Token ••••••••</div>
                        </Show>
                        
                        <div class="mt-2"><strong>Body Structure:</strong></div>
                        <div class="ml-4">{"{"}</div>
                        <div class="ml-6">"agent": 2,</div>
                        <div class="ml-6">"action": "{selectedAction()}",</div>
                        <div class="ml-6">"params": {"{"} ... {"}"}, </div>
                        <div class="ml-6">"debug": true</div>
                        <div class="ml-4">{"}"}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </Show>

              {/* HTTP Parameters */}
              <Show when={selectedAction()}>
                <div class="card bg-white shadow-professional">
                  <div class="card-body p-6">
                    <h3 class="text-lg font-semibold text-slate-900 mb-4">HTTP Parameters</h3>
                    
                    <div class="mb-3">
                      <label class="label">
                        <span class="label-text">Parameters (JSON)</span>
                        <span class="label-text-alt">Will be sent as "params" in the request body</span>
                      </label>
                    </div>
                    
                    <textarea
                      class="textarea textarea-bordered font-mono text-xs w-full"
                      rows="8"
                      placeholder="Enter JSON parameters..."
                      value={httpParams()}
                      onInput={(e) => setHttpParams(e.target.value)}
                    />
                    
                    <div class="flex gap-2 mt-4">
                      <button
                        class="btn btn-sm btn-primary"
                        onClick={executeHttpRequest}
                        disabled={isExecuting() || !selectedAction()}
                      >
                        <Show when={!isExecuting()}>
                          <PlayIcon class="w-4 h-4 mr-2" />
                        </Show>
                        <Show when={isExecuting()}>
                          <div class="loading loading-spinner loading-sm mr-2"></div>
                        </Show>
                        {isExecuting() ? 'Executing...' : 'Execute HTTP Request'}
                      </button>
                      <button 
                        class="btn btn-sm btn-outline" 
                        onClick={() => loadActionParams(selectedAction())}
                        disabled={!selectedAction()}
                      >
                        <RefreshIcon class="w-4 h-4 mr-2" />
                        Load Example
                      </button>
                      <button class="btn btn-sm btn-outline" onClick={clearResults}>
                        <TrashIcon class="w-4 h-4 mr-2" />
                        Clear
                      </button>
                    </div>
                  </div>
                </div>
              </Show>

              {/* Results */}
              <Show when={httpResults().length > 0}>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-slate-900">Results</h3>
                    <span class="badge badge-outline badge-secondary">{httpResults().length} result{httpResults().length > 1 ? 's' : ''}</span>
                  </div>
                  
                  <For each={httpResults()}>
                    {(result) => (
                      <div class="card bg-white shadow-professional">
                        <div class="border-b border-slate-200 bg-slate-50 px-6 py-3">
                          <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2">
                              <Show when={result.success}>
                                <CheckIcon class="w-4 h-4 text-emerald-600" />
                              </Show>
                              <Show when={!result.success}>
                                <AlertCircleIcon class="w-4 h-4 text-red-600" />
                              </Show>
                              <span class={`text-sm font-medium ${result.success ? 'text-emerald-700' : 'text-red-700'}`}>
                                {result.success ? 'Success' : 'Failed'}
                              </span>
                              <span class="badge badge-outline badge-sm">{result.status_code}</span>
                            </div>
                            <div class="flex items-center gap-3 text-xs text-slate-600">
                              <span>{result.execution_time}ms</span>
                              <span>{formatTimestamp(result.timestamp)}</span>
                            </div>
                          </div>
                        </div>
                        <div class="p-6">
                          <Show when={result.validation_errors}>
                            <div class="mb-4">
                              <h4 class="text-sm font-medium text-red-700 mb-2">Configuration Validation Errors:</h4>
                              <div class="space-y-1">
                                <For each={result.validation_errors}>
                                  {(error) => (
                                    <div class="flex items-start gap-2 text-sm text-red-600">
                                      <AlertTriangleIcon class="mt-0.5 h-3 w-3 flex-shrink-0" />
                                      <span>{error}</span>
                                    </div>
                                  )}
                                </For>
                              </div>
                            </div>
                          </Show>
                          <pre class="overflow-auto rounded-md bg-slate-100 p-3 text-xs">
                            {JSON.stringify(result.response_data || result.error, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </For>
                </div>
              </Show>
            </div>
          </Show>

          {/* Deployment Tab */}
          <Show when={activeTab() === 'deployment'}>
            <div class="mt-6 space-y-4">
              <div class="card bg-white shadow-professional">
                <div class="card-body p-6">
                  <h3 class="text-lg font-semibold text-slate-900 mb-4">Deployment Settings</h3>
                  
                  <div class="grid gap-4 md:grid-cols-2">
                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Backend URL</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered bg-slate-50"
                        value={publishConfig().host || 'Not configured'}
                        readonly
                      />
                    </div>
                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Access Token</span>
                      </label>
                      <input
                        type="password"
                        class="input input-bordered bg-slate-50"
                        value={publishConfig().accessToken ? '••••••••' : 'Not configured'}
                        readonly
                      />
                    </div>
                    <div class="form-control">
                      <label class="label cursor-pointer">
                        <span class="label-text">Enable Debug Mode</span>
                        <input
                          type="checkbox"
                          class="toggle toggle-primary ml-2"
                          checked={publishConfig().debug || false}
                          onChange={(e) => setPublishConfig(prev => ({ ...prev, debug: e.target.checked }))}
                        />
                      </label>
                    </div>
                    <div class="form-control">
                      <label class="label">
                        <span class="label-text">Debug Modules</span>
                      </label>
                      <input
                        type="text"
                        class="input input-bordered"
                        placeholder="module1,module2"
                        value={publishConfig().debugModules || ''}
                        onInput={(e) => setPublishConfig(prev => ({ ...prev, debugModules: e.target.value }))}
                      />
                      <label class="label">
                        <span class="label-text-alt">Comma-separated list of debug modules (optional)</span>
                      </label>
                    </div>
                  </div>

                  <div class="mt-6 border-t border-slate-200 pt-6">
                    <button
                      class="btn btn-primary"
                      onClick={publishPlugin}
                      disabled={isPublishing() || !canPublish()}
                    >
                      <Show when={!isPublishing()}>
                        <UploadIcon class="w-4 h-4 mr-2" />
                      </Show>
                      <Show when={isPublishing()}>
                        <div class="loading loading-spinner loading-sm mr-2"></div>
                      </Show>
                      {isPublishing() ? 'Publishing...' : 'Publish Plugin'}
                    </button>
                  </div>

                  {/* Publish Results */}
                  <Show when={publishResult()}>
                    <div class={`alert mt-6 ${publishResult().success ? 'alert-success' : 'alert-error'}`}>
                      <Show when={publishResult().success}>
                        <CheckCircleIcon class="w-4 h-4" />
                      </Show>
                      <Show when={!publishResult().success}>
                        <AlertCircleIcon class="w-4 h-4" />
                      </Show>
                      <div class="flex-1">
                        <h4 class="font-semibold">
                          {publishResult().success ? 'Published Successfully' : 'Publication Failed'}
                        </h4>
                        <p class="text-sm">
                          {publishResult().success ? publishResult().message : (publishResult().message || publishResult().error)}
                        </p>
                        
                        {/* Show validation errors if they exist */}
                        <Show when={!publishResult().success && publishResult().validation_errors}>
                          <div class="mt-3">
                            <h5 class="text-sm font-medium mb-2">Configuration Issues:</h5>
                            <div class="space-y-1">
                              <For each={publishResult().validation_errors}>
                                {(error) => (
                                  <div class="flex items-start gap-2 text-xs">
                                    <AlertTriangleIcon class="mt-0.5 h-3 w-3 flex-shrink-0" />
                                    <span>{error}</span>
                                  </div>
                                )}
                              </For>
                            </div>
                          </div>
                        </Show>
                        
                        <Show when={publishResult().success}>
                          <div class="flex gap-4 mt-2 text-xs">
                            <span>Plugin: {publishResult().plugin_code}</span>
                            <span>Version: {publishResult().version}</span>
                            <Show when={publishResult().name}>
                              <span>Name: {publishResult().name}</span>
                            </Show>
                          </div>
                        </Show>
                      </div>
                    </div>
                  </Show>
                </div>
              </div>
            </div>
          </Show>
        </main>
      </Show>

      {/* Status Toast */}
      <Show when={saveMessage()}>
        <div class="toast toast-top toast-end">
          <div class={`alert ${saveMessageType() === 'success' ? 'alert-success' : 'alert-error'}`}>
            <Show when={saveMessageType() === 'success'}>
              <CheckIcon class="w-4 h-4" />
            </Show>
            <Show when={saveMessageType() === 'error'}>
              <AlertCircleIcon class="w-4 h-4" />
            </Show>
            <span>{saveMessage()}</span>
          </div>
        </div>
      </Show>
    </div>
  );
}