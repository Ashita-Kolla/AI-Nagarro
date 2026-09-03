import { ArtifactIcon, XIcon } from './icons.jsx';

export function Toast({ notification, onOpenDownloads, onDismiss }) {
  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex items-start gap-3 bg-gray-900 border-l-4 border-l-green-500 border border-green-600/60 text-green-300 px-5 py-4 rounded-lg shadow-lg max-w-sm"
      style={{ animation: 'slideUp 0.3s ease-out' }}
      role="status"
    >
      <ArtifactIcon />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-green-300">Artifacts Generated ({notification.agent})</p>
        <p className="text-xs text-gray-400 mt-0.5">{notification.message}</p>
        <button
          onClick={onOpenDownloads}
          className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-green-700 hover:bg-green-600 text-white rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-green-400 outline-none"
        >
          Open Downloads Tab
        </button>
      </div>
      <button onClick={onDismiss} aria-label="Dismiss notification" className="text-gray-500 hover:text-white shrink-0 focus-visible:ring-2 focus-visible:ring-primary-400 rounded outline-none">
        <XIcon />
      </button>
    </div>
  );
}
