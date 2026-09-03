import { ClockIcon } from './icons.jsx';

export function HitlGate({ agentName, onAction }) {
  return (
    <div className="mt-4 pt-3 border-t border-amber-500/20">
      <div className="flex items-center gap-2 mb-3">
        <ClockIcon cls="w-4 h-4 text-amber-400" />
        <span className="text-xs font-bold text-amber-400">Human Gate Approval Required</span>
      </div>
      <div className="flex gap-2">
        <button onClick={() => onAction('Approve')} className="flex-1 py-1.5 bg-green-700 hover:bg-green-600 text-white text-xs font-semibold rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-green-400 outline-none">
          ✓ Approve
        </button>
        <button onClick={() => onAction('Edit')} className="flex-1 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-gray-400 outline-none">
          ✎ Edit
        </button>
        <button onClick={() => onAction('Regenerate')} className="flex-1 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-primary-400 outline-none">
          ↺ Regenerate
        </button>
        {agentName === 'QA' && (
          <button onClick={() => onAction('LoopToDeveloper')} className="flex-1 py-1.5 bg-purple-700 hover:bg-purple-600 text-white text-xs font-semibold rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-purple-400 outline-none" title="Loop back to the Developer to fix failing tests">
            ↶ Send to Dev
          </button>
        )}
      </div>
    </div>
  );
}
