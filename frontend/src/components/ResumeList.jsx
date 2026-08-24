import React from 'react';
import { FileText, Trash2, User, Sparkles } from 'lucide-react';

export default function ResumeList({ resumes, onScreenSingle, onDeleteResume, isScreening }) {
  if (resumes.length === 0) {
    return (
      <div className="empty-state">
        <FileText className="empty-state-icon" />
        <p>No resumes uploaded yet. Drag & drop candidate resumes above to begin.</p>
      </div>
    );
  }

  return (
    <div className="resume-list-container">
      {resumes.map((resume) => (
        <div key={resume.id} className="resume-item-card">
          <div className="resume-meta">
            <div className="resume-candidate-name">
              {resume.candidate_name || 'Candidate'}
            </div>
            <div className="resume-file-info">
              {resume.filename} • {resume.file_type.toUpperCase()}
              {resume.extracted_experience_years !== null &&
                ` • ~${resume.extracted_experience_years} yrs exp`}
            </div>

            {resume.extracted_skills && resume.extracted_skills.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.375rem' }}>
                {resume.extracted_skills.slice(0, 4).map((s, idx) => (
                  <span
                    key={idx}
                    style={{
                      fontSize: '0.6875rem',
                      background: 'rgba(255, 255, 255, 0.06)',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '4px',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {s}
                  </span>
                ))}
                {resume.extracted_skills.length > 4 && (
                  <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                    +{resume.extracted_skills.length - 4} more
                  </span>
                )}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}
              onClick={() => onScreenSingle(resume.id)}
              disabled={isScreening}
              title="Screen this resume against active job"
            >
              <Sparkles size={14} color="var(--primary)" /> Screen
            </button>
            <button
              className="btn btn-outline-danger"
              style={{ padding: '0.375rem 0.5rem' }}
              onClick={() => onDeleteResume(resume.id)}
              title="Delete resume"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
