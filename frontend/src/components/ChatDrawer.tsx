import React, { useState } from 'react';
import { Bot, Send, X, Sparkles, User } from 'lucide-react';

export const ChatDrawer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'bot'; text: string; sources?: string[] }>>([
    {
      sender: 'bot',
      text: 'Hello Security Officer. I am **GuardianAI RAG Assistant**. Ask me anything about CCTV threat alerts, camera health, or incident summaries.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: data.answer,
        sources: data.sources 
      }]);
    } catch {
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: 'Sorry, unable to connect to GuardianAI backend service right now.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 p-4 rounded-full bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_20px_rgba(0,240,255,0.5)] z-50 transition-all flex items-center gap-2 font-bold"
      >
        <Sparkles className="w-5 h-5 animate-pulse" />
        <span>AI Assistant</span>
      </button>

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 glass-card rounded-2xl border border-cyan-500/40 shadow-2xl z-50 flex flex-col h-[500px] overflow-hidden">
          {/* Header */}
          <div className="p-3 bg-slate-900/90 border-b border-cyan-500/30 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              <span className="font-bold text-sm text-white">GuardianAI RAG Assistant</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-3 overflow-y-auto space-y-3 text-xs">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex gap-2 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.sender === 'bot' && <Bot className="w-4 h-4 text-cyan-400 mt-1 shrink-0" />}
                <div className={`p-2.5 rounded-xl max-w-[80%] ${
                  m.sender === 'user'
                    ? 'bg-cyan-600 text-white rounded-br-none'
                    : 'bg-slate-900/90 text-slate-200 border border-cyan-500/20 rounded-bl-none'
                }`}>
                  <p className="whitespace-pre-line">{m.text}</p>
                  {m.sources && (
                    <div className="mt-2 text-[10px] text-cyan-400 font-mono border-t border-cyan-500/20 pt-1">
                      Sources: {m.sources.join(', ')}
                    </div>
                  )}
                </div>
                {m.sender === 'user' && <User className="w-4 h-4 text-cyan-400 mt-1 shrink-0" />}
              </div>
            ))}
            {loading && <div className="text-cyan-400 text-[10px] font-mono animate-pulse">Analyzing event vectors...</div>}
          </div>

          {/* Input Box */}
          <div className="p-2 border-t border-cyan-500/20 bg-slate-950 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask AI assistant..."
              className="flex-1 bg-slate-900 border border-cyan-500/30 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
            />
            <button onClick={handleSend} className="p-2 bg-cyan-500 text-black rounded-lg hover:bg-cyan-400 font-bold">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
};
