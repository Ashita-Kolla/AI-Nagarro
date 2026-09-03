import { AgentRow } from './AgentRow.jsx';
import { ConnectionStatus } from './ConnectionStatus.jsx';

export function AgentPipeline({
  agents, activeGate, expandedAgent, setExpandedAgent, setModalAgent,
  wsStatus, threadId, sendMessage, onGateAction,
}) {
  const completedCount = agents.filter(a => a.status === 'complete').length;
  const progressPercent = (completedCount / agents.length) * 100;

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <div className="p-5 border-b border-gray-800 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-100">Agent Operations</h2>
        <ConnectionStatus wsStatus={wsStatus} compact />
      </div>

      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/20">
        <div className="flex justify-between text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">
          <span>Pipeline Progress</span>
          <span>{completedCount} / {agents.length} agents</span>
        </div>
        <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary-600 to-accent-400 transition-all duration-700 ease-out rounded-full" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-2">
        {agents.map(agent => (
          <AgentRow
            key={agent.name}
            agent={agent}
            isGateActive={activeGate === agent.name}
            isExpanded={expandedAgent === agent.name}
            onToggleExpand={() => setExpandedAgent(expandedAgent === agent.name ? null : agent.name)}
            onOpenOutput={() => setModalAgent(agent)}
            canResume={threadId && wsStatus === 'connected' && agent.status !== 'complete' && agent.status !== 'waiting_approval'}
            onResume={() => sendMessage({ type: 'resume', thread_id: threadId, from_agent: agent.name })}
            onGateAction={onGateAction}
          />
        ))}
      </div>
    </div>
  );
}
