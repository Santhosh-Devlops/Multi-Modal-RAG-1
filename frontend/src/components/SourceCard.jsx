import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, FileText, Table, Image } from 'lucide-react';

const SourceCard = ({ source, index }) => {
  const getModalityIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'table':
        return <Table className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />;
      case 'image':
        return <Image className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />;
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900/70 border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-xs transition-all hover:border-brand-300 dark:hover:border-brand-700">
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 font-semibold text-gray-900 dark:text-white">
          {getModalityIcon(source.content_type)}
          <span>Source #{index || source.source_index || 1}: {source.document_name || `Doc #${source.document_id}`}</span>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
          Page {source.page_number || 1}
        </span>
      </div>

      {source.snippet && (
        <p className="text-gray-600 dark:text-gray-400 italic mb-2 line-clamp-2 leading-relaxed bg-white dark:bg-gray-800/80 p-2 rounded border border-gray-100 dark:border-gray-800 font-mono text-[11px]">
          "{source.snippet}"
        </p>
      )}

      <div className="flex items-center justify-between pt-1 text-[11px]">
        <span className="text-gray-500 dark:text-gray-400">
          Hybrid Match: <strong className="text-brand-600 dark:text-brand-400">{(source.hybrid_score * 100).toFixed(0)}%</strong>
        </span>
        <Link
          to={`/explorer?docId=${source.document_id}&page=${source.page_number}`}
          className="inline-flex items-center gap-1 text-brand-600 dark:text-brand-400 hover:underline font-semibold"
        >
          <span>View Page {source.page_number}</span>
          <ExternalLink className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
};

export default SourceCard;
