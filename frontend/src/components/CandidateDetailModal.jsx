import React from 'react';
import {
  X,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Award,
  Sparkles,
  ShieldCheck,
  Check,
} from 'lucide-react';

export default function CandidateDetailModal({
  candidate,
  isOpen,
  onClose,
  onToggleShortlist,
}) {
  if (!isOpen || !candidate) return null;

  const getScoreColor = (score) => {
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" style={{ maxWidth: '720px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">{candidate.candidate_name}</div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              {candidate.candidate_email || 'No email provided'} • {candidate.filename}
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Score & Fit Banner */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1.25rem',
              borderRadius: 'var(--radius-lg)',
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid var(--border-color)',
            }}
          >
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Overall Match Score
              </div>
              <div style={{ fontSize: '2.25rem', fontWeight: 800, color: getScoreColor(candidate.match_score) }}>
                {candidate.match_score}%
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Evaluation Fit
              </div>
              <div style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                {candidate.fit_level}
              </div>
            </div>
          </div>

          {/* Justification Box */}
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
              <Sparkles size={16} color="var(--primary)" /> Evaluation Justification
            </label>
            <div
              style={{
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.2)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                lineHeight: '1.6',
              }}
            >
              {candidate.justification}
            </div>
          </div>

          {/* Matched vs Missing Skills */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" style={{ color: 'var(--success)' }}>
                Matched Skills ({candidate.matched_skills?.length || 0})
              </label>
              <div
                style={{
                  minHeight: '80px',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(15, 23, 42, 0.4)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '0.375rem',
                  alignContent: 'flex-start',
                }}
              >
                {candidate.matched_skills && candidate.matched_skills.length > 0 ? (
                  candidate.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-chip matched">
                      ✓ {skill}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>No direct skills matched</span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" style={{ color: '#f87171' }}>
                Missing Skills ({candidate.missing_skills?.length || 0})
              </label>
              <div
                style={{
                  minHeight: '80px',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(15, 23, 42, 0.4)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '0.375rem',
                  alignContent: 'flex-start',
                }}
              >
                {candidate.missing_skills && candidate.missing_skills.length > 0 ? (
                  candidate.missing_skills.map((skill, idx) => (
                    <span key={idx} className="skill-chip missing">
                      ✕ {skill}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>None (full skill coverage)</span>
                )}
              </div>
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                <CheckCircle2 size={16} color="var(--success)" /> Key Strengths
              </label>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
                {candidate.strengths?.map((str, idx) => (
                  <li
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.5rem',
                      color: 'var(--text-secondary)',
                      background: 'rgba(16, 185, 129, 0.05)',
                      padding: '0.5rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    <span style={{ color: 'var(--success)' }}>•</span>
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                <AlertTriangle size={16} color="#f87171" /> Identified Gaps
              </label>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
                {candidate.weaknesses && candidate.weaknesses.length > 0 ? (
                  candidate.weaknesses.map((weak, idx) => (
                    <li
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.5rem',
                        color: 'var(--text-secondary)',
                        background: 'rgba(239, 68, 68, 0.05)',
                        padding: '0.5rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                      }}
                    >
                      <span style={{ color: '#f87171' }}>•</span>
                      <span>{weak}</span>
                    </li>
                  ))
                ) : (
                  <li style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>No major critical gaps identified.</li>
                )}
              </ul>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button
            className={`btn ${candidate.is_shortlisted ? 'btn-success' : 'btn-secondary'}`}
            onClick={() => onToggleShortlist(candidate.screening_id, !candidate.is_shortlisted)}
          >
            <Check size={16} />
            {candidate.is_shortlisted ? 'Shortlisted ✓' : 'Mark as Shortlisted'}
          </button>
          <button className="btn btn-primary" onClick={onClose}>
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
