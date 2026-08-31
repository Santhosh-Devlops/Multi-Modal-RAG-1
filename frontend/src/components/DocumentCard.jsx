import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Image, Table, Layers, Trash2, RefreshCw, Eye } from 'lucide-react';

const DocumentCard = ({ document, onDelete, onReprocess }) => {
  const getDomainColor = (domain) => {
    switch (domain?.toLowerCase()) {
      case 'manufacturing':
        return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800';
      case 'healthcare':
        return 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800';
      case 'finance':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800';
      case 'education':
        return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800';
      case 'defence':
        return 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getDomainColor(document.domain)}`}>
            {document.domain}
          </span>
          <span className="text-[11px] font-medium text-gray-400 dark:text-gray-500 uppercase">
            {document.file_type}
          </span>
        </div>

        <h3 className="text-sm font-bold text-gray-900 dark:text-white line-clamp-2 mb-1" title={document.filename}>
          {document.filename}
        </h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
          {document.doc_type || 'Document Reference'}
        </p>

        <div className="grid grid-cols-4 gap-2 py-3 px-3 bg-gray-50 dark:bg-gray-900/60 rounded-lg border border-gray-100 dark:border-gray-800 text-center mb-4">
          <div>
            <span className="text-[10px] text-gray-500 dark:text-gray-400 block font-medium">Pages</span>
            <span className="text-xs font-bold text-gray-800 dark:text-gray-200">{document.page_count}</span>
          </div>
          <div>
            <span className="text-[10px] text-gray-500 dark:text-gray-400 block font-medium">Images</span>
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400">{document.image_count}</span>
          </div>
          <div>
            <span className="text-[10px] text-gray-500 dark:text-gray-400 block font-medium">Tables</span>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">{document.table_count}</span>
          </div>
          <div>
            <span className="text-[10px] text-gray-500 dark:text-gray-400 block font-medium">Chunks</span>
            <span className="text-xs font-bold text-purple-600 dark:text-purple-400">{document.chunk_count}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700">
        <Link
          to={`/explorer?docId=${document.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Explore PDF</span>
        </Link>

        <div className="flex items-center gap-1">
          {onReprocess && (
            <button
              onClick={() => onReprocess(document.id)}
              title="Reprocess Document"
              className="p-1.5 text-gray-400 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(document.id)}
              title="Delete Document"
              className="p-1.5 text-gray-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentCard;
