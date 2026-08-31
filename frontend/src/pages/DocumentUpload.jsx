import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  Workflow
} from 'lucide-react';
import { uploadDocument } from '../services/apiService';

const DocumentUpload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [domain, setDomain] = useState('Manufacturing');
  const [docType, setDocType] = useState('Technical Operations Manual');
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setResult(null);
      setCurrentStep(0);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
      setResult(null);
      setCurrentStep(0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setUploading(true);
    setError('');
    setResult(null);
    setCurrentStep(1);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);
    formData.append('doc_type', docType);

    const timer1 = setTimeout(() => setCurrentStep(2), 700);
    const timer2 = setTimeout(() => setCurrentStep(3), 1400);
    const timer3 = setTimeout(() => setCurrentStep(4), 2100);

    try {
      const res = await uploadDocument(formData);
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      if (res.status === 'success') {
        setCurrentStep(5);
        setResult(res);
      }
    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setCurrentStep(0);
      setError(err.response?.data?.detail || 'Failed to process document.');
    } finally {
      setUploading(false);
    }
  };

  const steps = [
    { num: 1, name: 'Document Processing Agent', desc: 'Parsing multi-page layout and text extraction' },
    { num: 2, name: 'Image Understanding Agent', desc: 'Extracting raster diagrams and generating visual descriptions' },
    { num: 3, name: 'Table Understanding Agent', desc: 'Parsing structured matrices into Markdown & natural language' },
    { num: 4, name: 'Vector Embedding Pipeline', desc: 'Computing 384-dimensional dense vectors and indexing' }
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 font-serif">
      {/* Header */}
      <div className="pb-4 border-b border-gray-200 dark:border-hclsurface-darkborder">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <UploadCloud className="w-6 h-6 text-brand-500" />
          <span>Upload &amp; Ingest Document</span>
        </h1>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Upload your PDF manual, diagram, or tabular dataset to trigger sequential multi-agent extraction and vector indexing.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-xs font-semibold text-red-700 dark:text-red-300">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1.5">
              Domain Classification
            </label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="block w-full px-3 py-2.5 text-xs font-bold border border-gray-300 dark:border-hclsurface-darkborder rounded-xl bg-white dark:bg-hclsurface-darkcard text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500 font-serif"
            >
              <option value="Manufacturing">Manufacturing</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Finance">Finance</option>
              <option value="Education">Education</option>
              <option value="Defence">Defence</option>
              <option value="Engineering">Engineering</option>
              <option value="General">General Technical</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1.5">
              Document Category / Description
            </label>
            <input
              type="text"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="block w-full px-3 py-2.5 text-xs font-bold border border-gray-300 dark:border-hclsurface-darkborder rounded-xl bg-white dark:bg-hclsurface-darkcard text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500 font-serif"
              placeholder="e.g. Equipment Operations & Maintenance Manual"
            />
          </div>
        </div>

        {/* Drag and drop zone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="border-2 border-dashed border-gray-300 dark:border-hclsurface-darkborder hover:border-brand-500 dark:hover:border-brand-500 rounded-2xl p-8 text-center transition-colors bg-white dark:bg-hclsurface-darkcard shadow-sm"
        >
          <div className="flex justify-center mb-3">
            <div className="w-14 h-14 rounded-2xl bg-brand-50 dark:bg-hclsurface-dark text-brand-500 flex items-center justify-center border border-brand-100 dark:border-brand-900">
              <UploadCloud className="w-7 h-7" />
            </div>
          </div>

          <p className="text-sm font-bold text-gray-900 dark:text-white mb-1">
            {file ? file.name : 'Select a PDF document, image, or table to upload'}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
            Supports PDF (multi-page with images & tables), DOCX, CSV, XLSX, PNG, JPG
          </p>

          <input
            type="file"
            id="fileInput"
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf,.docx,.csv,.xlsx,.xls,.png,.jpg,.jpeg"
          />
          <label
            htmlFor="fileInput"
            className="cursor-pointer inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-50 text-brand-700 dark:bg-hclsurface-dark dark:text-brand-300 text-xs font-bold hover:bg-brand-100 transition-colors border border-brand-200 dark:border-hclsurface-darkborder"
          >
            <FileText className="w-4 h-4" />
            <span>Browse Files</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={uploading || !file}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-xs font-bold text-white bg-brand-500 hover:bg-brand-600 focus:outline-none transition-colors disabled:opacity-50 font-serif"
        >
          {uploading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Multi-Agent Ingestion Pipeline Active...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-4 h-4" />
              <span>Upload and Run Sequential Agent Ingestion</span>
            </>
          )}
        </button>
      </form>

      {/* Live Sequential Multi-Agent Pipeline Status */}
      {(uploading || result) && (
        <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-4 font-serif">
          <div className="flex items-center gap-2">
            <Workflow className="w-5 h-5 text-brand-500" />
            <h2 className="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">
              Sequential Ingestion Agent Pipeline Status
            </h2>
          </div>

          <div className="space-y-3">
            {steps.map((s) => {
              const isCurrent = currentStep === s.num;
              const isPassed = currentStep > s.num;

              return (
                <div
                  key={s.num}
                  className={`p-3.5 rounded-xl border text-xs flex items-center justify-between transition-all ${
                    isPassed
                      ? 'bg-emerald-50/60 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                      : isCurrent
                      ? 'bg-brand-50 dark:bg-hclsurface-dark border-brand-400 dark:border-brand-600 text-brand-900 dark:text-brand-100 font-bold animate-pulse'
                      : 'bg-gray-50 dark:bg-hclsurface-dark border-gray-200 dark:border-hclsurface-darkborder text-gray-400 dark:text-gray-500'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      isPassed ? 'bg-emerald-600 text-white' : isCurrent ? 'bg-brand-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                    }`}>
                      {isPassed ? <CheckCircle2 className="w-4 h-4" /> : s.num}
                    </span>
                    <div>
                      <span className="font-bold block text-sm">{s.name}</span>
                      <span className="text-xs opacity-80">{s.desc}</span>
                    </div>
                  </div>

                  <span className="text-[11px] font-bold uppercase">
                    {isPassed ? 'Completed' : isCurrent ? 'Processing...' : 'Waiting'}
                  </span>
                </div>
              );
            })}
          </div>

          {result && (
            <div className="pt-4 border-t border-gray-100 dark:border-hclsurface-darkborder flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                ✓ Extracted {result.document.page_count} pages, {result.document.image_count} figures, {result.document.table_count} tables &amp; {result.document.chunk_count} vector chunks.
              </span>

              <Link
                to="/assistant"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold shadow-md transition-colors font-serif"
              >
                <span>Ask Questions in Assistant</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
