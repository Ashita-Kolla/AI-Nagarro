import { FileIcon } from '../icons.jsx';
import { DownloadList } from '../DownloadCard.jsx';

export function DeveloperOutputView({ agent, output, hasArtifacts }) {
  const files = output.files || {};
  const filePaths = Object.keys(files);
  const setup = output.setup_instructions || {};
  const steps = setup.steps || [];
  const envs = setup.environment_variables || [];

  return (
    <div className="space-y-6">
      {hasArtifacts && <DownloadList agentName={agent.name} artifacts={agent.artifacts} />}

      <div>
        <h3 className="text-sm font-semibold text-primary-400 uppercase tracking-wider mb-3">Generated Codebase ({filePaths.length} files)</h3>
        <div className="bg-gray-950 border border-gray-700 rounded-xl p-4 font-mono text-sm text-gray-300">
          {filePaths.length > 0 ? (
            <ul className="space-y-2">
              {filePaths.map((fp, i) => (
                <li key={i} className="flex items-center gap-2">
                  <FileIcon />
                  {fp}
                </li>
              ))}
            </ul>
          ) : <p className="text-gray-500 italic">No files generated.</p>}
        </div>
      </div>

      {steps.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-green-400 uppercase tracking-wider mb-3">Setup Instructions</h3>
          <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4">
            <ul className="space-y-2">
              {steps.map((step, i) => (
                <li key={i} className="text-sm text-gray-200 flex gap-3"><span className="text-green-500 shrink-0">›</span> {step}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {envs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-purple-400 uppercase tracking-wider mb-3">Environment Variables</h3>
          <div className="space-y-2">
            {envs.map((env, i) => (
              <div key={i} className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-purple-400 bg-purple-900/30 px-2 py-0.5 rounded border border-purple-800/50">{env.key}</span>
                </div>
                <p className="text-xs text-gray-300">{env.description}</p>
                {env.example && <p className="text-xs text-gray-500 mt-1 font-mono break-all">Example: {env.example}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
