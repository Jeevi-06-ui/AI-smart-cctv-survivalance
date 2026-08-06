import React from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Camera, 
  FileWarning, 
  Bell, 
  BarChart3, 
  FileText, 
  Users, 
  Settings, 
  UserCheck
} from 'lucide-react';
import { PageView } from '../types';

interface SidebarProps {
  currentView: PageView;
  onSelectView: (view: PageView) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'cameras', label: 'Live Cameras', icon: Camera },
    { id: 'incidents', label: 'Incidents', icon: FileWarning },
    { id: 'alerts', label: 'Threat Alerts', icon: Bell },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'reports', label: 'AI Reports', icon: FileText },
    { id: 'users', label: 'User Mgmt', icon: Users },
    { id: 'settings', label: 'System Settings', icon: Settings },
    { id: 'profile', label: 'Operator Profile', icon: UserCheck },
  ];

  return (
    <aside className="w-64 glass-card h-screen flex flex-col justify-between p-4 z-20">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-4 mb-6 border-b border-cyan-500/20">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-400/30 text-cyan-400">
            <ShieldAlert className="w-7 h-7 neon-text" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-wider">Guardian<span className="text-cyan-400">AI</span></h1>
            <p className="text-[10px] text-cyan-400/70 uppercase tracking-widest font-mono">NVIDIA AI GPU Surveillance</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id as PageView)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* GPU Accelerator Footer Status */}
      <div className="p-3 rounded-lg bg-slate-900/80 border border-cyan-500/20 text-xs text-slate-300">
        <div className="flex justify-between items-center mb-1">
          <span className="text-[11px] font-mono text-cyan-400">NVIDIA TensorRT</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        </div>
        <div className="text-[10px] text-slate-400">GPU: RTX 4090 | FP16 Mode</div>
        <div className="text-[10px] text-slate-400">Latency: 4.2ms | FPS: 120</div>
      </div>
    </aside>
  );
};
