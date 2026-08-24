const API_BASE = import.meta.env.VITE_API_URL || '/api';

/**
 * Helper to handle fetch responses and standardized backend error messages.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.error) {
        errorMessage = errorData.error;
      } else if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((d) => d.msg || d.loc?.join('.')).join(', ');
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        }
      }
    } catch {
      // Non-JSON response error
    }
    const err = new Error(errorMessage);
    err.status = response.status;
    throw err;
  }
  return response.json();
}

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Jobs
  getJobs: async (skip = 0, limit = 100) => {
    const res = await fetch(`${API_BASE}/jobs?skip=${skip}&limit=${limit}`);
    return handleResponse(res);
  },

  getJob: async (jobId) => {
    const res = await fetch(`${API_BASE}/jobs/${jobId}`);
    return handleResponse(res);
  },

  createJob: async (jobData) => {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobData),
    });
    return handleResponse(res);
  },

  deleteJob: async (jobId) => {
    const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Resumes
  getResumes: async (skip = 0, limit = 100) => {
    const res = await fetch(`${API_BASE}/resumes?skip=${skip}&limit=${limit}`);
    return handleResponse(res);
  },

  getResume: async (resumeId) => {
    const res = await fetch(`${API_BASE}/resumes/${resumeId}`);
    return handleResponse(res);
  },

  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  uploadResumesBatch: async (files) => {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    const res = await fetch(`${API_BASE}/resumes/upload-batch`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  deleteResume: async (resumeId) => {
    const res = await fetch(`${API_BASE}/resumes/${resumeId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Screening
  screenResume: async (jobId, resumeId) => {
    const res = await fetch(`${API_BASE}/screen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, resume_id: resumeId }),
    });
    return handleResponse(res);
  },

  screenBatch: async (jobId, resumeIds = null) => {
    const payload = { job_id: jobId };
    if (resumeIds && resumeIds.length > 0) {
      payload.resume_ids = resumeIds;
    }
    const res = await fetch(`${API_BASE}/screen/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  getScreeningDetails: async (screeningId) => {
    const res = await fetch(`${API_BASE}/screen/${screeningId}`);
    return handleResponse(res);
  },

  getJobResults: async (jobId) => {
    const res = await fetch(`${API_BASE}/screen/job/${jobId}/results`);
    return handleResponse(res);
  },

  getJobRankings: async (jobId, minScore = null, shortlistedOnly = false) => {
    let url = `${API_BASE}/screen/job/${jobId}/rankings?shortlisted_only=${shortlistedOnly}`;
    if (minScore !== null && minScore !== undefined && minScore !== '') {
      url += `&min_score=${minScore}`;
    }
    const res = await fetch(url);
    return handleResponse(res);
  },

  toggleShortlist: async (screeningId, isShortlisted) => {
    const res = await fetch(`${API_BASE}/screen/${screeningId}/shortlist`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_shortlisted: isShortlisted }),
    });
    return handleResponse(res);
  },
};
