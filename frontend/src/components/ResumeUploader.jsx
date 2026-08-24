import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function ResumeUploader({ onUploadSuccess, onError }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = async (files) => {
    // Filter valid pdf and txt files
    const validFiles = files.filter((f) => {
      const ext = f.name.split('.').pop().toLowerCase();
      return ext === 'pdf' || ext === 'txt';
    });

    if (validFiles.length === 0) {
      onError('Please upload valid PDF (.pdf) or Plain Text (.txt) resume files.');
      return;
    }

    setIsUploading(true);
    setUploadStatus({ type: 'loading', message: `Uploading & parsing ${validFiles.length} file(s)...` });

    try {
      if (validFiles.length === 1) {
        const result = await onUploadSuccess(validFiles[0]);
        setUploadStatus({
          type: 'success',
          message: `Successfully parsed resume for ${result.candidate?.full_name || result.filename}!`,
        });
      } else {
        const results = await onUploadSuccess(validFiles);
        setUploadStatus({
          type: 'success',
          message: `Successfully parsed ${results.length} resumes!`,
        });
      }
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'Failed to upload and parse resume.',
      });
      onError(err.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
        accept=".pdf,.txt"
        multiple
      />

      <div
        className={`dropzone ${isDragging ? 'drag-active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <UploadCloud className="dropzone-icon" />
        <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          {isUploading ? 'Parsing Resume with AI Engine...' : 'Drag & Drop Resumes (PDF or TXT)'}
        </h4>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          Click to browse or drop single/multiple candidate files here (up to 10MB each)
        </p>
      </div>

      {uploadStatus && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.625rem 0.875rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.8125rem',
            background:
              uploadStatus.type === 'success'
                ? 'var(--success-bg)'
                : uploadStatus.type === 'error'
                ? 'var(--danger-bg)'
                : 'var(--primary-light)',
            color:
              uploadStatus.type === 'success'
                ? 'var(--success)'
                : uploadStatus.type === 'error'
                ? '#fca5a5'
                : '#a5b4fc',
          }}
        >
          {uploadStatus.type === 'loading' && <Loader2 size={16} className="spinner" />}
          {uploadStatus.type === 'success' && <CheckCircle2 size={16} />}
          {uploadStatus.type === 'error' && <AlertCircle size={16} />}
          <span>{uploadStatus.message}</span>
        </div>
      )}
    </div>
  );
}
