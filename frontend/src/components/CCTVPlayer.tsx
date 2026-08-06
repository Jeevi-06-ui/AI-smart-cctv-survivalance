import React, { useState } from 'react';
import { Camera, Maximize2, ShieldAlert, Video, Eye, AlertTriangle } from 'lucide-react';
import { CameraFeed } from '../types';

interface CCTVPlayerProps {
  camera: CameraFeed;
  onSelect?: () => void;
}

export const CCTVPlayer: React.FC<CCTVPlayerProps> = ({ camera }) => {
  const [showOverlays, setShowOverlays] = useState(true);

  return (
    <div className="relative glass-card rounded-xl overflow-hidden group border border-cyan-500/20 hover:border-cyan-400/50 transition-all">
      {/* Video Simulation Container */}
      <div className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden">
        {/* Animated Cyber Grid Canvas background */}
        <div className="absolute inset-0 opacity-20 bg-[linear-gradient(to_right,#082f49_1px,transparent_1px),linear-gradient(to_bottom,#082f49_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        
        {/* Camera Subject Graphic Simulation */}
        <div className="relative z-10 text-center">
          <Camera className="w-12 h-12 text-cyan-500/40 mx-auto mb-2 animate-pulse" />
          <div className="text-xs font-mono text-cyan-400/80">{camera.name}</div>
          <div className="text-[10px] text-slate-500 font-mono">{camera.rtspUrl}</div>
        </div>

        {/* Dynamic AI Detection Overlays (Bounding Boxes) */}
        {showOverlays && (
          <>
            {/* Person Bounding Box 1 */}
            <div className="absolute top-[25%] left-[30%] w-[20%] h-[50%] border-2 border-cyan-400 rounded-sm bg-cyan-500/10 pointer-events-none transition-all duration-300">
              <span className="absolute -top-5 left-0 text-[10px] font-mono bg-cyan-500 text-black px-1 rounded font-bold">
                ID:01 Person 94%
              </span>
            </div>
            {/* Weapon / Intrusion Box 2 */}
            <div className="absolute top-[40%] right-[25%] w-[18%] h-[35%] border-2 border-red-500 rounded-sm bg-red-500/20 pointer-events-none animate-pulse">
              <span className="absolute -top-5 left-0 text-[10px] font-mono bg-red-600 text-white px-1 rounded font-bold">
                ! WEAPON: Pistol 91%
              </span>
            </div>
          </>
        )}

        {/* Top Camera Status HUD */}
        <div className="absolute top-2 left-2 right-2 flex justify-between items-center text-[10px] font-mono z-20">
          <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-2 py-1 rounded border border-cyan-500/30 text-cyan-300">
            <span className={`w-2 h-2 rounded-full ${camera.status === 'ONLINE' ? 'bg-emerald-400' : 'bg-red-500'} animate-ping`} />
            <span>{camera.status}</span>
            <span className="text-slate-500">|</span>
            <span>{camera.location}</span>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-2 py-1 rounded border border-cyan-500/30">
            {camera.isRecording && (
              <span className="flex items-center gap-1 text-red-400 font-bold">
                <Video className="w-3 h-3 text-red-500 animate-pulse" /> REC
              </span>
            )}
            <span className="text-cyan-400">{camera.fps} FPS</span>
            <span className="text-slate-500">|</span>
            <span className="text-emerald-400">{camera.latencyMs}ms</span>
          </div>
        </div>

        {/* Bottom AI Detectors Badge Bar */}
        <div className="absolute bottom-2 left-2 right-2 flex justify-between items-center z-20">
          <div className="flex gap-1">
            {camera.activeDetectors.map((detector, i) => (
              <span key={i} className="text-[9px] font-mono bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 px-1.5 py-0.5 rounded">
                {detector}
              </span>
            ))}
          </div>

          <button 
            onClick={() => setShowOverlays(!showOverlays)}
            className="p-1 rounded bg-slate-900/80 text-slate-300 hover:text-cyan-400 border border-cyan-500/30"
          >
            <Eye className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
