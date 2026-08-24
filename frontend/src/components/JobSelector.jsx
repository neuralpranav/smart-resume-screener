import React from 'react';
import { Plus, Trash2, Calendar, Clock, Award } from 'lucide-react';

export default function JobSelector({
  jobs,
  activeJobId,
  onSelectJob,
  onOpenCreateJobModal,
  onDeleteJob,
}) {
  const activeJob = jobs.find((j) => j.id === activeJobId);

  return (
    <div className="job-control-panel">
      <div className="job-control-header">
        <div className="job-select-wrapper">
          <label htmlFor="active-job-select">Target Job Role:</label>
          <select
            id="active-job-select"
            className="job-dropdown"
            value={activeJobId || ''}
            onChange={(e) => onSelectJob(e.target.value)}
          >
            {jobs.length === 0 ? (
              <option value="">No jobs posted yet - Create one to start screening</option>
            ) : (
              jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} {job.department ? `(${job.department})` : ''}
                </option>
              ))
            )}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-primary" onClick={onOpenCreateJobModal}>
            <Plus size={16} /> New Job Posting
          </button>
          {activeJob && (
            <button
              className="btn btn-outline-danger"
              onClick={() => onDeleteJob(activeJob.id)}
              title="Delete this job posting"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {activeJob && (
        <div className="job-details-banner">
          <div className="job-details-meta">
            <span>
              <strong>Department:</strong> {activeJob.department || 'General'}
            </span>
            <span>
              <strong>Min Experience:</strong> {activeJob.min_experience_years} Years
            </span>
            <span>
              <strong>Posted:</strong> {new Date(activeJob.created_at).toLocaleDateString()}
            </span>
          </div>

          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
            {activeJob.description}
          </p>

          <div className="skill-chips-row">
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              Required Skills:
            </span>
            {activeJob.required_skills?.length > 0 ? (
              activeJob.required_skills.map((skill, idx) => (
                <span key={idx} className="skill-chip required">
                  {skill}
                </span>
              ))
            ) : (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>None specified</span>
            )}

            {activeJob.preferred_skills?.length > 0 && (
              <>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                  Preferred:
                </span>
                {activeJob.preferred_skills.map((skill, idx) => (
                  <span key={idx} className="skill-chip preferred">
                    {skill}
                  </span>
                ))}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
