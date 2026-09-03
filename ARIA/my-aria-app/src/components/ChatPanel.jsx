import { PaperclipIcon, SendIcon } from './icons.jsx';
import { ConnectionStatus } from './ConnectionStatus.jsx';

export function ChatPanel({ state, dispatch, wsStatus, handleSend, chatEndRef }) {
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) dispatch({ type: 'SET_FILE_PREVIEW', payload: { name: file.name, type: file.type } });
  };

  return (
    <div className="flex-1 min-h-0 lg:flex-none lg:w-1/2 flex flex-col border-b lg:border-b-0 lg:border-r border-gray-800 bg-gray-900/50">
      <div className="p-5 border-b border-gray-800 bg-gray-900/90 flex items-center justify-between">
        <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">ARIA Chatbot</h1>
        <ConnectionStatus wsStatus={wsStatus} />
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {state.messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center text-gray-600 gap-2">
            <p className="text-sm">Describe what you'd like built to get started.</p>
          </div>
        )}
        {state.messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[82%] p-4 rounded-md text-sm leading-relaxed whitespace-pre-wrap ${msg.sender === 'user'
                ? 'bg-primary-600/20 text-primary-100 border border-primary-500/25 rounded-br-sm'
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
              <div className="p-2 bg-primary-500/20 text-primary-400 rounded-lg"><PaperclipIcon /></div>
              <div>
                <p className="text-sm font-medium text-gray-200">{state.filePreview.name}</p>
                <p className="text-xs text-gray-500">Ready to include with brief</p>
              </div>
            </div>
            <button onClick={() => dispatch({ type: 'SET_FILE_PREVIEW', payload: null })} aria-label="Remove attached file" className="text-gray-500 hover:text-white focus-visible:ring-2 focus-visible:ring-primary-400 rounded outline-none">&times;</button>
          </div>
        )}
        <div className="flex items-end gap-2 bg-gray-950 p-2 rounded-md border border-gray-700/50 focus-within:border-primary-500/40 transition-colors">
          <div className="flex gap-1 pb-1 px-1">
            <label className="p-2 text-gray-500 hover:text-primary-400 hover:bg-gray-800 rounded-md cursor-pointer transition-colors focus-within:ring-2 focus-within:ring-primary-400">
              <PaperclipIcon />
              <input type="file" className="hidden" onChange={handleFileUpload} aria-label="Attach a file" />
            </label>
          </div>
          <textarea
            className="flex-1 bg-transparent border-none outline-none resize-none max-h-32 text-sm text-gray-200 placeholder-gray-600 py-3"
            rows={state.isEditing ? 3 : 1}
            placeholder={state.isEditing ? "Type your correction here..." : "Type your project brief..."}
            value={state.inputText}
            onChange={e => dispatch({ type: 'SET_INPUT', payload: e.target.value })}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
          />
          <button
            onClick={handleSend}
            aria-label="Send message"
            className={`p-3 rounded-md mb-1 mr-1 transition-all focus-visible:ring-2 focus-visible:ring-primary-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950 outline-none ${state.inputText.trim() || state.filePreview ? 'bg-primary-600 hover:bg-primary-500 text-white' : 'bg-gray-800 text-gray-600'}`}
          >
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  );
}
