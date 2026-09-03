import { createContext, useContext, useEffect, useRef, useState } from 'react';

export const AriaSocketContext = createContext(null);

export function useAriaSocketContext() {
  return useContext(AriaSocketContext);
}

/**
 * Owns the WebSocket connection lifecycle (connect, auto-reconnect every 4s,
 * status) and dispatches incoming server events into the reducer. Replaces
 * the old `window._wsRef` global escape hatch — sendMessage/wsStatus are
 * provided to descendants via AriaSocketContext instead.
 */
export function useAriaSocket(dispatch, setBrdNotification) {
  const [wsStatus, setWsStatus] = useState('connecting');
  const wsRef = useRef(null);

  useEffect(() => {
    connectWS();
    return () => { wsRef.current?.close(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function connectWS() {
    setWsStatus('connecting');
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus('connected');
      dispatch({ type: 'ADD_LOG', payload: 'Connected to ARIA backend (ws://localhost:8000).' });
    };
    ws.onclose = () => {
      setWsStatus('disconnected');
      dispatch({ type: 'ADD_LOG', payload: 'Backend disconnected. Retrying in 4s...' });
      setTimeout(connectWS, 4000);
    };
    ws.onerror = () => {
      setWsStatus('error');
      dispatch({ type: 'ADD_LOG', payload: 'Cannot reach backend. Start it with: uvicorn ws_server:app --port 8000' });
    };
    ws.onmessage = (evt) => {
      try { handleServerEvent(JSON.parse(evt.data)); }
      catch (e) { console.error('WS parse error', e); }
    };
  }

  function handleServerEvent(msg) {
    switch (msg.type) {
      case 'pipeline_started':
        dispatch({ type: 'SET_THREAD_ID', payload: msg.thread_id }); break;

      case 'log':
        dispatch({ type: 'ADD_LOG', payload: msg.message }); break;

      case 'supervisor_result': {
        const d = msg.data || {};
        const agents = (d.agents_required || []).join(' → ');
        const text = `${d.summary || ''}\n\nRouting: ${agents}\nConfidence: ${d.confidence_score ?? '?'}/100`;
        dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria', text } });
        break;
      }

      case 'agent_start':
        dispatch({ type: 'UPDATE_AGENT', payload: { name: msg.agent, status: 'running', summary: `Running ${msg.agent}…` } });
        break;

      case 'test_run_result':
        window.dispatchEvent(new CustomEvent('test_run_result', { detail: msg }));
        break;

      case 'test_run_single_result':
        window.dispatchEvent(new CustomEvent('test_run_single_result', { detail: msg }));
        break;

      case 'agent_output':
        dispatch({
          type: 'UPDATE_AGENT', payload: {
            name: msg.agent, status: 'waiting_approval',
            summary: msg.summary || `${msg.agent} output ready.`,
            score: msg.score ?? null, output: msg.data, warning: msg.warning || null,
          }
        });
        dispatch({
          type: 'ADD_MESSAGE', payload: {
            sender: 'aria',
            text: `${msg.agent} agent completed. Score: ${msg.score ?? 'N/A'}/100. Open the full output to review, then approve or edit.`
          }
        });
        break;

      case 'gate_required':
        dispatch({ type: 'SET_GATE', payload: msg.agent }); break;

      case 'agent_approved':
        dispatch({ type: 'UPDATE_AGENT', payload: { name: msg.agent, status: 'complete' } });
        dispatch({ type: 'SET_GATE', payload: null }); break;

      case 'artifacts_ready':
        dispatch({ type: 'UPDATE_AGENT', payload: { name: msg.agent, artifacts: msg.paths } });
        setBrdNotification({ agent: msg.agent, message: msg.message, paths: msg.paths });
        dispatch({ type: 'ADD_LOG', payload: msg.message });
        setTimeout(() => setBrdNotification(null), 8000);
        break;

      case 'pipeline_done':
        dispatch({
          type: 'ADD_MESSAGE', payload: {
            sender: 'aria',
            text: '✅ All agents completed. Full context saved to outputs/full_project_context.json.'
          }
        }); break;

      case 'error':
        dispatch({ type: 'ADD_LOG', payload: `ERROR: ${msg.message}` });
        dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria', text: `⚠️ ${msg.message}` } }); break;

      default: console.warn('Unknown WS event:', msg.type);
    }
  }

  const sendMessage = (payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
      return true;
    }
    dispatch({ type: 'ADD_LOG', payload: 'Cannot send — WebSocket not connected.' });
    return false;
  };

  return { wsStatus, sendMessage };
}
