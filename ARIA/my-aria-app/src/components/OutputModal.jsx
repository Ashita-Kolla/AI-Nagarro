import { useEffect, useState } from 'react';
import { CheckCircleIcon, WarningIcon, XIcon } from './icons.jsx';
import { useAriaSocketContext } from '../hooks/useAriaSocket.js';
import { BaOutputView } from './OutputModal/BaOutputView.jsx';
import { DeveloperOutputView } from './OutputModal/DeveloperOutputView.jsx';
import { GenericOutputView } from './OutputModal/GenericOutputView.jsx';
import { EnvOutputView } from './OutputModal/EnvOutputView.jsx';
import { QaOutputView } from './OutputModal/QaOutputView.jsx';

export function OutputModal({ agent, onClose }) {
  const { sendMessage } = useAriaSocketContext();
  const [tab, setTab] = useState(0);
  const output = agent.output;
  const hasArtifacts = agent.artifacts && agent.artifacts.length > 0;

  useEffect(() => {
    const handleKeyDown = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const [envScript, setEnvScript] = useState('');
  const [qaTestSuites, setQaTestSuites] = useState([]);
  const [testRunLog, setTestRunLog] = useState(null);
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [singleTestLogs, setSingleTestLogs] = useState({});
  const [runningSingleTests, setRunningSingleTests] = useState({});

  useEffect(() => {
    if (agent.name === 'Environment' && output && output.setup_commands) {
      setEnvScript(output.setup_commands.join('\n'));
    }
    if (agent.name === 'QA' && output && output.test_suite) {
      setQaTestSuites(output.test_suite);
    }
  }, [agent.name, output]);

  const handleTestRunScript = () => {
    if (!envScript.trim()) return;
    setIsTestRunning(true);
    setTestRunLog("Starting test run...");
    const sent = sendMessage({ type: 'test_run_script', script_content: envScript });
    if (!sent) {
      setTestRunLog("WebSocket not connected.");
      setIsTestRunning(false);
    }
  };

  const handleTestRunQa = () => {
    if (qaTestSuites.length === 0) return;
    setIsTestRunning(true);
    setTestRunLog("Running fast local Python tests...");
    const sent = sendMessage({ type: 'test_run_qa', test_suite: qaTestSuites });
    if (!sent) {
      setTestRunLog("WebSocket not connected.");
      setIsTestRunning(false);
    }
  };

  const handleTestRunSingle = (filename, code) => {
    setRunningSingleTests(prev => ({ ...prev, [filename]: true }));
    setSingleTestLogs(prev => ({ ...prev, [filename]: null }));
    sendMessage({ type: 'test_run_single_qa', filename, code });
  };

  const updateQaTestCode = (index, newCode) => {
    const updated = [...qaTestSuites];
    updated[index] = { ...updated[index], code: newCode };
    setQaTestSuites(updated);
  };

  useEffect(() => {
    const handleTestResult = (e) => {
      setIsTestRunning(false);
      setTestRunLog(`[${e.detail.status}]\n${e.detail.log}`);
    };
    const handleSingleTestResult = (e) => {
      const { filename, status, log } = e.detail;
      setRunningSingleTests(prev => ({ ...prev, [filename]: false }));
      setSingleTestLogs(prev => ({ ...prev, [filename]: { status, log } }));
    };
    window.addEventListener('test_run_result', handleTestResult);
    window.addEventListener('test_run_single_result', handleSingleTestResult);
    return () => {
      window.removeEventListener('test_run_result', handleTestResult);
      window.removeEventListener('test_run_single_result', handleSingleTestResult);
    };
  }, []);

  const isBA = agent.name === 'BA' && (output?.user_stories || output?.business_requirements || output?.functional_requirements);
  const isEnv = agent.name === 'Environment';
  const isQA = agent.name === 'QA';
  const isDeveloper = agent.name === 'Developer';

  // Expose edited data to parent component for Approve action
  useEffect(() => {
    if (isEnv) agent._editedScript = envScript;
    if (isQA) agent._editedQASuite = qaTestSuites;
  }, [isEnv, envScript, isQA, qaTestSuites, agent]);

  let tabsKeys = [];
  if (typeof output === 'object' && output !== null && !Array.isArray(output)) {
    tabsKeys = Object.keys(output).filter(k => !['supervisor_warning'].includes(k));
  }
  if (hasArtifacts) {
    tabsKeys.unshift('Downloads');
  }

  return (
    <div className="fixed inset-0 z-50 flex items-stretch" onClick={onClose} role="dialog" aria-modal="true" aria-label={`${agent.name} agent full output`}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <div
        className="relative ml-auto w-full max-w-3xl bg-gray-900 border-l border-gray-700 flex flex-col shadow-2xl shadow-black/50"
        onClick={e => e.stopPropagation()}
        style={{ animation: 'slideIn 0.25s ease-out' }}
      >
        <div className="p-6 border-b border-gray-800 flex items-center justify-between bg-gray-900/80 backdrop-blur-sm sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <CheckCircleIcon cls="w-5 h-5 text-green-400" />
              <h2 className="text-lg font-bold text-gray-100">{agent.name} Agent — Full Output</h2>
            </div>
            <p className="text-xs text-gray-500">{agent.summary}</p>
          </div>
          <div className="flex items-center gap-3">
            {agent.score !== null && (
              <span className={`text-xs font-mono px-3 py-1.5 rounded-lg border ${agent.score >= 80 ? 'bg-green-900/30 text-green-400 border-green-800' :
                  agent.score >= 50 ? 'bg-amber-900/30 text-amber-400 border-amber-800' :
                    'bg-red-900/30 text-red-400 border-red-800'
                }`}>Score: {agent.score}/100</span>
            )}
            <button onClick={onClose} aria-label="Close output panel" className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-primary-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-900 outline-none">
              <XIcon />
            </button>
          </div>
        </div>

        {agent.warning && (
          <div className="mx-6 mt-4 flex items-start gap-3 bg-amber-900/20 border border-amber-700/50 rounded-lg px-4 py-3 text-sm text-amber-300">
            <WarningIcon />
            <span>{agent.warning}</span>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6">
          {output ? (
            isBA ? <BaOutputView agent={agent} output={output} hasArtifacts={hasArtifacts} tab={tab} setTab={setTab} /> :
              isEnv ? (
                <EnvOutputView
                  envScript={envScript} setEnvScript={setEnvScript}
                  testRunLog={testRunLog} isTestRunning={isTestRunning}
                  onTestRun={handleTestRunScript}
                />
              ) : isQA && qaTestSuites.length > 0 ? (
                <QaOutputView
                  agent={agent} hasArtifacts={hasArtifacts}
                  qaTestSuites={qaTestSuites} updateQaTestCode={updateQaTestCode}
                  testRunLog={testRunLog} isTestRunning={isTestRunning} onTestRunAll={handleTestRunQa}
                  singleTestLogs={singleTestLogs} runningSingleTests={runningSingleTests}
                  onTestRunSingle={handleTestRunSingle}
                />
              ) : isDeveloper ? <DeveloperOutputView agent={agent} output={output} hasArtifacts={hasArtifacts} /> :
                <GenericOutputView agent={agent} output={output} hasArtifacts={hasArtifacts} tab={tab} setTab={setTab} tabsKeys={tabsKeys} />
          ) : (
            <p className="text-gray-500 text-sm">No output available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
