export type PageView = 
  | 'dashboard'
  | 'cameras'
  | 'incidents'
  | 'alerts'
  | 'analytics'
  | 'reports'
  | 'users'
  | 'settings'
  | 'profile';

export interface CameraFeed {
  id: string;
  name: string;
  location: string;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED';
  fps: number;
  latencyMs: number;
  isRecording: boolean;
  activeDetectors: string[];
  rtspUrl: string;
}

export interface ThreatAlert {
  id: string;
  cameraId: string;
  cameraName: string;
  threatType: 'WEAPON' | 'FIRE_SMOKE' | 'FIGHT_VIOLENCE' | 'INTRUSION' | 'BLACKLIST_FACE' | 'ALPR';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  timestamp: string;
  snapshotUrl: string;
  isAcknowledged: boolean;
}

export interface IncidentRecord {
  id: string;
  code: string;
  title: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED';
  assignedTo: string;
  timestamp: string;
  timelineCount: number;
}
