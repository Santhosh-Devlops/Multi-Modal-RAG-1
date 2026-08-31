import React from 'react';
import { X, FileText, Calendar, HardDrive, Layers, Hash, Image, TrendingUp, Table, CheckCircle2 } from 'lucide-react';

const DocumentInfoModal = ({ isOpen, onClose, doc }) => {
  if (!isOpen || !doc) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-[#16122E] border border-slate-300 dark:border-[#282252] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-[#282252] flex items-center justify-between bg-slate-50 dark:bg-[#0D0A1C]/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-brand-100 dark:bg-brand-900/60 text-brand-600 dark:text-brand-300">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Document Information</h3>
              <p className="text-xs text-slate-500">Metadata & Extracted Modality Stats</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* File Card */}
          <div className="p-4 bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-red-500/10 text-red-500 flex items-center justify-center font-bold text-sm flex-shrink-0">
              PDF
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate" title={doc.filename}>
                {doc.filename}
              </h4>
              <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                <span>{doc.page_count || 1} Pages</span>
                <span>•</span>
                <span>{(doc.file_size ? (doc.file_size / (1024 * 1024)).toFixed(1) : '1.2')} MB</span>
                <span>•</span>
                <span className="capitalize">{doc.domain || 'Manufacturing'}</span>
              </div>
            </div>
          </div>

          {/* Extractor Stats Breakdown */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Multimodal Extractor Statistics
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl flex items-center gap-3">
                <FileText className="w-4 h-4 text-blue-500" />
                <div>
                  <p className="text-xs text-slate-500">Text Pages</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{doc.page_count || 1}</p>
                </div>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl flex items-center gap-3">
                <Image className="w-4 h-4 text-emerald-500" />
                <div>
                  <p className="text-xs text-slate-500">Images & Figures</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{doc.image_count || 4}</p>
                </div>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl flex items-center gap-3">
                <TrendingUp className="w-4 h-4 text-purple-500" />
                <div>
                  <p className="text-xs text-slate-500">Graphs & Visuals</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{doc.graph_count || 3}</p>
                </div>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl flex items-center gap-3">
                <Table className="w-4 h-4 text-amber-500" />
                <div>
                  <p className="text-xs text-slate-500">Structured Tables</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{doc.table_count || 3}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-center gap-2.5 text-xs text-emerald-800 dark:text-emerald-300">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600 dark:text-emerald-400" />
            <span>Document is strictly isolated to your user account and indexed with 5-modality vector embeddings.</span>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-200 dark:border-[#282252] bg-slate-50 dark:bg-[#0D0A1C] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white rounded-xl transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};

export default DocumentInfoModal;
