import React, { useState } from 'react';
import {
  Trophy,
  Filter,
  CheckCircle,
  Eye,
  Sparkles,
  ArrowUpDown,
  Search,
  UserX,
} from 'lucide-react';

export default function Leaderboard({
  rankings,
  onToggleShortlist,
  onViewCandidateDetails,
  onBatchScreen,
  isScreening,
  hasResumes,
  hasActiveJob,
}) {
  const [minScore, setMinScore] = useState('');
  const [shortlistedOnly, setShortlistedOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Client-side search and filtering
  const filteredRankings = rankings.filter((item) => {
    if (shortlistedOnly && !item.is_shortlisted) return false;
    if (minScore !== '' && item.match_score < parseFloat(minScore)) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = item.candidate_name?.toLowerCase().includes(q);
      const matchSkills = item.matched_skills?.some((s) => s.toLowerCase().includes(q));
      if (!matchName && !matchSkills) return false;
    }
    return true;
  });

  const getScoreBadgeClass = (score) => {
    if (score >= 75) return 'score-badge strong';
    if (score >= 50) return 'score-badge moderate';
    return 'score-badge low';
  };

  const getFitBadgeClass = (level) => {
    if (level === 'Strong Match') return 'fit-badge strong';
    if (level === 'Moderate Match') return 'fit-badge moderate';
    return 'fit-badge low';
  };

  return (
    <div className="panel-card" style={{ flex: 1 }}>
      <div className="panel-header">
        <div className="panel-title">
          <Trophy size={20} color="#fbbf24" />
          Candidate Leaderboard & Evaluation
        </div>

        <button
          className="btn btn-primary"
          onClick={onBatchScreen}
          disabled={isScreening || !hasResumes || !hasActiveJob}
        >
          <Sparkles size={16} /> {isScreening ? 'Screening...' : 'Screen All Resumes'}
        </button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '180px' }}>
          <Search size={16} color="var(--text-muted)" />
          <input
            type="text"
            className="form-input"
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.8125rem', width: '100%' }}
            placeholder="Search candidate name or skill..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-inputs">
          <div className="filter-label">
            <span>Min Score:</span>
            <input
              type="number"
              min="0"
              max="100"
              className="input-sm"
              placeholder="0"
              value={minScore}
              onChange={(e) => setMinScore(e.target.value)}
            />
          </div>

          <label className="filter-label">
            <input
              type="checkbox"
              checked={shortlistedOnly}
              onChange={(e) => setShortlistedOnly(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Shortlisted Only
          </label>
        </div>
      </div>

      {/* Rankings Table */}
      {filteredRankings.length === 0 ? (
        <div className="empty-state">
          <UserX className="empty-state-icon" />
          <p>
            {!hasActiveJob
              ? 'Please select or create a job posting to view candidate rankings.'
              : rankings.length === 0
              ? 'No candidates screened for this job yet. Click "Screen All Resumes" or screen individual candidates.'
              : 'No candidates matched the current filter criteria.'}
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="candidate-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>#</th>
                <th>Candidate</th>
                <th>Score</th>
                <th>Fit Level</th>
                <th>Matched Skills</th>
                <th>Shortlist</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredRankings.map((cand, idx) => (
                <tr key={cand.screening_id}>
                  <td>
                    <span className={`rank-badge ${idx < 3 ? `top-${idx + 1}` : ''}`}>
                      #{idx + 1}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      {cand.candidate_name}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {cand.candidate_email || cand.filename}
                    </div>
                  </td>
                  <td>
                    <span className={getScoreBadgeClass(cand.match_score)}>
                      {cand.match_score}%
                    </span>
                  </td>
                  <td>
                    <span className={getFitBadgeClass(cand.fit_level)}>
                      {cand.fit_level}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', maxWidth: '240px' }}>
                      {cand.matched_skills?.slice(0, 3).map((skill, sIdx) => (
                        <span key={sIdx} className="skill-chip matched" style={{ fontSize: '0.6875rem' }}>
                          {skill}
                        </span>
                      ))}
                      {cand.matched_skills?.length > 3 && (
                        <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                          +{cand.matched_skills.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <button
                      className={`shortlist-btn ${cand.is_shortlisted ? 'active' : ''}`}
                      onClick={() => onToggleShortlist(cand.screening_id, !cand.is_shortlisted)}
                    >
                      <CheckCircle size={14} />
                      {cand.is_shortlisted ? 'Shortlisted' : 'Shortlist'}
                    </button>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.375rem 0.625rem', fontSize: '0.75rem' }}
                      onClick={() => onViewCandidateDetails(cand)}
                      title="Inspect full AI reasoning and breakdown"
                    >
                      <Eye size={14} /> View Report
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
