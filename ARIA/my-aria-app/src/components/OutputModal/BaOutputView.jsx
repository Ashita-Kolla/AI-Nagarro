import { DownloadList } from '../DownloadCard.jsx';

export function BaOutputView({ agent, output, hasArtifacts, tab, setTab }) {
  const tabNames = ['User Stories', 'Business Reqs', 'Functional Reqs', 'Non-Functional', 'Assumptions', 'Out of Scope', 'Raw JSON'];
  if (hasArtifacts) tabNames.unshift('Downloads');
  const baTab = tabNames[tab] || tabNames[0];

  const userStories = Array.isArray(output.user_stories) ? output.user_stories : [];
  const businessReqs = output.business_requirements || [];
  const functionalReqs = output.functional_requirements || [];
  const nfrs = output.non_functional_requirements || {};
  const assumptions = output.assumptions || [];
  const outOfScope = output.out_of_scope || [];
  const confidence = output.confidence_score ?? null;
  const confidenceReason = output.confidence_reasoning || '';

  return (
    <>
      {confidence !== null && (
        <div className={`mb-5 flex items-center gap-3 px-4 py-3 rounded-xl border text-sm ${confidence >= 71 ? 'bg-green-900/20 border-green-700/40 text-green-300' :
            confidence >= 41 ? 'bg-amber-900/20 border-amber-700/40 text-amber-300' :
              'bg-red-900/20 border-red-700/40 text-red-300'
          }`}>
          <span className="font-bold text-base">{confidence}/100</span>
          <span className="text-xs opacity-80">{confidenceReason}</span>
        </div>
      )}

      <div className="flex gap-1 mb-6 border-b border-gray-700 pb-0 flex-wrap">
        {tabNames.map((t, i) => (
          <button key={t} onClick={() => setTab(i)}
            className={`px-3 py-2 text-xs font-medium rounded-t-lg border-b-2 transition-colors -mb-px ${tab === i ? 'border-accent-400 text-accent-400 bg-accent-400/5' : 'border-transparent text-gray-500 hover:text-gray-300'}`}>
            {t}
          </button>
        ))}
      </div>

      {baTab === 'Downloads' && hasArtifacts && (
        <DownloadList agentName={agent.name} artifacts={agent.artifacts} />
      )}

      {baTab === 'User Stories' && (
        <div className="space-y-4">
          {userStories.length > 0 ? (
            userStories.map((us, i) => {
              if (!us || typeof us !== 'object') return null;
              const storyId = us.id || `US-${i + 1}`;
              const role = us.role || us.persona || 'User';
              const action = us.action || us.story || '';
              const benefit = us.benefit || '';
              const storyText = action
                ? `As a ${role}, I want ${action}${benefit ? `, so that ${benefit}` : ''}`
                : (us.story || '');
              const criteria = us.acceptance_criteria || us.acceptance || [];
              const criteriaArray = Array.isArray(criteria) ? criteria : [criteria];

              return (
                <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-mono font-bold text-primary-400 bg-primary-600/15 px-2 py-0.5 rounded border border-primary-800/50">{storyId}</span>
                    <span className="text-xs text-gray-500 italic">{role}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-100 leading-relaxed mb-3">{storyText}</p>
                  {criteriaArray.length > 0 && (
                    <div className="space-y-1 pl-3 border-l-2 border-gray-700">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Acceptance Criteria</p>
                      {criteriaArray.map((ac, j) => (
                        <p key={j} className="text-xs text-gray-400 flex gap-2 items-start">
                          <span className="text-green-500 mt-0.5 shrink-0">✓</span>{String(ac)}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          ) : <p className="text-gray-500 text-sm">No user stories available.</p>}
        </div>
      )}

      {baTab === 'Business Reqs' && (
        <div className="space-y-2">
          {businessReqs.length > 0 ? businessReqs.map((req, i) => (
            <div key={i} className="flex items-start gap-3 bg-gray-800/40 rounded-lg p-3 border border-gray-700/50">
              <span className="text-primary-400 mt-0.5 shrink-0 font-mono text-xs">{i + 1}</span>
              <span className="text-sm text-gray-200">{String(req)}</span>
            </div>
          )) : <p className="text-gray-500 text-sm">No business requirements.</p>}
        </div>
      )}

      {baTab === 'Functional Reqs' && (
        <div className="space-y-2">
          {functionalReqs.length > 0 ? functionalReqs.map((req, i) => (
            <div key={i} className="flex items-start gap-3 bg-gray-800/40 rounded-lg p-3 border border-gray-700/50">
              <span className="text-accent-400 mt-0.5 shrink-0 font-mono text-xs">{i + 1}</span>
              <span className="text-sm text-gray-200">{String(req)}</span>
            </div>
          )) : <p className="text-gray-500 text-sm">No functional requirements.</p>}
        </div>
      )}

      {baTab === 'Non-Functional' && (
        <div className="space-y-5">
          {Object.entries(nfrs).filter(([, v]) => Array.isArray(v) && v.length > 0).map(([cat, items]) => (
            <div key={cat}>
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-500 inline-block"></span>
                {cat}
              </h4>
              <div className="space-y-2">
                {items.map((item, j) => (
                  <div key={j} className="flex items-start gap-3 bg-gray-800/40 rounded-lg p-3 border border-gray-700/50">
                    <span className="text-purple-400 mt-0.5 shrink-0">›</span>
                    <span className="text-sm text-gray-200">{String(item)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
          {Object.values(nfrs).every(v => !Array.isArray(v) || v.length === 0) && (
            <p className="text-gray-500 text-sm">No non-functional requirements specified.</p>
          )}
        </div>
      )}

      {baTab === 'Assumptions' && (
        <div className="space-y-3">
          {assumptions.length > 0 ? assumptions.map((a, i) => (
            <div key={i} className="flex items-start gap-3 bg-amber-900/10 rounded-lg p-4 border border-amber-800/30">
              <span className="text-amber-500 font-bold shrink-0">!</span>
              <span className="text-sm text-gray-200">{String(a)}</span>
            </div>
          )) : <p className="text-gray-500 text-sm">No assumptions listed.</p>}
        </div>
      )}

      {baTab === 'Out of Scope' && (
        <div className="space-y-2">
          {outOfScope.length > 0 ? outOfScope.map((item, i) => (
            <div key={i} className="flex items-start gap-3 bg-red-900/10 rounded-lg p-3 border border-red-800/30">
              <span className="text-red-400 mt-0.5 shrink-0">✗</span>
              <span className="text-sm text-gray-300">{String(item)}</span>
            </div>
          )) : <p className="text-gray-500 text-sm">No out-of-scope items listed.</p>}
        </div>
      )}

      {baTab === 'Raw JSON' && (
        <pre className="text-xs text-green-400 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}
    </>
  );
}
