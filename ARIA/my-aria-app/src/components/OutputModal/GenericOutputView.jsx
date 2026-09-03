import { MermaidChart } from '../MermaidChart.jsx';
import { DownloadList } from '../DownloadCard.jsx';

function renderValue(val) {
  if (Array.isArray(val)) return (
    <ul className="space-y-1 mt-1">
      {val.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
          <span className="text-primary-400 mt-0.5 shrink-0">›</span>
          <span>{typeof item === 'object' && item !== null ? JSON.stringify(item) : String(item)}</span>
        </li>
      ))}
    </ul>
  );
  if (typeof val === 'object' && val !== null) return (
    <div className="space-y-3 mt-2">
      {Object.entries(val).map(([k, v]) => (
        <div key={k} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <span className="text-xs font-semibold text-primary-400 uppercase tracking-wider block mb-1">{k}</span>
          {renderValue(v)}
        </div>
      ))}
    </div>
  );
  return <p className="text-sm text-gray-200 mt-1">{String(val)}</p>;
}

export function GenericOutputView({ agent, output, hasArtifacts, tab, setTab, tabsKeys }) {
  const isPlainObject = typeof output === 'object' && output !== null && !Array.isArray(output);

  if (!isPlainObject) {
    return (
      <pre className="text-sm text-gray-200 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed whitespace-pre-wrap">
        {typeof output === 'string' ? output : JSON.stringify(output, null, 2)}
      </pre>
    );
  }

  const tabNames = [...tabsKeys, 'Raw JSON'];
  const currentKey = tabNames[tab] || 'Raw JSON';

  return (
    <>
      <div className="flex gap-2 mb-6 border-b border-gray-700 pb-0 flex-wrap">
        {tabNames.map((t, i) => (
          <button key={t} onClick={() => setTab(i)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors -mb-px capitalize ${tab === i ? 'border-accent-400 text-accent-400 bg-accent-400/5' : 'border-transparent text-gray-500 hover:text-gray-300'}`}>
            {t.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      {currentKey === 'Downloads' && hasArtifacts ? (
        <DownloadList agentName={agent.name} artifacts={agent.artifacts} />
      ) : currentKey === 'Raw JSON' ? (
        <pre className="text-xs text-green-400 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed">
          {JSON.stringify(output, null, 2)}
        </pre>
      ) : currentKey.startsWith('mermaid_') ? (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-primary-500 inline-block"></span>
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">{currentKey.replace(/_/g, ' ')}</h4>
          </div>
          <MermaidChart chart={output[currentKey]} />
          <details className="mt-4">
            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300">Show raw mermaid syntax</summary>
            <pre className="mt-2 text-[10px] text-gray-400 bg-gray-900 rounded p-3 overflow-auto border border-gray-800 font-mono">
              {output[currentKey]}
            </pre>
          </details>
        </div>
      ) : (
        <div className="space-y-4">
          {Array.isArray(output[currentKey]) ? (
            output[currentKey].map((item, i) => (
              <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors">
                {typeof item === 'object' && item !== null ? (
                  Object.entries(item).map(([k, v]) => (
                    <div key={k} className="mb-3 last:mb-0">
                      <span className="text-xs font-semibold text-primary-400 uppercase tracking-wider block mb-1">{k.replace(/_/g, ' ')}</span>
                      {renderValue(v)}
                    </div>
                  ))
                ) : <p className="text-sm text-gray-200">{item !== null ? String(item) : 'null'}</p>}
              </div>
            ))
          ) : renderValue(output[currentKey])}
        </div>
      )}
    </>
  );
}
