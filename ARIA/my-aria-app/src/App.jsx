import { useEffect, useReducer, useRef, useState } from 'react';
import { reducer, initialState } from './constants.js';
import { AriaSocketContext, useAriaSocket } from './hooks/useAriaSocket.js';
import { ChatPanel } from './components/ChatPanel.jsx';
import { AgentPipeline } from './components/AgentPipeline.jsx';
import { LiveLogConsole } from './components/LiveLogConsole.jsx';
import { OutputModal } from './components/OutputModal.jsx';
import { Toast } from './components/Toast.jsx';

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [modalAgent, setModalAgent] = useState(null);
  const [brdNotification, setBrdNotification] = useState(null);
  const chatEndRef = useRef(null);
  const logEndRef = useRef(null);

  const { wsStatus, sendMessage } = useAriaSocket(dispatch, setBrdNotification);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [state.messages]);
  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [state.logs]);

  const startPipeline = (brief) => {
    dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'user', text: brief } });
    dispatch({ type: 'SET_INPUT', payload: '' });
    dispatch({ type: 'SET_FILE_PREVIEW', payload: null });
    dispatch({ type: 'ADD_LOG', payload: 'Sending brief to ARIA backend…' });
    sendMessage({ type: 'start', brief });
  };

  const handleSend = () => {
    if (!state.inputText.trim() && !state.filePreview) return;
    if (state.isEditing) {
      const correction = state.inputText;
      dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'user', text: correction } });
      dispatch({ type: 'END_EDIT' });
      sendMessage({ type: 'gate_action', action: 'Edit', agent: state.activeGate, correction });
    } else {
      let brief = state.inputText;
      if (state.filePreview) brief = `[Uploaded: ${state.filePreview.name}]\n\n` + brief;
      startPipeline(brief);
    }
  };

  const handleGateAction = (action) => {
    const agent = state.activeGate;
    if (action === 'Edit') {
      dispatch({ type: 'START_EDIT' });
      dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria', text: `Correction mode active for ${agent}. Type your feedback and press Send.` } });
    } else if (action === 'Approve') {
      // Safely tell backend to save user's edited scripts directly to disk
      const agentObj = state.agents.find(a => a.name === agent);
      if (agentObj) {
        if (agentObj.name === 'Environment' && agentObj._editedScript !== undefined) {
          sendMessage({ type: 'save_scripts', agent: 'Environment', script_content: agentObj._editedScript });
        } else if (agentObj.name === 'QA' && agentObj._editedQASuite !== undefined) {
          sendMessage({ type: 'save_scripts', agent: 'QA', test_suite: agentObj._editedQASuite });
        }
      }
      // Immediately send standard gate action - LangGraph routing is completely untouched!
      sendMessage({ type: 'gate_action', action, agent });
      dispatch({ type: 'UPDATE_AGENT', payload: { name: agent, status: 'complete' } });
      dispatch({ type: 'SET_GATE', payload: null });
      dispatch({ type: 'ADD_LOG', payload: `${agent} approved. Pipeline continuing...` });
    } else if (action === 'Regenerate') {
      sendMessage({ type: 'gate_action', action, agent });
      dispatch({ type: 'UPDATE_AGENT', payload: { name: agent, status: 'running', summary: 'Regenerating…' } });
      dispatch({ type: 'SET_GATE', payload: null });
    } else {
      sendMessage({ type: 'gate_action', action, agent });
    }
  };

  return (
    <AriaSocketContext.Provider value={{ wsStatus, sendMessage }}>
      <div className="flex flex-col lg:flex-row h-screen bg-gray-950 text-gray-100 font-sans overflow-hidden">
        <ChatPanel
          state={state}
          dispatch={dispatch}
          wsStatus={wsStatus}
          handleSend={handleSend}
          chatEndRef={chatEndRef}
        />

        <div className="flex-1 min-h-0 lg:flex-none lg:w-1/2 flex flex-col">
          <AgentPipeline
            agents={state.agents}
            activeGate={state.activeGate}
            expandedAgent={expandedAgent}
            setExpandedAgent={setExpandedAgent}
            setModalAgent={setModalAgent}
            wsStatus={wsStatus}
            threadId={state.thread_id}
            sendMessage={sendMessage}
            onGateAction={handleGateAction}
          />
          <LiveLogConsole logs={state.logs} logEndRef={logEndRef} />
        </div>

        {modalAgent && <OutputModal agent={modalAgent} onClose={() => setModalAgent(null)} />}

        {brdNotification && (
          <Toast
            notification={brdNotification}
            onOpenDownloads={() => { setModalAgent(state.agents.find(a => a.name === brdNotification.agent)); setBrdNotification(null); }}
            onDismiss={() => setBrdNotification(null)}
          />
        )}
      </div>
    </AriaSocketContext.Provider>
  );
}
