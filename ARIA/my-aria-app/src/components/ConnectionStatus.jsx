export function ConnectionStatus({ wsStatus, compact = false }) {
  const dotClass = wsStatus === 'connected' ? 'bg-green-500 animate-pulse' :
    wsStatus === 'connecting' ? 'bg-amber-500 animate-pulse' :
      'bg-red-500';
  const label = wsStatus === 'connected' ? 'Backend Connected' : wsStatus;

  if (compact) {
    return (
      <div className="flex items-center gap-2" role="status" aria-label={`Connection status: ${label}`}>
        <div className={`w-2 h-2 rounded-full ${dotClass}`} />
        <span className="text-xs text-gray-400 capitalize">{label}</span>
      </div>
    );
  }

  const pillClass = wsStatus === 'connected' ? 'bg-green-900/30 text-green-400 border-green-800' :
    wsStatus === 'connecting' ? 'bg-amber-900/30 text-amber-400 border-amber-800' :
      wsStatus === 'error' ? 'bg-red-900/30 text-red-400 border-red-800' :
        'bg-gray-800/50 text-gray-400 border-gray-700/50';

  return (
    <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${pillClass}`} role="status" aria-label={`Connection status: ${label}`}>
      <div className={`w-2 h-2 rounded-full ${dotClass}`} />
      <span className="capitalize">{label}</span>
    </div>
  );
}
