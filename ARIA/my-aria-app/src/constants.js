export const AGENTS_LIST = ["BA", "Architect", "Planner", "Developer", "Environment", "QA", "DevOps", "PM", "Optimisation"];

export const initialState = {
  messages: [{ id: 1, sender: 'aria', text: 'Welcome to ARIA. Please provide your project brief or upload a document to begin.', time: new Date().toLocaleTimeString() }],
  agents: AGENTS_LIST.map(name => ({ name, status: 'pending', summary: '', score: null, output: null, warning: null })),
  logs: [],
  filePreview: null,
  activeGate: null,
  inputText: '',
  isEditing: false,
  thread_id: null,
};

export function reducer(state, action) {
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
    case 'SET_THREAD_ID': return { ...state, thread_id: action.payload };
    default: return state;
  }
}
