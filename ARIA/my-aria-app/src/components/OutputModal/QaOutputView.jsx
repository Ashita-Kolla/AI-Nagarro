import { FileIcon } from '../icons.jsx';
import { DownloadList } from '../DownloadCard.jsx';

export function QaOutputView({
  agent, hasArtifacts, qaTestSuites, updateQaTestCode,
  testRunLog, isTestRunning, onTestRunAll,
  singleTestLogs, runningSingleTests, onTestRunSingle,
}) {
  return (
    <div className="flex flex-col h-full gap-6">
      {hasArtifacts && <DownloadList agentName={agent.name} artifacts={agent.artifacts} />}

      <div className="flex items-center justify-between sticky top-0 bg-gray-900 pb-2 z-10">
        <h3 className="text-sm font-semibold text-gray-300">Python Test Suite ({qaTestSuites.length} files)</h3>
        <button onClick={onTestRunAll} disabled={isTestRunning} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors">
          {isTestRunning ? 'Running tests...' : '▶ Test Run Scripts'}
        </button>
      </div>
      {testRunLog && (
        <pre className={`w-full max-h-64 overflow-auto rounded-lg p-4 font-mono text-xs border ${testRunLog.includes('[FAIL]') ? 'bg-red-900/10 border-red-800/50 text-red-300' : 'bg-green-900/10 border-green-800/50 text-green-300'}`}>{testRunLog}</pre>
      )}
      {qaTestSuites.map((test, idx) => (
        <div key={idx} className="bg-gray-800/60 border border-gray-700 rounded-xl overflow-hidden flex flex-col">
          <div className="flex items-center justify-between bg-gray-800 px-4 py-3 border-b border-gray-700">
            <div className="text-sm font-mono text-gray-300 flex items-center gap-2">
              <FileIcon />
              {test.file}
            </div>
            <button
              onClick={() => onTestRunSingle(test.file, test.code)}
              disabled={runningSingleTests[test.file]}
              className="flex items-center gap-1 px-3 py-1.5 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white text-xs font-semibold rounded transition-colors"
            >
              {runningSingleTests[test.file] ? 'Running...' : '▶ Run Code'}
            </button>
          </div>

          <div className="flex flex-col xl:flex-row h-96">
            <textarea
              value={test.code}
              onChange={(e) => updateQaTestCode(idx, e.target.value)}
              className="w-full xl:w-1/2 h-full bg-gray-950 border-r border-gray-700 p-4 font-mono text-xs text-green-400 resize-none outline-none focus:bg-gray-900/50 transition-colors"
              spellCheck={false}
            />
            <div className="w-full xl:w-1/2 h-full bg-black p-4 overflow-y-auto font-mono text-xs">
              {singleTestLogs[test.file] ? (
                <div>
                  <div className={`mb-2 font-bold ${singleTestLogs[test.file].status === 'PASS' ? 'text-green-500' : 'text-red-500'}`}>
                    Status: {singleTestLogs[test.file].status}
                  </div>
                  <pre className="text-gray-400 whitespace-pre-wrap leading-relaxed">{singleTestLogs[test.file].log}</pre>
                </div>
              ) : (
                <div className="text-gray-600 flex items-center h-full justify-center text-center px-4">
                  {runningSingleTests[test.file] ? "Executing..." : "Click 'Run Code' to execute this test and view output here."}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
