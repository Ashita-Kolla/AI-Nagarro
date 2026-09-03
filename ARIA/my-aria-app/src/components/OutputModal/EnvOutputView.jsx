export function EnvOutputView({ envScript, setEnvScript, testRunLog, isTestRunning, onTestRun }) {
  return (
    <div className="flex flex-col h-full gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-300">Generated Setup Script</h3>
        <button onClick={onTestRun} disabled={isTestRunning} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors">
          {isTestRunning ? 'Running...' : '▶ Test Run Script'}
        </button>
      </div>
      <textarea value={envScript} onChange={(e) => setEnvScript(e.target.value)} className="w-full h-64 bg-gray-950 border border-gray-700 rounded-lg p-4 font-mono text-sm text-green-400" spellCheck={false} />
      {testRunLog && (
        <pre className={`w-full max-h-64 overflow-auto rounded-lg p-4 font-mono text-xs border ${testRunLog.includes('[FAIL]') ? 'bg-red-900/10 border-red-800/50 text-red-300' : 'bg-green-900/10 border-green-800/50 text-green-300'}`}>{testRunLog}</pre>
      )}
    </div>
  );
}
