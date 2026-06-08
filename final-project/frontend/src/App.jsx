import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, PlusCircle, MessageSquare, AlertCircle, CheckCircle2, Ticket } from 'lucide-react';

const DEPARTMENT_COLORS = {
  HR: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  IT: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  Finance: 'bg-green-500/10 text-green-400 border-green-500/20',
  QA: 'bg-red-500/10 text-red-400 border-red-500/20',
  PM: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  Escalated: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  System: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
};

const PRIORITY_COLORS = {
  low: 'text-gray-400',
  medium: 'text-yellow-400',
  high: 'text-red-400',
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('https://ashitakolla.app.n8n.cloud/webhook/service-desk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with service desk.');
      }

      const data = await response.json();
      
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
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs font-medium border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded-md border border-gray-700">
              Ticket Created
            </span>
            {msg.priority && (
              <span className={`text-xs font-medium ${PRIORITY_COLORS[msg.priority.toLowerCase()] || 'text-gray-400'}`}>
                {msg.priority.toUpperCase()} PRIORITY
              </span>
            )}
          </div>
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 mt-2 flex items-start space-x-3">
            <Ticket className="w-5 h-5 text-blue-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-200">Ticket successfully logged</p>
              <p className="text-sm text-gray-400 mt-1">{msg.summary}</p>
            </div>
          </div>
        </div>
      );
    }

    if (msg.status === 'email_sent') {
      return (
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs font-medium border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded-md border border-gray-700">
              Email Sent
            </span>
          </div>
          <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 mt-2 flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-green-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-200">Email delivered successfully</p>
              <p className="text-sm text-gray-400 mt-1">Check your inbox for further details.</p>
            </div>
          </div>
        </div>
      );
    }

    if (msg.status === 'clarification_needed') {
      return (
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs font-medium border rounded-md ${deptColor}`}>
              {msg.department || 'System'}
            </span>
            <span className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded-md border border-gray-700">
              Clarification Needed
            </span>
          </div>
          <p className="text-gray-200 text-sm mt-2">{msg.message}</p>
        </div>
      );
    }

    if (msg.status === 'escalated') {
      return (
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs font-medium border rounded-md ${DEPARTMENT_COLORS.Escalated}`}>
              Escalated
            </span>
            {msg.confidence && (
              <span className="text-xs text-gray-500">
                Confidence: {(msg.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mt-2 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-500">Request Escalated</p>
              <p className="text-sm text-yellow-500/80 mt-1">{msg.reason}</p>
            </div>
          </div>
        </div>
      );
    }

    if (msg.status === 'completed') {
      return (
        <div className="flex flex-col space-y-2">
           <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 text-xs font-medium border rounded-md ${DEPARTMENT_COLORS.System}`}>
              Completed
            </span>
            <span className="text-xs text-gray-500">Action: {msg.action}</span>
          </div>
          <p className="text-gray-200 text-sm mt-2">{msg.message}</p>
        </div>
      );
    }

    return (
       <div className="flex flex-col space-y-2">
          <p className="text-gray-200 text-sm">{JSON.stringify(msg)}</p>
       </div>
    );
  };

  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex h-screen bg-[#0E1116] text-gray-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-800 bg-[#11141A] flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <button 
            onClick={() => setMessages([])}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors text-sm font-medium"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Recent</div>
          <div className="space-y-1">
            <button className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800/50 rounded-md transition-colors text-left group">
              <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-gray-300" />
              <span className="truncate">Service Desk Session</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Header */}
        <header className="h-14 border-b border-gray-800 flex items-center px-6 bg-[#0E1116]/80 backdrop-blur-sm z-10">
          <h1 className="text-sm font-medium text-gray-200">Enterprise Service Desk</h1>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
              <MessageSquare className="w-12 h-12 opacity-20" />
              <p className="text-sm">How can we help you today?</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] lg:max-w-[60%] flex flex-col space-y-1 ${
                    msg.type === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div
                    className={`px-5 py-3.5 rounded-2xl ${
                      msg.type === 'user'
                        ? 'bg-blue-600 text-white rounded-br-sm'
                        : msg.type === 'error'
                        ? 'bg-red-500/10 border border-red-500/20 text-red-400 rounded-bl-sm'
                        : 'bg-[#151921] border border-gray-800 rounded-bl-sm'
                    }`}
                  >
                    {msg.type === 'user' ? (
                      <p className="text-sm">{msg.content}</p>
                    ) : msg.type === 'error' ? (
                      <p className="text-sm">{msg.content}</p>
                    ) : (
                      renderAgentResponse(msg)
                    )}
                  </div>
                  <span className="text-[10px] text-gray-500 font-medium px-1">
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[#151921] border border-gray-800 px-5 py-4 rounded-2xl rounded-bl-sm flex items-center space-x-3">
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                <span className="text-sm text-gray-400">Processing request...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-[#0E1116] border-t border-gray-800">
          <div className="max-w-4xl mx-auto relative flex items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder="Describe your issue or request..."
              className="w-full bg-[#151921] border border-gray-700/50 text-gray-100 rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-50 resize-none overflow-hidden min-h-[52px] max-h-32 text-sm transition-all"
              rows={1}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="text-center mt-3">
            <p className="text-[10px] text-gray-500">Service Desk routes requests to HR, IT, Finance, PM, or QA automatically.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
