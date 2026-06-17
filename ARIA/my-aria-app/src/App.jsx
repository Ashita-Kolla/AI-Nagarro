import React, { useState, useEffect, useReducer, useRef } from 'react';

// --- ICONS ---
const PaperclipIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>;
const MicIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/></svg>;
const SendIcon = () => <svg className="w-5 h-5 transform rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>;
const CheckCircleIcon = ({cls}) => <svg className={cls || "w-5 h-5 text-green-500"} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>;
const ClockIcon = ({cls}) => <svg className={cls || "w-5 h-5 text-amber-500"} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>;
const DotsIcon = () => <svg className="w-5 h-5 text-gray-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"/></svg>;
const ChevronDownIcon = () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"/></svg>;
const ChevronUpIcon = () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7"/></svg>;
const XIcon = () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/></svg>;
const ExternalLinkIcon = () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>;
const WarningIcon = () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>;

const AGENTS_LIST = ["BA", "Architect", "Developer", "QA", "DevOps", "PM", "Optimisation"];

// --- RICH MOCK OUTPUTS ---
const MOCK_OUTPUTS = {
  BA: {
    user_stories: [
      { id: "US-001", persona: "As a fitness enthusiast", story: "I want to register and log in so I can access my personalized workout and nutrition plans within 2 minutes", acceptance: ["Registration form loads in under 2 seconds on 4G", "Login displays username, password, and Remember Me checkbox", "Profile page renders on iPhone 12 (390px), iPad (768px), desktop (1440px)"] },
      { id: "US-002", persona: "As a trainer", story: "I want to create and assign workout plans to clients so I can manage multiple clients from one portal", acceptance: ["Plan creation form loads under 2 seconds on 4G", "Form includes name, description, exercises with sets and reps", "Client receives notification when plan is assigned"] },
      { id: "US-003 — US-006", persona: "Workout tracking · Nutrition · Payments · Analytics", story: "4 additional stories covering core feature areas. All with measurable acceptance criteria.", acceptance: ["All responsive across mobile, tablet, desktop", "All load times under 2-3 seconds on 4G"] },
    ],
    requirements: [
      { category: "Functional", items: ["User authentication with JWT tokens and refresh cycle", "Role-based access: Admin, Trainer, Client", "Dashboard with KPI widgets: active clients, plans, revenue", "Workout plan CRUD with exercise library (500+ exercises)", "Nutrition tracker with macro calculation engine", "Stripe payment integration for subscriptions"] },
      { category: "Non-Functional", items: ["99.9% uptime SLA", "WCAG 2.1 AA accessibility compliance", "GDPR compliant data storage and consent flow", "API response time < 300ms at p95", "Mobile-first responsive layout"] },
    ],
    assumptions: [
      "No existing codebase — greenfield project",
      "Target platforms: web only (mobile app out of scope for v1)",
      "Payment processing via Stripe (not custom PCI DSS)",
      "Initial launch: single region (EU-West)",
    ],
    supervisor_warning: "GDPR consent and notifications have no dedicated user stories. Consider editing before approving.",
  },
  Architect: {
    stack: { frontend: "React 18 + Vite + Tailwind CSS", backend: "FastAPI (Python 3.12)", database: "PostgreSQL 16 + Redis (caching)", auth: "JWT + OAuth2 (Google SSO)", hosting: "AWS ECS + RDS + CloudFront CDN" },
    components: [
      { name: "API Gateway", desc: "FastAPI with versioned routes (/api/v1/), rate limiting at 100 req/min per IP, CORS configured for frontend domain." },
      { name: "Auth Service", desc: "JWT with 15-min access tokens, 7-day refresh tokens stored as HttpOnly cookies. BCrypt password hashing." },
      { name: "Workout Engine", desc: "Service layer handling plan CRUD, exercise library queries, assignment notifications via Celery async tasks." },
      { name: "Notification Worker", desc: "Celery + Redis queue for email (SendGrid) and push notifications. Dead-letter queue with 3 retries." },
    ],
    decisions: ["PostgreSQL over MongoDB: relational structure suits workout plan assignments", "Redis for session caching to reduce DB load by ~40%", "Celery for async notifications to prevent API blocking"],
  },
};

// --- REDUCER ---
const initialState = {
  messages: [{ id: 1, sender: 'aria', text: 'Welcome to ARIA. Please provide your project brief or upload a document to begin.', time: new Date().toLocaleTimeString() }],
  agents: AGENTS_LIST.map(name => ({ name, status: 'pending', summary: '', score: null, output: null, warning: null })),
  logs: [],
  filePreview: null,
  activeGate: null,
  inputText: '',
  isEditing: false,
};

function reducer(state, action) {
  const timestamp = new Date().toLocaleTimeString();
  switch (action.type) {
    case 'ADD_MESSAGE': return { ...state, messages: [...state.messages, { id: Date.now(), time: timestamp, ...action.payload }] };
    case 'SET_INPUT': return { ...state, inputText: action.payload };
    case 'SET_FILE_PREVIEW': return { ...state, filePreview: action.payload };
    case 'ADD_LOG': return { ...state, logs: [...state.logs, { id: Date.now(), time: timestamp, text: action.payload }] };
    case 'UPDATE_AGENT': return { ...state, agents: state.agents.map(a => a.name === action.payload.name ? { ...a, ...action.payload } : a) };
    case 'SET_GATE': return { ...state, activeGate: action.payload };
    case 'START_EDIT': return { ...state, isEditing: true, inputText: `Correction for ${state.activeGate}: ` };
    case 'END_EDIT': return { ...state, isEditing: false, inputText: '' };
    default: return state;
  }
}

// =====================================================
// FULL OUTPUT MODAL
// =====================================================
function OutputModal({ agent, onClose }) {
  const [tab, setTab] = useState(0);
  const output = agent.output;
  const tabs = (typeof output === 'object' && output !== null && !Array.isArray(output))
    ? Object.keys(output).filter(k => !['supervisor_warning'].includes(k))
    : [];

  const renderValue = (val) => {
    if (Array.isArray(val)) return (
      <ul className="space-y-1 mt-1">
        {val.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
            <span className="text-blue-400 mt-0.5 shrink-0">›</span>
            <span>{typeof item === 'object' && item !== null ? JSON.stringify(item) : String(item)}</span>
          </li>
        ))}
      </ul>
    );
    if (typeof val === 'object' && val !== null) return (
      <div className="space-y-3 mt-2">
        {Object.entries(val).map(([k, v]) => (
          <div key={k} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider block mb-1">{k}</span>
            {renderValue(v)}
          </div>
        ))}
      </div>
    );
    return <p className="text-sm text-gray-200 mt-1">{String(val)}</p>;
  };

  // BA-specific rich render
  const renderBAOutput = (output) => {
    const tabNames = ['User Stories', 'Requirements', 'Assumptions', 'Raw JSON'];
    const baTab = tabNames[tab] || tabNames[0];

    const userStories = Array.isArray(output.user_stories) ? output.user_stories : [];
    const requirements = output.requirements || output.business_requirements || [];
    const assumptions = output.assumptions || [];

    return (
      <>
        <div className="flex gap-2 mb-6 border-b border-gray-700 pb-0">
          {tabNames.map((t, i) => (
            <button key={t} onClick={() => setTab(i)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors -mb-px ${tab === i ? 'border-blue-500 text-blue-400 bg-blue-500/5' : 'border-transparent text-gray-500 hover:text-gray-300'}`}>
              {t}
            </button>
          ))}
        </div>

        {baTab === 'User Stories' && (
          <div className="space-y-4">
            {userStories.length > 0 ? (
              userStories.map((us, i) => {
                if (!us || typeof us !== 'object') return null;
                const storyId = us.id || `US-${i + 1}`;
                const persona = us.persona || us.role || 'User';
                const storyText = us.story || (us.action ? `As a ${persona}, I want ${us.action}${us.benefit ? `, so that ${us.benefit}` : ''}` : '');
                
                const criteria = us.acceptance_criteria || us.acceptance || [];
                const criteriaArray = Array.isArray(criteria) ? criteria : [criteria];

                return (
                  <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-xs font-mono font-bold text-blue-400 bg-blue-900/30 px-2 py-0.5 rounded border border-blue-800/50">{storyId}</span>
                      <span className="text-xs text-gray-500 italic">{persona}</span>
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
            ) : (
              <p className="text-gray-500 text-sm">No user stories available.</p>
            )}
          </div>
        )}

        {baTab === 'Requirements' && (
          <div className="space-y-6">
            {Array.isArray(requirements) && requirements.length > 0 ? (
              requirements.map((req, i) => {
                if (typeof req === 'object' && req !== null) {
                  const category = req.category || 'System';
                  const items = Array.isArray(req.items) ? req.items : [req.items];
                  return (
                    <div key={i}>
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-indigo-500 inline-block"></span>
                        {category} Requirements
                      </h4>
                      <div className="space-y-2">
                        {items.map((item, j) => (
                          <div key={j} className="flex items-start gap-3 bg-gray-800/40 rounded-lg p-3 border border-gray-700/50">
                            <span className="text-indigo-400 mt-0.5 shrink-0">›</span>
                            <span className="text-sm text-gray-200">{String(item)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <div key={i} className="flex items-start gap-3 bg-gray-800/40 rounded-lg p-3 border border-gray-700/50">
                      <span className="text-indigo-400 mt-0.5 shrink-0">›</span>
                      <span className="text-sm text-gray-200">{String(req)}</span>
                    </div>
                  );
                }
              })
            ) : (
              <p className="text-gray-500 text-sm">No requirements specified.</p>
            )}
          </div>
        )}

        {baTab === 'Assumptions' && (
          <div className="space-y-3">
            {Array.isArray(assumptions) && assumptions.length > 0 ? (
              assumptions.map((a, i) => (
                <div key={i} className="flex items-start gap-3 bg-amber-900/10 rounded-lg p-4 border border-amber-800/30">
                  <span className="text-amber-500 font-bold shrink-0">!</span>
                  <span className="text-sm text-gray-200">{String(a)}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No assumptions listed.</p>
            )}
          </div>
        )}

        {baTab === 'Raw JSON' && (
          <pre className="text-xs text-green-400 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed">
            {JSON.stringify(output, null, 2)}
          </pre>
        )}
      </>
    );
  };

  // Generic rich render for non-BA agents
  const renderGenericOutput = (output) => {
    const isPlainObject = typeof output === 'object' && output !== null && !Array.isArray(output);

    if (!isPlainObject) {
      return (
        <pre className="text-sm text-gray-200 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed whitespace-pre-wrap">
          {typeof output === 'string' ? output : JSON.stringify(output, null, 2)}
        </pre>
      );
    }

    const tabNames = [...Object.keys(output), 'Raw JSON'];
    const currentKey = tabNames[tab] || 'Raw JSON';

    return (
      <>
        <div className="flex gap-2 mb-6 border-b border-gray-700 pb-0 flex-wrap">
          {tabNames.map((t, i) => (
            <button key={t} onClick={() => setTab(i)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors -mb-px capitalize ${tab === i ? 'border-blue-500 text-blue-400 bg-blue-500/5' : 'border-transparent text-gray-500 hover:text-gray-300'}`}>
              {t.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
        {currentKey === 'Raw JSON' ? (
          <pre className="text-xs text-green-400 bg-black/60 rounded-xl p-5 overflow-auto border border-gray-800 font-mono leading-relaxed">
            {JSON.stringify(output, null, 2)}
          </pre>
        ) : (
          <div className="space-y-4">
            {Array.isArray(output[currentKey]) ? (
              output[currentKey].map((item, i) => (
                <div key={i} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors">
                  {typeof item === 'object' && item !== null ? (
                    Object.entries(item).map(([k, v]) => (
                      <div key={k} className="mb-3 last:mb-0">
                        <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider block mb-1">{k.replace(/_/g, ' ')}</span>
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
  };

  const isBA = agent.name === 'BA' && (output?.user_stories || output?.business_requirements);

  return (
    <div className="fixed inset-0 z-50 flex items-stretch" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Drawer */}
      <div
        className="relative ml-auto w-full max-w-3xl bg-gray-900 border-l border-gray-700 flex flex-col shadow-2xl"
        onClick={e => e.stopPropagation()}
        style={{ animation: 'slideIn 0.25s ease-out' }}
      >
        {/* Header */}
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
              <span className={`text-xs font-mono px-3 py-1.5 rounded-lg border ${
                agent.score >= 80 ? 'bg-green-900/30 text-green-400 border-green-800' :
                agent.score >= 50 ? 'bg-amber-900/30 text-amber-400 border-amber-800' :
                'bg-red-900/30 text-red-400 border-red-800'
              }`}>Score: {agent.score}/100</span>
            )}
            <button onClick={onClose} className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
              <XIcon />
            </button>
          </div>
        </div>

        {/* Supervisor Warning Banner */}
        {agent.warning && (
          <div className="mx-6 mt-4 flex items-start gap-3 bg-amber-900/20 border border-amber-700/50 rounded-lg px-4 py-3 text-sm text-amber-300">
            <WarningIcon />
            <span>{agent.warning}</span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {output ? (
            isBA ? renderBAOutput(output) : renderGenericOutput(output)
          ) : (
            <p className="text-gray-500 text-sm">No output available.</p>
          )}
        </div>
      </div>

      <style>{`@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`}</style>
    </div>
  );
}

// =====================================================
// MAIN APP
// =====================================================
export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [modalAgent, setModalAgent] = useState(null);
  const [wsStatus, setWsStatus] = useState('connecting');
  const chatEndRef = useRef(null);
  const logEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [state.messages]);
  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [state.logs]);

  // ── WebSocket lifecycle ──────────────────────────────────────────────────
  useEffect(() => {
    connectWS();
    return () => { wsRef.current?.close(); };
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

  // ── Handle events pushed by Python backend ───────────────────────────────
  function handleServerEvent(msg) {
    switch (msg.type) {
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

      case 'agent_output':
        dispatch({ type: 'UPDATE_AGENT', payload: {
          name: msg.agent, status: 'waiting_approval',
          summary: msg.summary || `${msg.agent} output ready.`,
          score: msg.score ?? null, output: msg.data, warning: msg.warning || null,
        }});
        dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria',
          text: `${msg.agent} agent completed. Score: ${msg.score ?? 'N/A'}/100. Open the full output to review, then approve or edit.` } });
        break;

      case 'gate_required':
        dispatch({ type: 'SET_GATE', payload: msg.agent }); break;

      case 'agent_approved':
        dispatch({ type: 'UPDATE_AGENT', payload: { name: msg.agent, status: 'complete' } });
        dispatch({ type: 'SET_GATE', payload: null }); break;

      case 'pipeline_done':
        dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria',
          text: '✅ All agents completed. Full context saved to outputs/full_project_context.json.' } }); break;

      case 'error':
        dispatch({ type: 'ADD_LOG', payload: `ERROR: ${msg.message}` });
        dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria', text: `⚠️ ${msg.message}` } }); break;

      default: console.warn('Unknown WS event:', msg.type);
    }
  }

  // ── Send helpers ─────────────────────────────────────────────────────────
  const wsSend = (payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    } else {
      dispatch({ type: 'ADD_LOG', payload: 'Cannot send — WebSocket not connected.' });
    }
  };

  const startPipeline = (brief) => {
    dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'user', text: brief } });
    dispatch({ type: 'SET_INPUT', payload: '' });
    dispatch({ type: 'SET_FILE_PREVIEW', payload: null });
    dispatch({ type: 'ADD_LOG', payload: 'Sending brief to ARIA backend…' });
    wsSend({ type: 'start', brief });
  };

  const handleSend = () => {
    if (!state.inputText.trim() && !state.filePreview) return;
    if (state.isEditing) {
      const correction = state.inputText;
      dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'user', text: correction } });
      dispatch({ type: 'END_EDIT' });
      wsSend({ type: 'gate_action', action: 'Edit', agent: state.activeGate, correction });
    } else {
      let brief = state.inputText;
      if (state.filePreview) brief = `[Uploaded: ${state.filePreview.name}]\n\n` + brief;
      startPipeline(brief);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) dispatch({ type: 'SET_FILE_PREVIEW', payload: { name: file.name, type: file.type } });
  };

  const handleGateAction = (action) => {
    const agent = state.activeGate;
    if (action === 'Edit') {
      dispatch({ type: 'START_EDIT' });
      dispatch({ type: 'ADD_MESSAGE', payload: { sender: 'aria', text: `Correction mode active for ${agent}. Type your feedback and press Send.` } });
    } else {
      wsSend({ type: 'gate_action', action, agent });
      if (action === 'Regenerate') {
        dispatch({ type: 'UPDATE_AGENT', payload: { name: agent, status: 'running', summary: 'Regenerating…' } });
        dispatch({ type: 'SET_GATE', payload: null });
      }
    }
  };

  const completedCount = state.agents.filter(a => a.status === 'complete').length;
  const progressPercent = (completedCount / state.agents.length) * 100;

  const getScoreStyle = (score) => {
    if (!score) return 'bg-gray-800 text-gray-500 border-gray-700';
    if (score >= 80) return 'bg-green-900/30 text-green-400 border-green-800';
    if (score >= 50) return 'bg-amber-900/30 text-amber-400 border-amber-800';
    return 'bg-red-900/30 text-red-400 border-red-800';
  };

  const getStatusIcon = (status) => {
    if (status === 'complete') return <CheckCircleIcon />;
    if (status === 'running') return <div className="w-5 h-5 border-2 border-t-blue-500 border-gray-700 rounded-full animate-spin" />;
    if (status === 'waiting_approval') return <ClockIcon />;
    return <DotsIcon />;
  };

  const canOpenOutput = (agent) => (agent.status === 'complete' || agent.status === 'waiting_approval') && agent.output;

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 font-sans overflow-hidden">
      {/* ========== LEFT PANEL ========== */}
      <div className="w-1/2 flex flex-col border-r border-gray-800 bg-gray-900/50">
        <div className="p-5 border-b border-gray-800 bg-gray-900/90 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">ARIA Chatbot</h1>
          <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${
            wsStatus === 'connected'    ? 'bg-green-900/30 text-green-400 border-green-800' :
            wsStatus === 'connecting'   ? 'bg-amber-900/30 text-amber-400 border-amber-800' :
            wsStatus === 'error'        ? 'bg-red-900/30 text-red-400 border-red-800' :
                                         'bg-gray-800/50 text-gray-400 border-gray-700/50'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              wsStatus === 'connected'  ? 'bg-green-500 animate-pulse' :
              wsStatus === 'connecting' ? 'bg-amber-500 animate-pulse' :
                                         'bg-red-500'
            }`} />
            <span className="capitalize">{wsStatus === 'connected' ? 'Backend Connected' : wsStatus}</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {state.messages.map(msg => (
            <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[82%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-blue-600/20 text-blue-100 border border-blue-500/25 rounded-br-sm'
                  : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-bl-sm'
              }`}>
                {msg.text}
              </div>
              <span className="text-[10px] text-gray-600 mt-1 px-1">{msg.time}</span>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="p-5 bg-gray-900 border-t border-gray-800">
          {state.filePreview && (
            <div className="mb-3 p-3 bg-gray-800 border border-gray-700 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg"><PaperclipIcon /></div>
                <div>
                  <p className="text-sm font-medium text-gray-200">{state.filePreview.name}</p>
                  <p className="text-xs text-gray-500">Ready to include with brief</p>
                </div>
              </div>
              <button onClick={() => dispatch({ type: 'SET_FILE_PREVIEW', payload: null })} className="text-gray-500 hover:text-white">&times;</button>
            </div>
          )}
          <div className="flex items-end gap-2 bg-gray-950 p-2 rounded-2xl border border-gray-700/50 focus-within:border-blue-500/40 transition-colors">
            <div className="flex gap-1 pb-1 px-1">
              <label className="p-2 text-gray-500 hover:text-blue-400 hover:bg-gray-800 rounded-xl cursor-pointer transition-colors">
                <PaperclipIcon />
                <input type="file" className="hidden" onChange={handleFileUpload} />
              </label>
              <button className="p-2 text-gray-500 hover:text-blue-400 hover:bg-gray-800 rounded-xl transition-colors"><MicIcon /></button>
            </div>
            <textarea
              className="flex-1 bg-transparent border-none outline-none resize-none max-h-32 text-sm text-gray-200 placeholder-gray-600 py-3"
              rows={state.isEditing ? 3 : 1}
              placeholder={state.isEditing ? "Type your correction here..." : "Type your project brief..."}
              value={state.inputText}
              onChange={e => dispatch({ type: 'SET_INPUT', payload: e.target.value })}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            />
            <button onClick={handleSend} className={`p-3 rounded-xl mb-1 mr-1 transition-all ${state.inputText.trim() || state.filePreview ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-gray-800 text-gray-600'}`}>
              <SendIcon />
            </button>
          </div>
        </div>
      </div>

      {/* ========== RIGHT PANEL ========== */}
      <div className="w-1/2 flex flex-col">
        <div className="p-5 border-b border-gray-800 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-100">Agent Operations</h2>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-gray-400">System active</span>
          </div>
        </div>

        {/* Progress */}
        <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/20">
          <div className="flex justify-between text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">
            <span>Pipeline Progress</span>
            <span>{completedCount} / {state.agents.length} agents</span>
          </div>
          <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-700 ease-out rounded-full" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>

        {/* Agent List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-2">
          {state.agents.map(agent => (
            <div key={agent.name}>
              {/* Agent Row */}
              <div className={`rounded-xl border px-4 py-3 transition-all ${
                agent.status === 'running' ? 'bg-gray-800/60 border-blue-500/40 shadow-[0_0_12px_rgba(59,130,246,0.08)]' :
                agent.status === 'waiting_approval' ? 'bg-amber-900/10 border-amber-500/30' :
                agent.status === 'complete' ? 'bg-gray-900 border-gray-700' :
                'bg-gray-950 border-gray-800/40 opacity-40'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-6 flex justify-center shrink-0">{getStatusIcon(agent.status)}</div>
                    <div>
                      <p className="text-sm font-semibold text-gray-200">{agent.name} {agent.status === 'waiting_approval' ? 'agent' : agent.status === 'complete' ? 'agent' : ''}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{agent.summary || (agent.status === 'pending' ? 'Queued — waiting in pipeline' : 'Initialising...')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {agent.score !== null && (
                      <span className={`text-xs font-mono px-2 py-0.5 rounded border ${getScoreStyle(agent.score)}`}>Score: {agent.score}</span>
                    )}
                    {canOpenOutput(agent) && (
                      <button
                        onClick={() => setModalAgent(agent)}
                        className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white border border-gray-700 rounded-lg transition-colors font-medium"
                      >
                        <ExternalLinkIcon />
                        Open full output
                      </button>
                    )}
                    {agent.status === 'complete' && (
                      <button onClick={() => setExpandedAgent(expandedAgent === agent.name ? null : agent.name)} className="text-gray-500 hover:text-gray-300 p-1">
                        {expandedAgent === agent.name ? <ChevronUpIcon /> : <ChevronDownIcon />}
                      </button>
                    )}
                  </div>
                </div>

                {/* Supervisor warning inline */}
                {agent.warning && (
                  <div className="mt-3 flex items-start gap-2 bg-amber-900/15 border border-amber-700/30 rounded-lg px-3 py-2 text-xs text-amber-400">
                    <WarningIcon />
                    <span>{agent.warning}</span>
                  </div>
                )}

                {/* Inline Human Gate controls */}
                {state.activeGate === agent.name && (
                  <div className="mt-4 pt-3 border-t border-amber-500/20">
                    <div className="flex items-center gap-2 mb-3">
                      <ClockIcon cls="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-bold text-amber-400">Human Gate Approval Required</span>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => handleGateAction('Approve')} className="flex-1 py-1.5 bg-green-700 hover:bg-green-600 text-white text-xs font-semibold rounded-lg transition-colors">
                        ✓ Approve
                      </button>
                      <button onClick={() => handleGateAction('Edit')} className="flex-1 py-1.5 bg-blue-700 hover:bg-blue-600 text-white text-xs font-semibold rounded-lg transition-colors">
                        ✎ Edit
                      </button>
                      <button onClick={() => handleGateAction('Regenerate')} className="flex-1 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold rounded-lg transition-colors">
                        ↺ Regenerate
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Inline quick-preview (collapsed) */}
              {expandedAgent === agent.name && agent.output && (
                <div className="ml-9 mt-1 mb-1 p-4 bg-gray-900 rounded-xl border border-gray-800">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">Quick Summary</p>
                    <button onClick={() => setModalAgent(agent)} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
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
          ))}
        </div>

        {/* Live Log */}
        <div className="h-44 border-t border-gray-800 bg-black p-4 overflow-y-auto font-mono text-[11px] leading-relaxed">
          <p className="text-gray-600 font-bold mb-2 tracking-widest uppercase text-[10px]">Live System Log</p>
          {state.logs.length === 0 && <p className="text-gray-700 italic">Waiting for pipeline to start...</p>}
          {state.logs.map(log => (
            <div key={log.id} className="flex gap-3 mb-0.5 hover:bg-gray-900/40 px-1 rounded">
              <span className="text-gray-600 shrink-0">[{log.time}]</span>
              <span className={log.text.toLowerCase().includes('warning') || log.text.toLowerCase().includes('warn') ? 'text-amber-400' : 'text-gray-300'}>{log.text}</span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </div>

      {/* Full Output Modal */}
      {modalAgent && <OutputModal agent={modalAgent} onClose={() => setModalAgent(null)} />}

      <style>{`@keyframes shimmer { 100% { transform: translateX(500%); } }`}</style>
    </div>
  );
}
