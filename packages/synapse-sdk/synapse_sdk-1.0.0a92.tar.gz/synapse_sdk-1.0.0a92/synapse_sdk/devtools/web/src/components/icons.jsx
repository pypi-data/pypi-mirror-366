// Icon components using SolidJS JSX with Heroicons

export const SaveIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
    />
  </svg>
);

export const RefreshIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
    />
  </svg>
);

export const AlertCircleIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

export const CheckIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <polyline points="20,6 9,17 4,12" />
  </svg>
);

export const AlertTriangleIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
    />
  </svg>
);

export const InfoIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);

export const PlayIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <polygon points="5,3 19,12 5,21" />
  </svg>
);

export const TrashIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <polyline points="3,6 5,6 21,6" />
    <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" />
  </svg>
);

export const XIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

export const UploadIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
    />
  </svg>
);

export const CheckCircleIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

export const SettingsIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <circle cx="12" cy="12" r="3" />
    <path d="m12,1 1.27,2.418c.3.568.92.885 1.544.784l2.617-.427a1.031,1.031 0 0 1 1.205.968l.212,2.706c.023.294.177.569.425.762l2.209,1.719a1.031,1.031 0 0 1 0 1.614l-2.209,1.719c-.248.193-.402.468-.425.762l-.212,2.706a1.031,1.031 0 0 1 -1.205.968l-2.617-.427c-.624-.101-1.244.216-1.544.784L12,23l-1.27-2.418c-.3-.568-.92-.885-1.544-.784l-2.617.427a1.031,1.031 0 0 1 -1.205-.968l-.212-2.706c-.023-.294-.177-.569-.425-.762L2.518,14.07a1.031,1.031 0 0 1 0,-1.614l2.209-1.719c.248-.193.402-.468.425-.762l.212-2.706a1.031,1.031 0 0 1 1.205-.968l2.617.427c.624.101,1.244-.216,1.544-.784L12,1z" />
  </svg>
);

export const FlaskIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M11 6L8 21l4-7 4 7-3-15M8 8h8M15 6h1a2 2 0 012 2v1M9 6V4a2 2 0 012-2h2a2 2 0 012 2v2"
    />
  </svg>
);

export const RocketIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M4.5 19.5l15-15m0 0H8m11.5 0v11.5M12 18.5L9.5 21L7 18.5l1.5-1.5L12 18.5zM2.5 13.5L5 16l2.5-2.5L6 12l-3.5 1.5z"
    />
  </svg>
);

export const HomeIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="m3 12 2-2m0 0 7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
    />
  </svg>
);

export const DocumentIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
    />
  </svg>
);

export const CubeIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="m7.875 14.25 1.214 1.942a2.25 2.25 0 0 0 1.908 1.058h2.006c.776 0 1.497-.4 1.908-1.058l1.214-1.942M2.41 9h4.636a2.25 2.25 0 0 1 1.872 1.002l.164.246a2.25 2.25 0 0 0 1.872 1.002h2.092a2.25 2.25 0 0 0 1.872-1.002l.164-.246A2.25 2.25 0 0 1 16.954 9h4.636M7.5 14.25v-3.375c0-.621.504-1.125 1.125-1.125h6.75c.621 0 1.125.504 1.125 1.125v3.375m-8 0V18a2.25 2.25 0 0 0 2.25 2.25h3.5A2.25 2.25 0 0 0 16.5 18v-3.625"
    />
  </svg>
);

export const ArrowLeftIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M15 19l-7-7 7-7"
    />
  </svg>
);

export const EyeIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
    />
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
    />
  </svg>
);

export const StatusIcon = (props) => (
  <div class={`inline-flex items-center justify-center w-2 h-2 rounded-full ${props.class}`} />
);

export const MenuIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M3 12h18M3 6h18M3 18h18"
    />
  </svg>
);

export const CloseIcon = (props) => (
  <svg
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);