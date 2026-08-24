import React from 'react';
import { Sparkles, Activity } from 'lucide-react';

export default function Navbar({ isBackendConnected, version }) {
  return (
    <header className="navbar">
      <div className="brand-logo">
        <div className="brand-icon">
          <Sparkles size={22} />
        </div>
        <div>
          <span>Smart Resume Screener</span>
          <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-muted)', fontWeight: 400 }}>
            AI-Powered Candidate Evaluation Platform
          </span>
        </div>
      </div>

      <div className="nav-status">
        <span className={`status-dot ${isBackendConnected ? 'online' : 'offline'}`} />
        <span>{isBackendConnected ? `Backend API Active (v${version || '0.1.0'})` : 'Backend Disconnected'}</span>
      </div>
    </header>
  );
}
