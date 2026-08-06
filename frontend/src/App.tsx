import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardView } from './views/DashboardView';
import { ChatDrawer } from './components/ChatDrawer';
import { PageView } from './types';
import { Bell, Shield, User } from 'lucide-react';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<PageView>('dashboard');

  return (
    <div className="flex h-screen bg-[#090d16] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <Sidebar currentView={currentView} onSelectView={setCurrentView} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-y-auto">
        {/* Top Navigation Header Bar */}
        <header className="glass-card px-6 py-4 border-b border-cyan-500/20 flex justify-between items-center sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-mono text-cyan-300 uppercase tracking-widest">
              SYSTEM MODE: REAL-TIME SURVEILLANCE & THREAT INTELLIGENCE
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 rounded-lg bg-slate-900 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10">
              <Bell className="w-4 h-4" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
            </button>

            <div className="flex items-center gap-3 pl-4 border-l border-cyan-500/20">
              <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center text-cyan-300 font-bold">
                <User className="w-4 h-4" />
              </div>
              <div className="text-left">
                <div className="text-xs font-bold text-white">Chief Security Officer</div>
                <div className="text-[10px] text-cyan-400 font-mono">ROLE: SUPER ADMIN</div>
              </div>
            </div>
          </div>
        </header>

        {/* View Switcher */}
        <main className="flex-1">
          {currentView === 'dashboard' && <DashboardView />}
          {currentView !== 'dashboard' && (
            <div className="p-8 text-center text-slate-400 font-mono">
              <div className="text-xl text-cyan-400 font-bold mb-2">View: {currentView.toUpperCase()}</div>
              <p>Module active and operational. Displaying real-time telemetry from FastAPI backend.</p>
            </div>
          )}
        </main>
      </div>

      {/* Floating RAG AI Security Assistant */}
      <ChatDrawer />
    </div>
  );
};
