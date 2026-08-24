import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import MetricCards from './components/MetricCards';
import JobSelector from './components/JobSelector';
import JobModal from './components/JobModal';
import ResumeUploader from './components/ResumeUploader';
import ResumeList from './components/ResumeList';
import Leaderboard from './components/Leaderboard';
import CandidateDetailModal from './components/CandidateDetailModal';
import Toast from './components/Toast';
import { api } from './services/api';
import { Sparkles, FileText, Trophy } from 'lucide-react';

export default function App() {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [apiVersion, setApiVersion] = useState('0.1.0');
  
  const [jobs, setJobs] = useState([]);
  const [activeJobId, setActiveJobId] = useState('');
  const [resumes, setResumes] = useState([]);
  const [rankings, setRankings] = useState([]);
  
  const [isCreateJobModalOpen, setIsCreateJobModalOpen] = useState(false);
  const [selectedCandidateDetail, setSelectedCandidateDetail] = useState(null);
  const [isScreening, setIsScreening] = useState(false);
  const [toasts, setToasts] = useState([]);

  // Toast Helper
  const showToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  // Health check
  const checkHealth = useCallback(async () => {
    try {
      const data = await api.getHealth();
      setIsBackendConnected(data.status === 'healthy');
      setApiVersion(data.version);
    } catch {
      setIsBackendConnected(false);
    }
  }, []);

  // Load Jobs
  const loadJobs = useCallback(async () => {
    try {
      const data = await api.getJobs();
      setJobs(data);
      if (data.length > 0 && !activeJobId) {
        setActiveJobId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  }, [activeJobId]);

  // Load Resumes
  const loadResumes = useCallback(async () => {
    try {
      const data = await api.getResumes();
      setResumes(data);
    } catch (err) {
      console.error('Failed to load resumes:', err);
    }
  }, []);

  // Load Rankings for Active Job
  const loadRankings = useCallback(async (jobId) => {
    if (!jobId) {
      setRankings([]);
      return;
    }
    try {
      const data = await api.getJobRankings(jobId);
      setRankings(data);
    } catch (err) {
      console.error('Failed to load rankings:', err);
    }
  }, []);

  // Initial Data Load
  useEffect(() => {
    checkHealth();
    loadJobs();
    loadResumes();
  }, [checkHealth, loadJobs, loadResumes]);

  // Sync Rankings whenever active job changes
  useEffect(() => {
    if (activeJobId) {
      loadRankings(activeJobId);
    } else {
      setRankings([]);
    }
  }, [activeJobId, loadRankings]);

  // Handlers
  const handleCreateJob = async (jobData) => {
    const newJob = await api.createJob(jobData);
    setJobs((prev) => [newJob, ...prev]);
    setActiveJobId(newJob.id);
    showToast(`Job posting "${newJob.title}" created successfully!`);
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job posting and its screening results?')) {
      return;
    }
    try {
      await api.deleteJob(jobId);
      const remaining = jobs.filter((j) => j.id !== jobId);
      setJobs(remaining);
      setActiveJobId(remaining.length > 0 ? remaining[0].id : '');
      showToast('Job posting deleted.');
    } catch (err) {
      showToast(err.message || 'Failed to delete job', 'error');
    }
  };

  const handleUploadResume = async (fileOrFiles) => {
    if (Array.isArray(fileOrFiles)) {
      const uploaded = await api.uploadResumesBatch(fileOrFiles);
      await loadResumes();
      showToast(`Uploaded and parsed ${uploaded.length} resumes!`);
      return uploaded;
    } else {
      const uploaded = await api.uploadResume(fileOrFiles);
      await loadResumes();
      showToast(`Parsed resume for ${uploaded.candidate?.full_name || uploaded.filename}!`);
      return uploaded;
    }
  };

  const handleDeleteResume = async (resumeId) => {
    try {
      await api.deleteResume(resumeId);
      setResumes((prev) => prev.filter((r) => r.id !== resumeId));
      if (activeJobId) {
        loadRankings(activeJobId);
      }
      showToast('Resume removed.');
    } catch (err) {
      showToast(err.message || 'Failed to delete resume', 'error');
    }
  };

  const handleScreenSingle = async (resumeId) => {
    if (!activeJobId) {
      showToast('Please select or create a job posting first.', 'error');
      return;
    }
    setIsScreening(true);
    try {
      const result = await api.screenResume(activeJobId, resumeId);
      await loadRankings(activeJobId);
      showToast(`Screened candidate! Score: ${result.match_score}% (${result.fit_level})`);

      // Open detail modal with formatted candidate object
      const candObj = {
        screening_id: result.id,
        resume_id: result.resume_id,
        candidate_name: result.resume?.candidate?.full_name || 'Candidate',
        candidate_email: result.resume?.candidate?.email || null,
        filename: result.resume?.filename || 'resume',
        match_score: result.match_score,
        fit_level: result.fit_level,
        matched_skills: result.matched_skills,
        missing_skills: result.missing_skills,
        strengths: result.strengths,
        weaknesses: result.weaknesses,
        justification: result.justification,
        is_shortlisted: result.is_shortlisted,
      };
      setSelectedCandidateDetail(candObj);
    } catch (err) {
      showToast(err.message || 'Screening failed', 'error');
    } finally {
      setIsScreening(false);
    }
  };

  const handleBatchScreen = async () => {
    if (!activeJobId) {
      showToast('Please select a target job posting first.', 'error');
      return;
    }
    if (resumes.length === 0) {
      showToast('Please upload candidate resumes first.', 'error');
      return;
    }

    setIsScreening(true);
    try {
      const results = await api.screenBatch(activeJobId);
      await loadRankings(activeJobId);
      showToast(`Batch screening complete! Evaluated ${results.length} candidate(s).`);
    } catch (err) {
      showToast(err.message || 'Batch screening failed', 'error');
    } finally {
      setIsScreening(false);
    }
  };

  const handleToggleShortlist = async (screeningId, newStatus) => {
    try {
      const updated = await api.toggleShortlist(screeningId, newStatus);
      // Update rankings list state
      setRankings((prev) =>
        prev.map((r) =>
          r.screening_id === screeningId ? { ...r, is_shortlisted: updated.is_shortlisted } : r
        )
      );
      // Update active detail modal if open
      if (selectedCandidateDetail && selectedCandidateDetail.screening_id === screeningId) {
        setSelectedCandidateDetail((prev) => ({ ...prev, is_shortlisted: updated.is_shortlisted }));
      }
      showToast(
        updated.is_shortlisted ? 'Candidate marked as shortlisted!' : 'Shortlist removed.'
      );
    } catch (err) {
      showToast(err.message || 'Failed to update shortlist status', 'error');
    }
  };

  // Derived metrics
  const totalShortlisted = rankings.filter((r) => r.is_shortlisted).length;

  return (
    <div className="app-container">
      <Navbar isBackendConnected={isBackendConnected} version={apiVersion} />

      <MetricCards
        totalJobs={jobs.length}
        totalResumes={resumes.length}
        totalScreenings={rankings.length}
        totalShortlisted={totalShortlisted}
      />

      <JobSelector
        jobs={jobs}
        activeJobId={activeJobId}
        onSelectJob={setActiveJobId}
        onOpenCreateJobModal={() => setIsCreateJobModalOpen(true)}
        onDeleteJob={handleDeleteJob}
      />

      <div className="dashboard-grid">
        {/* Left Column: Upload & Resumes */}
        <div className="panel-card">
          <div className="panel-header">
            <div className="panel-title">
              <FileText size={20} color="var(--primary)" />
              Candidate Resumes ({resumes.length})
            </div>
          </div>

          <ResumeUploader
            onUploadSuccess={handleUploadResume}
            onError={(msg) => showToast(msg, 'error')}
          />

          <ResumeList
            resumes={resumes}
            onScreenSingle={handleScreenSingle}
            onDeleteResume={handleDeleteResume}
            isScreening={isScreening}
          />
        </div>

        {/* Right Column: Leaderboard & Evaluation */}
        <Leaderboard
          rankings={rankings}
          onToggleShortlist={handleToggleShortlist}
          onViewCandidateDetails={setSelectedCandidateDetail}
          onBatchScreen={handleBatchScreen}
          isScreening={isScreening}
          hasResumes={resumes.length > 0}
          hasActiveJob={Boolean(activeJobId)}
        />
      </div>

      {/* Create Job Modal */}
      <JobModal
        isOpen={isCreateJobModalOpen}
        onClose={() => setIsCreateJobModalOpen(false)}
        onCreateJob={handleCreateJob}
      />

      {/* Candidate Detail Report Modal */}
      <CandidateDetailModal
        candidate={selectedCandidateDetail}
        isOpen={Boolean(selectedCandidateDetail)}
        onClose={() => setSelectedCandidateDetail(null)}
        onToggleShortlist={handleToggleShortlist}
      />

      {/* Toast Notifications */}
      <Toast toasts={toasts} />
    </div>
  );
}
