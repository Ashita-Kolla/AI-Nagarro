export function LiveLogConsole({ logs, logEndRef }) {
  return (
    <div className="h-44 border-t border-gray-800 bg-black p-4 overflow-y-auto font-mono text-[11px] leading-relaxed">
      <p className="text-gray-600 font-bold mb-2 tracking-widest uppercase text-[10px]">Live System Log</p>
      {logs.length === 0 && <p className="text-gray-700 italic">Waiting for pipeline to start...</p>}
      {logs.map(log => (
        <div key={log.id} className="flex gap-3 mb-0.5 hover:bg-gray-900/40 px-1 rounded">
          <span className="text-gray-600 shrink-0">[{log.time}]</span>
          <span className={log.text.toLowerCase().includes('warning') || log.text.toLowerCase().includes('warn') ? 'text-amber-400' : 'text-gray-300'}>{log.text}</span>
        </div>
      ))}
      <div ref={logEndRef} />
    </div>
  );
}
