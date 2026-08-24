import React, { useState } from 'react';
import { X, Briefcase } from 'lucide-react';

export default function JobModal({ isOpen, onClose, onCreateJob }) {
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [description, setDescription] = useState('');
  const [requiredSkillsStr, setRequiredSkillsStr] = useState('');
  const [preferredSkillsStr, setPreferredSkillsStr] = useState('');
  const [minExperience, setMinExperience] = useState(2);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setFormError('Title and description are required.');
      return;
    }

    const requiredSkills = requiredSkillsStr
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const preferredSkills = preferredSkillsStr
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    setIsSubmitting(true);
    setFormError('');

    try {
      await onCreateJob({
        title: title.trim(),
        department: department.trim() || null,
        description: description.trim(),
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        min_experience_years: parseInt(minExperience, 10) || 0,
      });

      // Reset and close
      setTitle('');
      setDepartment('');
      setDescription('');
      setRequiredSkillsStr('');
      setPreferredSkillsStr('');
      setMinExperience(2);
      onClose();
    } catch (err) {
      setFormError(err.message || 'Failed to create job posting.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Briefcase size={20} color="var(--primary)" />
            Create New Job Posting
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {formError && (
              <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', background: 'var(--danger-bg)', color: '#fca5a5', fontSize: '0.875rem' }}>
                {formError}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Job Title *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Senior Python Developer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Department / Team</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Engineering"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Min. Experience (Years)</label>
                <input
                  type="number"
                  min="0"
                  max="30"
                  className="form-input"
                  value={minExperience}
                  onChange={(e) => setMinExperience(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Job Description *</label>
              <textarea
                rows="4"
                className="form-textarea"
                placeholder="Describe role responsibilities, core scope, and team expectations..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Must-Have Skills (comma-separated)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Python, FastAPI, Docker, PostgreSQL"
                value={requiredSkillsStr}
                onChange={(e) => setRequiredSkillsStr(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Nice-to-Have Skills (comma-separated)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. AWS, Kubernetes, GraphQL, Redis"
                value={preferredSkillsStr}
                onChange={(e) => setPreferredSkillsStr(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Posting'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
