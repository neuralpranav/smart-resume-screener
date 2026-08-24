import React from 'react';
import { Briefcase, FileText, UserCheck, CheckCircle2 } from 'lucide-react';

export default function MetricCards({ totalJobs, totalResumes, totalScreenings, totalShortlisted }) {
  const metrics = [
    {
      title: 'Active Jobs',
      value: totalJobs,
      icon: <Briefcase size={24} color="#6366f1" />,
      bg: 'rgba(99, 102, 241, 0.15)',
    },
    {
      title: 'Uploaded Resumes',
      value: totalResumes,
      icon: <FileText size={24} color="#38bdf8" />,
      bg: 'rgba(56, 189, 248, 0.15)',
    },
    {
      title: 'Screened Candidates',
      value: totalScreenings,
      icon: <UserCheck size={24} color="#a855f7" />,
      bg: 'rgba(168, 85, 247, 0.15)',
    },
    {
      title: 'Shortlisted Talent',
      value: totalShortlisted,
      icon: <CheckCircle2 size={24} color="#10b981" />,
      bg: 'rgba(16, 185, 129, 0.15)',
    },
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((m, idx) => (
        <div key={idx} className="metric-card">
          <div className="metric-icon-wrap" style={{ backgroundColor: m.bg }}>
            {m.icon}
          </div>
          <div className="metric-info">
            <h4>{m.title}</h4>
            <div className="metric-value">{m.value}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
