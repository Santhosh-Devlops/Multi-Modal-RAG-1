import React, { useState } from 'react';
import { X, Upload, CheckCircle2, AlertCircle, RefreshCw, FileText, Check, FileCheck } from 'lucide-react';
import { uploadDocumentFile } from '../services/apiService';

const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB

const UploadModal = ({ isOpen, onClose, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState(null);
  const [uploadedResult, setUploadedResult] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selectedFile = e.target.files && e.target.files[0];
    if (!selectedFile) return;

    // Validate size (25 MB)
    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      setError(`File size (${(selectedFile.size / 1024 / 1024).toFixed(1)} MB) exceeds the maximum allowed limit of 25 MB.`);
      setFile(null);
      return;
    }

    // Validate extension
    const allowed = ['.pdf', '.docx', '.csv', '.xlsx', '.xls', '.png', '.jpg', '.jpeg'];
    const nameLower = selectedFile.name.toLowerCase();
    const isAllowed = allowed.some(ext => nameLower.endsWith(ext));
    if (!isAllowed) {
      setError('Unsupported format. Please upload PDF, DOCX, CSV, XLSX, PNG, or JPG documents.');
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a document to upload.');
      return;
    }

    setUploading(true);
    setError(null);
    setStep(1);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('domain', 'General');
      formData.append('doc_type', 'Document');

      const stepTimer = setInterval(() => {
        setStep((prev) => (prev < 5 ? prev + 1 : prev));
      }, 600);

      const res = await uploadDocumentFile(formData);
      clearInterval(stepTimer);
      setStep(6);
      setUploadedResult(res);

      setTimeout(() => {
        if (onUploadSuccess) onUploadSuccess(res.document);
        onClose();
        // Reset state
        setFile(null);
        setUploading(false);
        setStep(0);
        setUploadedResult(null);
      }, 1600);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload and extract document.');
      setUploading(false);
      setStep(0);
    }
  };

  const extractionSteps = [
    'Parsing file layout & structure...',
    'Extracting text paragraphs & sections...',
    'Extracting visual figures, diagrams & tables...',
    'Extracting mathematical equations & formulas...',
    'Extracting numerical limits & parameters...',
    'Generating dense embeddings & indexing complete!'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#16122E] border border-slate-300 dark:border-[#282252] rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-[#282252] flex items-center justify-between bg-slate-50 dark:bg-[#0D0A1C]/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-brand-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <Upload className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-900 dark:text-white">Upload Document</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">Offline multi-agent extraction & private RAG assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={uploading}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-full hover:bg-slate-100 dark:hover:bg-[#201A40]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleUpload} className="p-6 space-y-4">
          
          {error && (
            <div className="p-3.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-2xl text-red-700 dark:text-red-300 text-xs font-bold flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Success Upload Result with Preview Thumbnail & Actual File Size */}
          {uploadedResult ? (
            <div className="p-5 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/80 rounded-2xl flex items-center gap-4 animate-in fade-in">
              <div className="w-16 h-20 bg-white dark:bg-[#0D0A1C] rounded-xl overflow-hidden border border-emerald-300 dark:border-emerald-700/60 shadow-sm flex items-center justify-center flex-shrink-0">
                {uploadedResult.preview_image_path ? (
                  <img
                    src={uploadedResult.preview_image_path}
                    alt="Page preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <FileCheck className="w-8 h-8 text-emerald-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-300 font-extrabold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Document Extracted Successfully!</span>
                </div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate mt-1">
                  {uploadedResult.document?.filename}
                </p>
                <div className="flex items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  <span className="font-semibold">Actual Size: <strong>{uploadedResult.formatted_size || `${(uploadedResult.document?.file_size / 1024 / 1024).toFixed(2)} MB`}</strong></span>
                  <span>•</span>
                  <span><strong>{uploadedResult.document?.page_count || 1}</strong> Pages</span>
                </div>
              </div>
            </div>
          ) : (
            /* Single Drag-and-Drop Upload Dropzone */
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Drag & Drop or Browse Document
                </span>
                <span className="text-[11px] font-extrabold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/80 px-2.5 py-0.5 rounded-full border border-brand-200 dark:border-brand-800">
                  Max file size: 25 MB
                </span>
              </div>

              <div className="border-2 border-dashed border-slate-300 dark:border-[#282252] hover:border-brand-500 dark:hover:border-brand-500 rounded-2xl p-8 text-center cursor-pointer transition-all bg-slate-50/50 dark:bg-[#0D0A1C]/50 relative group">
                <input
                  type="file"
                  accept=".pdf,.docx,.csv,.xlsx,.xls,.png,.jpg,.jpeg"
                  onChange={handleFileChange}
                  disabled={uploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                <div className="w-12 h-12 rounded-2xl bg-brand-50 dark:bg-[#1A1435] text-brand-600 dark:text-brand-400 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6" />
                </div>

                {file ? (
                  <div>
                    <p className="text-sm font-extrabold text-slate-900 dark:text-white truncate max-w-xs mx-auto">
                      {file.name}
                    </p>
                    <p className="text-xs font-bold text-brand-600 dark:text-brand-400 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB • Ready to ingest
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm font-extrabold text-slate-800 dark:text-slate-200">
                      Click to choose or drop document file here
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Supports PDF, DOCX, CSV, XLSX, PNG, JPG
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Ingestion Progress Steps */}
          {uploading && (
            <div className="p-4 bg-slate-100 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-2xl space-y-2.5">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-brand-600 dark:text-brand-400 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  {extractionSteps[step] || 'Finalizing vector indexing...'}
                </span>
                <span className="text-slate-500 font-extrabold">{Math.min(100, Math.round((step / 6) * 100))}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-brand-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${Math.min(100, Math.round((step / 6) * 100))}%` }}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={uploading}
              className="px-4 py-2.5 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!file || uploading}
              className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white font-extrabold text-sm rounded-2xl shadow-lg shadow-brand-600/25 flex items-center gap-2 transition-all"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload & Ingest</span>
                </>
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default UploadModal;
