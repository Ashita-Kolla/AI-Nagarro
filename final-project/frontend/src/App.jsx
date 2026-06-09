import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, PlusCircle, MessageSquare, AlertCircle, CheckCircle2, Ticket, Bot, User, LayoutDashboard, Settings, HelpCircle, Activity, BarChart3, Clock, ChevronRight } from 'lucide-react';

const DEPARTMENT_COLORS = {
  HR: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  IT: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  Finance: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
  QA: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  PM: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  Escalated: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  System: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
};

const PRIORITY_COLORS = {
  low: 'text-slate-400 bg-slate-500/10 border-slate-500/20',
  medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  high: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
};

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'dashboard', 'tickets'
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [context, setContext] = useState(null);

  // Ticket Memory State
  const [tickets, setTickets] = useState(() => {
    const saved = localStorage.getItem('Nagarro_tickets');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
    return [];
  });

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (activeTab === 'chat') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, activeTab]);

  const handleSend = async (e, textOverride = null) => {
    e?.preventDefault();
    const textToSend = textOverride || input;
    if (!textToSend.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: textToSend,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textOverride) setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('https://ashitakolla.app.n8n.cloud/webhook/service-desk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend, context: context }),
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with service desk.');
      }

      const data = await response.json();

      // Handle Context for KB Solution
      if (data.status === 'kb_solution') {
        setContext({
          awaiting_confirmation: data.awaiting_confirmation,
          issue: data.issue,
          department: data.department,
          summary: data.summary,
          priority: data.priority
        });
      } else {
        setContext(null);
      }

      // Save created tickets to memory
      if (data.status === 'ticket_created') {
        const newTicket = {
          id: `TKT-${Math.floor(1000 + Math.random() * 9000)}`,
          department: data.department || 'System',
          priority: data.priority || 'medium',
          summary: data.summary || 'General request',
          status: 'Open',
          createdAt: new Date().toISOString()
        };

        setTickets(prev => {
          const updated = [newTicket, ...prev];
          localStorage.setItem('Nagarro_tickets', JSON.stringify(updated));
          return updated;
        });
      }

      const agentMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        timestamp: new Date().toISOString(),
        ...data,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          type: 'error',
          content: 'Failed to connect to the service desk. Please try again later.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const extractMessageText = (rawMsg) => {
    if (!rawMsg) return '';
    if (typeof rawMsg === 'object') {
      return rawMsg.message || rawMsg.text || JSON.stringify(rawMsg);
    }
    try {
      const parsed = JSON.parse(rawMsg);
      if (parsed && typeof parsed === 'object') {
        return parsed.message || parsed.text || rawMsg;
      }
    } catch (e) {
      // Not JSON, return as is
    }
    return rawMsg;
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderAgentResponse = (msg) => {
    const deptColor = DEPARTMENT_COLORS[msg.department] || DEPARTMENT_COLORS.System;

    if (msg.status === 'ticket_created') {
      return (
        <div className="flex flex-col space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-[11px] font-semibold tracking-wide uppercase text-slate-300 bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">
              Ticket Created
            </span>
            {msg.priority && (
              <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${PRIORITY_COLORS[msg.priority.toLowerCase()] || 'text-slate-400 bg-slate-800 border-slate-700'}`}>
                {msg.priority} Priority
              </span>
            )}
          </div>
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4 mt-2 flex items-start space-x-3 shadow-sm">
            <div className="bg-blue-500/20 p-2 rounded-lg">
              <Ticket className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-200">Ticket successfully logged</p>
              <p className="text-sm text-slate-400 mt-1 leading-relaxed">{msg.summary}</p>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('tickets')}
            className="text-[13px] font-medium text-blue-400 hover:text-blue-300 flex items-center mt-2 w-fit"
          >
            View in My Tickets <ChevronRight className="w-3 h-3 ml-1" />
          </button>
        </div>
      );
    }

    if (msg.status === 'email_sent') {
      return (
        <div className="flex flex-col space-y-3">
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-[11px] font-semibold tracking-wide uppercase text-slate-300 bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">
              Email Sent
            </span>
          </div>
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4 mt-2 flex items-start space-x-3 shadow-sm">
            <div className="bg-emerald-500/20 p-2 rounded-lg">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-200">Email delivered successfully</p>
              <p className="text-sm text-slate-400 mt-1 leading-relaxed">Check your inbox for further details.</p>
            </div>
          </div>
        </div>
      );
    }

    if (msg.status === 'clarification_needed') {
      const displayText = extractMessageText(msg.message);
      return (
        <div className="flex flex-col space-y-3 w-full">
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-[11px] font-semibold tracking-wide uppercase text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/20">
              Clarification Needed
            </span>
          </div>
          <p className="text-slate-200 text-[15px] leading-relaxed mt-2 whitespace-pre-wrap">{displayText}</p>
          <div className="mt-2 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 flex items-start space-x-2 w-fit">
            <AlertCircle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
            <p className="text-[13px] text-slate-300">Please reply in the chat below with the requested details to proceed.</p>
          </div>
        </div>
      );
    }

    if (msg.status === 'escalated') {
      return (
        <div className="flex flex-col space-y-3">
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${DEPARTMENT_COLORS.Escalated}`}>
              Escalated
            </span>
            {msg.confidence && (
              <span className="text-[11px] font-medium text-slate-400 bg-slate-800/50 px-2 py-1 rounded-md">
                Confidence: {(msg.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 mt-2 flex items-start space-x-3 shadow-sm">
            <div className="bg-amber-500/20 p-2 rounded-lg">
              <AlertCircle className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-amber-500">Request Escalated</p>
              <p className="text-sm text-amber-500/80 mt-1 leading-relaxed">{msg.reason}</p>
            </div>
          </div>
        </div>
      );
    }

    if (msg.status === 'completed') {
      return (
        <div className="flex flex-col space-y-3">
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${DEPARTMENT_COLORS.System}`}>
              Completed
            </span>
            <span className="text-[11px] font-medium text-slate-400 bg-slate-800/50 px-2 py-1 rounded-md">
              Action: {msg.action}
            </span>
          </div>
          <p className="text-slate-200 text-[15px] leading-relaxed mt-2">{msg.message}</p>
        </div>
      );
    }

    if (msg.status === 'kb_solution') {
      return (
        <div className="flex flex-col space-y-3 w-full">
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 text-[11px] font-semibold tracking-wide uppercase border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-[11px] font-semibold tracking-wide uppercase text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md border border-blue-500/20">
              Suggested Solution
            </span>
          </div>
          <p className="text-slate-200 text-[15px] leading-relaxed mt-2">{msg.message}</p>
          {msg.steps && msg.steps.length > 0 && (
            <div className="bg-[#1a1f2c] border border-slate-700/50 rounded-xl p-5 mt-3 shadow-inner">
              <h4 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Resolution Steps</h4>
              <ul className="list-decimal list-inside text-[14px] text-slate-300 space-y-2.5">
                {msg.steps.map((step, idx) => (
                  <li key={idx} className="pl-2 marker:text-slate-500 marker:font-medium leading-relaxed">{step}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-5 pt-4 border-t border-slate-700/50">
            <p className="text-sm text-slate-300 font-medium mb-3">
              Did this resolve your issue?
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => handleSend(null, "fixed")}
                disabled={isLoading}
                className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:border-emerald-500/50 rounded-lg transition-all duration-200 text-sm font-medium disabled:opacity-50"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Yes, fixed</span>
              </button>
              <button
                onClick={() => handleSend(null, "still broken")}
                disabled={isLoading}
                className="flex items-center space-x-2 px-4 py-2.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:border-amber-500/50 rounded-lg transition-all duration-200 text-sm font-medium disabled:opacity-50"
              >
                <AlertCircle className="w-4 h-4" />
                <span>No, still broken</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    const displayText = extractMessageText(msg.message || msg.content || '');
    return (
      <div className="flex flex-col space-y-2">
        {displayText && (
          <p className="text-slate-200 text-[15px] leading-relaxed whitespace-pre-wrap">
            {displayText}
          </p>
        )}
        <details className={displayText ? "mt-2" : ""}>
          <summary className="text-[11px] text-slate-500 cursor-pointer hover:text-slate-400 w-fit">View raw data</summary>
          <p className="text-slate-400 text-[11px] font-mono bg-slate-900/50 p-3 rounded-lg overflow-x-auto mt-2">
            {JSON.stringify(msg, null, 2)}
          </p>
        </details>
      </div>
    );
  };

  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Views Component
  const renderContent = () => {
    if (activeTab === 'dashboard') {
      const openTicketsCount = tickets.filter(t => t.status === 'Open').length;

      return (
        <div className="flex-1 overflow-y-auto p-4 md:p-8 z-10 scroll-smooth animate-in fade-in">
          <div className="max-w-6xl mx-auto space-y-6">
            <h2 className="text-2xl font-semibold text-slate-100">Dashboard</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[#151b26] border border-slate-700/50 p-6 rounded-2xl shadow-sm hover:border-blue-500/30 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-400">Total Tickets</p>
                    <p className="text-3xl font-bold text-slate-100 mt-2">{tickets.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center">
                    <Activity className="w-6 h-6 text-blue-400" />
                  </div>
                </div>
              </div>

              <div className="bg-[#151b26] border border-slate-700/50 p-6 rounded-2xl shadow-sm hover:border-amber-500/30 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-400">Open Issues</p>
                    <p className="text-3xl font-bold text-amber-400 mt-2">{openTicketsCount}</p>
                  </div>
                  <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-amber-400" />
                  </div>
                </div>
              </div>

              <div className="bg-[#151b26] border border-slate-700/50 p-6 rounded-2xl shadow-sm hover:border-emerald-500/30 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-400">Resolved</p>
                    <p className="text-3xl font-bold text-emerald-400 mt-2">{tickets.length - openTicketsCount}</p>
                  </div>
                  <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-[#151b26] border border-slate-700/50 rounded-2xl p-6 shadow-sm mt-8">
              <div className="flex items-center space-x-2 mb-6">
                <BarChart3 className="w-5 h-5 text-slate-400" />
                <h3 className="text-lg font-semibold text-slate-200">Recent Activity</h3>
              </div>
              {tickets.length > 0 ? (
                <div className="space-y-4">
                  {tickets.slice(0, 5).map((ticket) => (
                    <div key={ticket.id} className="flex items-center justify-between p-4 bg-slate-800/40 rounded-xl border border-slate-700/50 hover:bg-slate-800/60 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className={`w-2 h-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)] ${ticket.status === 'Open' ? 'bg-amber-400 shadow-amber-400/50' : 'bg-emerald-400 shadow-emerald-400/50'}`}></div>
                        <div>
                          <p className="text-sm font-medium text-slate-200">{ticket.summary}</p>
                          <p className="text-[11px] text-slate-500 mt-1">Logged on {formatDate(ticket.createdAt)}</p>
                        </div>
                      </div>
                      <span className={`px-2.5 py-1 text-[10px] font-semibold uppercase rounded-md border ${DEPARTMENT_COLORS[ticket.department] || DEPARTMENT_COLORS.System}`}>
                        {ticket.department}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-12 text-center text-slate-500 flex flex-col items-center">
                  <Activity className="w-10 h-10 mb-3 opacity-20" />
                  <p>No activity yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (activeTab === 'tickets') {
      return (
        <div className="flex-1 overflow-y-auto p-4 md:p-8 z-10 scroll-smooth animate-in fade-in">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-slate-100">My Tickets</h2>
              <button
                onClick={() => {
                  if (confirm('Clear all local ticket history?')) {
                    setTickets([]);
                    localStorage.removeItem('Nagarro_tickets');
                  }
                }}
                className="px-3 py-1.5 text-xs font-medium text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-lg transition-colors border border-transparent hover:border-rose-500/20"
              >
                Clear History
              </button>
            </div>

            <div className="bg-[#151b26] border border-slate-700/50 rounded-2xl shadow-sm overflow-hidden">
              {tickets.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700/50">
                      <tr>
                        <th className="px-6 py-4 font-semibold">ID</th>
                        <th className="px-6 py-4 font-semibold">Department</th>
                        <th className="px-6 py-4 font-semibold">Priority</th>
                        <th className="px-6 py-4 font-semibold">Summary</th>
                        <th className="px-6 py-4 font-semibold">Date</th>
                        <th className="px-6 py-4 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tickets.map((ticket) => (
                        <tr key={ticket.id} className="border-b border-slate-700/30 hover:bg-slate-800/50 transition-colors">
                          <td className="px-6 py-4 font-mono text-xs text-slate-400">{ticket.id}</td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 text-[10px] font-semibold uppercase rounded-md border ${DEPARTMENT_COLORS[ticket.department] || DEPARTMENT_COLORS.System}`}>
                              {ticket.department}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 text-[10px] font-semibold uppercase rounded-md border ${PRIORITY_COLORS[ticket.priority.toLowerCase()] || 'text-slate-400 bg-slate-800 border-slate-700'}`}>
                              {ticket.priority}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-medium text-slate-200 max-w-xs truncate" title={ticket.summary}>
                            {ticket.summary}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-slate-400 text-xs flex items-center space-x-1.5">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{formatDate(ticket.createdAt)}</span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-2 bg-slate-800/50 w-fit px-2.5 py-1 rounded-full border border-slate-700/50">
                              <div className={`w-2 h-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)] ${ticket.status === 'Open' ? 'bg-amber-400 shadow-amber-400/50' : 'bg-emerald-400 shadow-emerald-400/50'}`}></div>
                              <span className="text-xs font-medium text-slate-300">{ticket.status}</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-16 flex flex-col items-center justify-center text-slate-500">
                  <Ticket className="w-12 h-12 mb-4 opacity-20" />
                  <p className="text-[15px] font-medium text-slate-400">No tickets generated yet</p>
                  <p className="text-sm mt-1">When the agent creates a ticket, it will appear here.</p>
                  <button
                    onClick={() => setActiveTab('chat')}
                    className="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-500/20"
                  >
                    Start a Chat
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    // Default Chat View
    return (
      <div className="flex-1 flex flex-col relative h-full">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 z-10 scroll-smooth">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-5">
              <div className="w-20 h-20 rounded-2xl bg-slate-800/50 flex items-center justify-center border border-slate-700/50 shadow-2xl">
                <Bot className="w-10 h-10 text-blue-500/50" />
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-xl font-semibold text-slate-200">How can I help you?</h3>
                <p className="text-sm text-slate-400 max-w-md mx-auto">
                  Describe your issue or ask a question. I'll search our knowledge base or route you to the right department.
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center mt-4 max-w-lg">
                {['Reset password', 'Request new software', 'WiFi issues', 'Payroll question'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSend(null, suggestion)}
                    className="px-4 py-2 bg-slate-800/40 hover:bg-slate-700/50 border border-slate-700/50 rounded-full text-sm text-slate-300 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
              >
                <div
                  className={`max-w-[90%] md:max-w-[75%] lg:max-w-[65%] flex flex-col space-y-1.5 ${msg.type === 'user' ? 'items-end' : 'items-start'
                    }`}
                >
                  <div className="flex items-center space-x-2 px-1">
                    <span className="text-[11px] text-slate-500 font-medium">
                      {msg.type === 'user' ? 'You' : 'Nagarro AI'} • {formatTime(msg.timestamp)}
                    </span>
                  </div>

                  <div
                    className={`px-5 py-4 rounded-2xl shadow-sm ${msg.type === 'user'
                        ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-tr-sm shadow-blue-900/20 border border-blue-500/20'
                        : msg.type === 'error'
                          ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-tl-sm'
                          : 'bg-[#151b26] border border-slate-700/50 rounded-tl-sm backdrop-blur-sm'
                      }`}
                  >
                    {msg.type === 'user' ? (
                      <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    ) : msg.type === 'error' ? (
                      <div className="flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5" />
                        <p className="text-sm font-medium">{msg.content}</p>
                      </div>
                    ) : (
                      renderAgentResponse(msg)
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start animate-in fade-in">
              <div className="flex flex-col space-y-1.5">
                <span className="text-[11px] text-slate-500 font-medium px-1">Nagarro AI • Typing...</span>
                <div className="bg-[#151b26] border border-slate-700/50 px-5 py-4 rounded-2xl rounded-tl-sm flex items-center space-x-3 w-fit">
                  <div className="flex space-x-1.5">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-[#0a0f18]/90 backdrop-blur-md border-t border-slate-800/60 z-10 shrink-0">
          <div className="max-w-4xl mx-auto relative flex flex-col">
            <div className="relative flex items-end bg-[#131924] border border-slate-700/60 rounded-2xl shadow-inner focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500/50 transition-all duration-200">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                placeholder="Describe your issue or request..."
                className="w-full bg-transparent text-slate-100 pl-5 pr-14 py-4 focus:outline-none disabled:opacity-50 resize-none overflow-y-auto min-h-[56px] max-h-40 text-[15px] leading-relaxed"
                rows={1}
                style={{ scrollbarWidth: 'thin', scrollbarColor: '#334155 transparent' }}
              />
              <div className="absolute right-2 bottom-2">
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="p-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl disabled:opacity-40 disabled:hover:bg-blue-600 transition-all duration-200 flex items-center justify-center shadow-lg shadow-blue-900/20"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="text-center mt-3">
              <p className="text-[11px] text-slate-500 font-medium tracking-wide">
                Nagarro AI securely routes requests to HR, IT, Finance, PM, or QA.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-[#0a0f18] text-slate-100 font-sans overflow-hidden selection:bg-blue-500/30">
      {/* Sidebar Navigation */}
      <div className="w-72 border-r border-slate-800/60 bg-[#0d131f] flex flex-col hidden md:flex shrink-0">
        <div className="p-5 border-b border-slate-800/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100 tracking-wide">Nagarro AI</h2>
            <p className="text-[11px] text-slate-400 font-medium">Enterprise Service Desk</p>
          </div>
        </div>

        <div className="p-4">
          <button
            onClick={() => {
              setActiveTab('chat');
              setMessages([]);
              setContext(null);
            }}
            className="w-full flex items-center justify-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-xl transition-all duration-200 text-sm font-medium border border-slate-700/50"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Request</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          <div>
            <div className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Menu</div>
            <div className="space-y-1">
              <button
                onClick={() => setActiveTab('chat')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 text-sm rounded-lg transition-colors text-left font-medium border ${activeTab === 'chat' ? 'bg-slate-800/80 text-blue-400 border-slate-700/50' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-transparent'}`}
              >
                <MessageSquare className={`w-4 h-4 ${activeTab === 'chat' ? 'text-blue-400' : 'text-slate-500'}`} />
                <span>Active Chat</span>
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 text-sm rounded-lg transition-colors text-left font-medium border ${activeTab === 'dashboard' ? 'bg-slate-800/80 text-blue-400 border-slate-700/50' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-transparent'}`}
              >
                <LayoutDashboard className={`w-4 h-4 ${activeTab === 'dashboard' ? 'text-blue-400' : 'text-slate-500'}`} />
                <span>Dashboard</span>
              </button>
              <button
                onClick={() => setActiveTab('tickets')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 text-sm rounded-lg transition-colors text-left font-medium border ${activeTab === 'tickets' ? 'bg-slate-800/80 text-blue-400 border-slate-700/50' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-transparent'}`}
              >
                <Ticket className={`w-4 h-4 ${activeTab === 'tickets' ? 'text-blue-400' : 'text-slate-500'}`} />
                <span>My Tickets</span>
                {tickets.length > 0 && (
                  <span className="ml-auto bg-slate-800 text-xs py-0.5 px-2 rounded-md font-medium">{tickets.length}</span>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-slate-800/60 space-y-1">
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 text-sm text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-lg transition-colors text-left">
            <Settings className="w-4 h-4 text-slate-500" />
            <span>Settings</span>
          </button>
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 text-sm text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 rounded-lg transition-colors text-left">
            <HelpCircle className="w-4 h-4 text-slate-500" />
            <span>Help & FAQ</span>
          </button>
        </div>
      </div>

      {/* Main Interface Area */}
      <div className="flex-1 flex flex-col relative bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-fixed overflow-hidden">
        <div className="absolute inset-0 bg-[#0a0f18]/95 z-0"></div>

        {/* Header */}
        <header className="h-16 border-b border-slate-800/60 flex items-center justify-between px-6 bg-[#0a0f18]/80 backdrop-blur-md z-10 sticky top-0 shrink-0">
          <div className="flex items-center space-x-3">
            <div className={`w-2 h-2 rounded-full ${activeTab === 'chat' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`}></div>
            <h1 className="text-sm font-medium text-slate-200 capitalize">{activeTab === 'chat' ? 'System Online' : activeTab}</h1>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex flex-col items-end mr-2">
              <span className="text-sm font-medium text-slate-200">User</span>
              <span className="text-[10px] text-slate-400">Employee ID: 4829</span>
            </div>
            <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shadow-inner">
              <User className="w-4 h-4 text-slate-300" />
            </div>
          </div>
        </header>

        {/* Dynamic Content */}
        {renderContent()}
      </div>
    </div>
  );
}
