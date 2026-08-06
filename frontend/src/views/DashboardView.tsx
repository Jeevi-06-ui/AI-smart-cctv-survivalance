import React from 'react';
import { Camera, ShieldAlert, Users, Flame, AlertTriangle, Activity, Cpu } from 'lucide-react';
import { CCTVPlayer } from '../components/CCTVPlayer';
import { CameraFeed, ThreatAlert } from '../types';

export const DashboardView: React.FC = () => {
  const sampleCameras: CameraFeed[] = [
    {
      id: 'cam-1',
      name: 'CAM-01: Main Gate Terminal',
      location: 'Zone A - Entrance',
      status: 'ONLINE',
      fps: 30,
      latencyMs: 14,
      isRecording: true,
      activeDetectors: ['YOLO11', 'InsightFace', 'Weapon'],
      rtspUrl: 'rtsp://192.168.1.101/live'
    },
    {
      id: 'cam-2',
      name: 'CAM-02: North Concourse',
      location: 'Zone B - Passenger Gate',
      status: 'ONLINE',
      fps: 29.8,
      latencyMs: 18,
      isRecording: true,
      activeDetectors: ['Fire/Smoke', 'Fight', 'Crowd'],
      rtspUrl: 'rtsp://192.168.1.102/live'
    },
    {
      id: 'cam-3',
      name: 'CAM-03: Perimeter Fence Line',
      location: 'Zone C - Restricted Perimeter',
      status: 'ONLINE',
      fps: 30,
      latencyMs: 12,
      isRecording: true,
      activeDetectors: ['Virtual Fence', 'ALPR'],
      rtspUrl: 'rtsp://192.168.1.103/live'
    },
    {
      id: 'cam-4',
      name: 'CAM-04: Baggage Claim Area',
      location: 'Zone D - Lower Level',
      status: 'ONLINE',
      fps: 30,
      latencyMs: 16,
      isRecording: true,
      activeDetectors: ['Crowd Heatmap', 'YOLO11'],
      rtspUrl: 'rtsp://192.168.1.104/live'
    }
  ];

  const recentAlerts: ThreatAlert[] = [
    {
      id: 'alt-1',
      cameraId: 'cam-1',
      cameraName: 'CAM-01 Main Gate',
      threatType: 'WEAPON',
      severity: 'CRITICAL',
      confidence: 0.94,
      timestamp: '14:22:10 UTC',
      snapshotUrl: '',
      isAcknowledged: false
    },
    {
      id: 'alt-2',
      cameraId: 'cam-2',
      cameraName: 'CAM-02 North Concourse',
      threatType: 'FIGHT_VIOLENCE',
      severity: 'HIGH',
      confidence: 0.89,
      timestamp: '14:18:45 UTC',
      snapshotUrl: '',
      isAcknowledged: true
    },
    {
      id: 'alt-3',
      cameraId: 'cam-3',
      cameraName: 'CAM-03 Perimeter',
      threatType: 'INTRUSION',
      severity: 'HIGH',
      confidence: 0.92,
      timestamp: '14:05:00 UTC',
      snapshotUrl: '',
      isAcknowledged: true
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Top KPI Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl border border-cyan-500/30 flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-400/40 rounded-lg text-cyan-400">
            <Camera className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">ACTIVE CAMERAS</div>
            <div className="text-2xl font-bold text-white font-mono">16 / 16</div>
            <div className="text-[10px] text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> 100% Online
            </div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-red-500/30 flex items-center gap-4">
          <div className="p-3 bg-red-500/10 border border-red-400/40 rounded-lg text-red-400">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">CRITICAL ALERTS (24H)</div>
            <div className="text-2xl font-bold text-red-400 font-mono">3 THREATS</div>
            <div className="text-[10px] text-red-400">1 Unacknowledged</div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-cyan-500/30 flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-400/40 rounded-lg text-cyan-400">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">LIVE PERSON COUNT</div>
            <div className="text-2xl font-bold text-cyan-300 font-mono">148 SUBJECTS</div>
            <div className="text-[10px] text-slate-400">DeepSORT Tracking</div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-emerald-500/30 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 border border-emerald-400/40 rounded-lg text-emerald-400">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono">TENSORRT LATENCY</div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">4.2 ms</div>
            <div className="text-[10px] text-emerald-400">NVIDIA FP16 Acceleration</div>
          </div>
        </div>
      </div>

      {/* Main Grid Section: 4x Live CCTV + Real-time Alert Ticker */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CCTV Grid (2x2) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Camera className="w-5 h-5 text-cyan-400" /> Live Surveillance Matrix
            </h2>
            <span className="text-xs font-mono text-cyan-400/80 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/30">
              LAYOUT: 2x2 GRID
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {sampleCameras.map((cam) => (
              <CCTVPlayer key={cam.id} camera={cam} />
            ))}
          </div>
        </div>

        {/* Real-Time Security Alert Ticker Feed */}
        <div className="glass-card p-4 rounded-xl space-y-4 border border-cyan-500/20">
          <div className="flex justify-between items-center border-b border-cyan-500/20 pb-3">
            <h3 className="text-md font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-400 animate-pulse" /> Threat Alert Feed
            </h3>
            <span className="text-[10px] font-mono text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/30">
              LIVE BROADCAST
            </span>
          </div>

          <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
            {recentAlerts.map((alert) => (
              <div 
                key={alert.id}
                className={`p-3 rounded-lg border transition-all ${
                  alert.severity === 'CRITICAL' 
                    ? 'bg-red-950/40 border-red-500/60 shadow-[0_0_10px_rgba(239,68,68,0.2)]'
                    : 'bg-slate-900/60 border-amber-500/40'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${
                    alert.severity === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-amber-600 text-white'
                  }`}>
                    {alert.threatType}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">{alert.timestamp}</span>
                </div>

                <div className="text-xs font-semibold text-slate-200 mt-2">{alert.cameraName}</div>
                <div className="flex justify-between items-center text-[10px] text-slate-400 mt-2 font-mono">
                  <span>Confidence: {(alert.confidence * 100).toFixed(0)}%</span>
                  <button className="text-cyan-400 hover:underline">ACKNOWLEDGE</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
