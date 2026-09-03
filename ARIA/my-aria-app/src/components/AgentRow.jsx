import { CheckCircleIcon, ClockIcon, DotsIcon, ChevronDownIcon, ChevronUpIcon, ExternalLinkIcon, WarningIcon } from './icons.jsx';
import { HitlGate } from './HitlGate.jsx';

function getScoreStyle(score) {
  if (!score) return 'bg-gray-800 text-gray-500 border-gray-700';
  if (score >= 80) return 'bg-green-900/30 text-green-400 border-green-800';
  if (score >= 50) return 'bg-amber-900/30 text-amber-400 border-amber-800';
  return 'bg-red-900/30 text-red-400 border-red-800';
}

function getStatusIcon(status) {
  if (status === 'complete') return <CheckCircleIcon />;
  if (status === 'running') return <div className="w-5 h-5 border-2 border-t-primary-500 border-gray-700 rounded-full animate-spin" />;
  if (status === 'waiting_approval') return <ClockIcon />;
  return <DotsIcon />;
}

const canOpenOutput = (agent) => (agent.status === 'complete' || agent.status === 'waiting_approval') && agent.output;

export function AgentRow({
  agent, isGateActive, isExpanded, onToggleExpand, onOpenOutput,
  canResume, onResume, onGateAction,
}) {
  return (
    <div>
      <div className={`rounded-lg border px-4 py-3 transition-all ${agent.status === 'running' ? 'bg-gray-800/60 border-primary-500/50 shadow-[0_0_12px_rgba(59,130,246,0.08)]' :
          agent.status === 'waiting_approval' ? 'bg-amber-900/10 border-amber-500/30' :
            agent.status === 'complete' ? 'bg-gray-900 border-gray-700' :
              'bg-gray-950 border-gray-800/40 opacity-40'
        }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-6 flex justify-center shrink-0">{getStatusIcon(agent.status)}</div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-200">{agent.name}</p>
              {agent.summary ? (
                <p className="text-xs text-gray-500 mt-0.5">{agent.summary}</p>
              ) : agent.status === 'pending' ? (
                <p className="text-xs text-gray-500 mt-0.5">Queued — waiting in pipeline</p>
              ) : (
                <div className="h-3 w-32 mt-1 rounded bg-gray-700/40 animate-pulse" />
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {agent.score !== null && (
              <span className={`text-xs font-mono px-2 py-0.5 rounded border ${getScoreStyle(agent.score)}`}>Score: {agent.score}</span>
            )}
            {canOpenOutput(agent) && (
              <button
                onClick={onOpenOutput}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white border border-gray-700 rounded-md transition-colors font-medium focus-visible:ring-2 focus-visible:ring-primary-400 outline-none"
              >
                <ExternalLinkIcon />
                Open full output
              </button>
            )}
            {canResume && (
              <button
                onClick={onResume}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-primary-600/20 hover:bg-primary-600/30 text-primary-400 hover:text-primary-300 border border-primary-700/50 rounded-md transition-colors font-medium focus-visible:ring-2 focus-visible:ring-primary-400 outline-none"
                title="Resume pipeline execution from this agent"
              >
                ▶ Resume
              </button>
            )}
            {agent.status === 'complete' && (
              <button onClick={onToggleExpand} aria-label={isExpanded ? `Collapse ${agent.name} summary` : `Expand ${agent.name} summary`} className="text-gray-500 hover:text-gray-300 p-1 focus-visible:ring-2 focus-visible:ring-primary-400 rounded outline-none">
                {isExpanded ? <ChevronUpIcon /> : <ChevronDownIcon />}
              </button>
            )}
          </div>
        </div>

        {agent.warning && (
          <div className="mt-3 flex items-start gap-2 bg-amber-900/15 border border-amber-700/30 rounded-lg px-3 py-2 text-xs text-amber-400">
            <WarningIcon />
            <span>{agent.warning}</span>
          </div>
        )}

        {isGateActive && <HitlGate agentName={agent.name} onAction={onGateAction} />}
      </div>

      {isExpanded && agent.output && (
        <div className="ml-9 mt-1 mb-1 p-4 bg-gray-900 rounded-lg border border-gray-800">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Quick Summary</p>
            <button onClick={onOpenOutput} className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1 focus-visible:ring-2 focus-visible:ring-primary-400 rounded outline-none">
              <ExternalLinkIcon /> Open full output
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(agent.output).slice(0, 4).map(([k, v]) => (
              <div key={k} className="bg-gray-950 rounded-lg p-2.5 border border-gray-800">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{k.replace(/_/g, ' ')}</p>
                <p className="text-xs text-gray-300 line-clamp-2">
                  {Array.isArray(v) ? `${v.length} items` : typeof v === 'object' ? `${Object.keys(v).length} fields` : String(v).slice(0, 60)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
