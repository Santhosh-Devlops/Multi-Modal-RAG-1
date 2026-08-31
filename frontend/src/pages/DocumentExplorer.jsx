import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  Image as ImageIcon,
  Table as TableIcon,
  Layers,
  Sparkles,
  ExternalLink,
  Bot
} from 'lucide-react';
import { getDocuments, getDocumentDetails, getDocumentPage } from '../services/apiService';

const DocumentExplorer = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [docDetails, setDocDetails] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageData, setPageData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initial load
  useEffect(() => {
    const fetchInitial = async () => {
      try {
        const res = await getDocuments();
        if (res.status === 'success' && res.documents.length > 0) {
          setDocuments(res.documents);
          
          const paramDocId = searchParams.get('docId');
          const paramPage = searchParams.get('page');
          
          const targetId = paramDocId ? parseInt(paramDocId, 10) : res.documents[0].id;
          const targetPage = paramPage ? parseInt(paramPage, 10) : 1;
          
          setSelectedDocId(targetId);
          setCurrentPage(targetPage);
          loadDoc(targetId, targetPage);
        }
      } catch (err) {
        console.error('Error loading documents for explorer:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitial();
  }, []);

  const loadDoc = async (docId, pageNum = 1) => {
    try {
      const [detailRes, pageRes] = await Promise.all([
        getDocumentDetails(docId),
        getDocumentPage(docId, pageNum),
      ]);
      if (detailRes.status === 'success') {
        setDocDetails(detailRes.document);
      }
      if (pageRes.status === 'success') {
        setPageData(pageRes);
      }
    } catch (err) {
      console.error('Error loading page details:', err);
    }
  };

  const handleDocChange = (newDocId) => {
    const id = parseInt(newDocId, 10);
    setSelectedDocId(id);
    setCurrentPage(1);
    setSearchParams({ docId: id, page: 1 });
    loadDoc(id, 1);
  };

  const handlePageChange = (newPageNum) => {
    if (!docDetails || newPageNum < 1 || newPageNum > docDetails.page_count) return;
    setCurrentPage(newPageNum);
    setSearchParams({ docId: selectedDocId, page: newPageNum });
    loadDoc(selectedDocId, newPageNum);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            <span>Multimodal Document Explorer & Inspector</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Examine what the RAG ingestion pipeline extracted: rendered PDF pages, raw text, detected raster images, and structured tables.
          </p>
        </div>

        {/* Document Selector Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">Document:</span>
          <select
            value={selectedDocId || ''}
            onChange={(e) => handleDocChange(e.target.value)}
            className="px-3 py-1.5 text-xs font-medium border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500 max-w-xs"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename} ({d.domain})
              </option>
            ))}
          </select>
        </div>
      </div>

      {docDetails && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm text-xs">
          <div className="flex items-center gap-3">
            <span className="font-bold text-gray-900 dark:text-white">{docDetails.filename}</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
              Domain: {docDetails.domain}
            </span>
          </div>

          {/* Page Navigator */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="font-semibold text-gray-800 dark:text-gray-200 text-xs">
              Page <strong className="text-brand-600 dark:text-brand-400">{currentPage}</strong> of {docDetails.page_count}
            </span>

            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage >= docDetails.page_count}
              className="p-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Explorer Workspace (Side-by-Side) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: PDF Page Preview Thumbnail & Visuals */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <span>Rendered Page Preview (Page {currentPage})</span>
            </h2>

            <div className="bg-gray-100 dark:bg-gray-900 rounded-xl p-2 border border-gray-200 dark:border-gray-800 flex justify-center items-center min-h-[480px]">
              {pageData?.page?.preview_image_path ? (
                <img
                  src={pageData.page.preview_image_path}
                  alt={`Page ${currentPage} Preview`}
                  className="max-h-[580px] w-auto rounded shadow-sm object-contain border border-gray-200 dark:border-gray-700"
                />
              ) : (
                <div className="text-center text-xs text-gray-400 p-8">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <span>Preview rendering generated by PyMuPDF engine</span>
                </div>
              )}
            </div>
          </div>

          {/* Detected Images on Page */}
          {pageData?.images && pageData.images.length > 0 && (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
              <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                <ImageIcon className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                <span>Detected Visual Figures ({pageData.images.length})</span>
              </h2>

              <div className="space-y-3">
                {pageData.images.map((img) => (
                  <div key={img.id} className="p-3 bg-gray-50 dark:bg-gray-900/60 rounded-xl border border-gray-100 dark:border-gray-800 space-y-2">
                    <div className="flex justify-center bg-white dark:bg-gray-800 p-2 rounded-lg border border-gray-200 dark:border-gray-700">
                      <img
                        src={img.image_path}
                        alt={img.image_name}
                        className="max-h-48 w-auto rounded object-contain"
                      />
                    </div>
                    <div className="text-xs space-y-1">
                      <div className="flex items-center justify-between text-[11px] font-semibold text-gray-600 dark:text-gray-400">
                        <span>Type: {img.image_type}</span>
                        <span>Dimensions: {img.width} x {img.height}</span>
                      </div>
                      <p className="text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-800 p-2 rounded border border-gray-100 dark:border-gray-700 leading-relaxed font-sans text-[11px]">
                        <strong>AI Vision Analysis:</strong> {img.generated_description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Extracted Text & Structured Tables */}
        <div className="space-y-4">
          {/* Extracted Page Text */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>Extracted Plain Text Stream</span>
              </h2>
              <span className="text-[10px] text-gray-400 font-mono">
                {pageData?.page?.page_text?.length || 0} characters
              </span>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-900/60 rounded-xl border border-gray-200 dark:border-gray-700 font-sans text-xs text-gray-800 dark:text-gray-200 leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-line">
              {pageData?.page?.page_text || 'No text extracted on this page.'}
            </div>
          </div>

          {/* Detected Structured Tables */}
          {pageData?.tables && pageData.tables.length > 0 && (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
              <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                <TableIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>Detected Structured Tables ({pageData.tables.length})</span>
              </h2>

              <div className="space-y-4">
                {pageData.tables.map((tbl) => (
                  <div key={tbl.id} className="p-3 bg-gray-50 dark:bg-gray-900/60 rounded-xl border border-gray-100 dark:border-gray-800 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-semibold text-gray-600 dark:text-gray-400">
                      <span>Table #{tbl.table_index}</span>
                      <span>{tbl.row_count} Rows &times; {tbl.column_count} Columns</span>
                    </div>

                    <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 font-mono text-[11px] text-gray-800 dark:text-gray-200 overflow-x-auto whitespace-pre leading-relaxed">
                      {tbl.raw_markdown}
                    </div>

                    <div className="p-2.5 bg-emerald-50/60 dark:bg-emerald-950/40 rounded-lg border border-emerald-200 dark:border-emerald-800 text-[11px] text-emerald-900 dark:text-emerald-200">
                      <strong>Natural Language Assertion for Indexing:</strong>
                      <p className="mt-1 leading-relaxed">{tbl.natural_language_text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentExplorer;
