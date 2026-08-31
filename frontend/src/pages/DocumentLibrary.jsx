import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  FolderOpen,
  Trash2,
  Plus,
  ChevronLeft,
  ChevronRight,
  FileText
} from 'lucide-react';
import { getDocuments, getDocumentDetails, getDocumentPage, deleteDocument } from '../services/apiService';

const DocumentLibrary = () => {
  const [searchParams] = useSearchParams();
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageData, setPageData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await getDocuments();
      if (res.status === 'success') {
        setDocuments(res.documents);
        
        const paramDocId = searchParams.get('docId');
        const paramPage = searchParams.get('page');

        if (res.documents.length > 0) {
          const targetId = paramDocId ? parseInt(paramDocId, 10) : res.documents[0].id;
          const targetPage = paramPage ? parseInt(paramPage, 10) : 1;
          loadDocDetail(targetId, targetPage);
        }
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const loadDocDetail = async (docId, pageNum = 1) => {
    try {
      const [detailRes, pageRes] = await Promise.all([
        getDocumentDetails(docId),
        getDocumentPage(docId, pageNum),
      ]);
      if (detailRes.status === 'success') {
        setSelectedDoc(detailRes.document);
        setCurrentPage(pageNum);
      }
      if (pageRes.status === 'success') {
        setPageData(pageRes);
      }
    } catch (err) {
      console.error('Error loading doc details:', err);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(id);
        setSelectedDoc(null);
        setPageData(null);
        fetchDocs();
      } catch (err) {
        alert('Failed to delete document');
      }
    }
  };

  const handlePageChange = (newPage) => {
    if (!selectedDoc || newPage < 1 || newPage > selectedDoc.page_count) return;
    loadDocDetail(selectedDoc.id, newPage);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 font-serif">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-hclsurface-darkborder">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <FolderOpen className="w-6 h-6 text-brand-500" />
            <span>My Uploaded Documents &amp; Page Inspector</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Browse your uploaded files, review page-by-page extractions, detected diagrams, and structured tables.
          </p>
        </div>

        <Link
          to="/upload"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold shadow-md transition-colors self-start font-serif"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Another File</span>
        </Link>
      </div>

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-hclsurface-darkcard rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder p-8 space-y-3 shadow-sm">
          <FolderOpen className="w-12 h-12 text-brand-500 mx-auto opacity-60" />
          <h3 className="text-sm font-bold text-gray-900 dark:text-white">No documents uploaded yet</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
            Upload your first manufacturing manual or technical specification to start.
          </p>
          <div className="pt-2">
            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold shadow-md font-serif"
            >
              <span>Upload Document</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document list selector */}
          <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
            <h2 className="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider mb-2">
              Uploaded Documents ({documents.length})
            </h2>

            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {documents.map((d) => (
                <div
                  key={d.id}
                  onClick={() => loadDocDetail(d.id, 1)}
                  className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all ${
                    selectedDoc?.id === d.id
                      ? 'bg-brand-50 dark:bg-hclsurface-dark border-brand-500 shadow-sm font-bold text-brand-900 dark:text-brand-200'
                      : 'bg-gray-50 dark:bg-hclsurface-dark/60 border-gray-200 dark:border-hclsurface-darkborder text-gray-700 dark:text-gray-300 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-bold line-clamp-1 text-sm">{d.filename}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(d.id);
                      }}
                      className="text-gray-400 hover:text-red-600 p-1"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-600 dark:text-gray-400 font-semibold">
                    <span>{d.page_count} Pages</span>
                    <span>&bull;</span>
                    <span>{d.image_count} Figures</span>
                    <span>&bull;</span>
                    <span>{d.table_count} Tables</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Document & Page Inspector */}
          <div className="lg:col-span-2 space-y-4">
            {selectedDoc && (
              <>
                <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-sm text-gray-900 dark:text-white block">{selectedDoc.filename}</span>
                    <span className="text-gray-500 dark:text-gray-400 text-xs">
                      Domain: {selectedDoc.domain} | Total Pages: {selectedDoc.page_count}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage <= 1}
                      className="p-1.5 rounded-lg border border-gray-300 dark:border-hclsurface-darkborder hover:bg-gray-100 dark:hover:bg-hclsurface-dark disabled:opacity-40"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="font-bold text-gray-800 dark:text-gray-200">
                      Page {currentPage} of {selectedDoc.page_count}
                    </span>
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage >= selectedDoc.page_count}
                      className="p-1.5 rounded-lg border border-gray-300 dark:border-hclsurface-darkborder hover:bg-gray-100 dark:hover:bg-hclsurface-dark disabled:opacity-40"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Page content display */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left: Page Preview */}
                  <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-300 block">
                      Page {currentPage} Preview
                    </span>

                    <div className="bg-gray-100 dark:bg-hclsurface-dark rounded-xl p-2 min-h-[380px] flex items-center justify-center border border-gray-200 dark:border-hclsurface-darkborder">
                      {pageData?.page?.preview_image_path ? (
                        <img
                          src={pageData.page.preview_image_path}
                          alt={`Page ${currentPage}`}
                          className="max-h-[420px] w-auto rounded shadow-sm object-contain"
                        />
                      ) : (
                        <span className="text-xs text-gray-400 font-bold">Page {currentPage}</span>
                      )}
                    </div>
                  </div>

                  {/* Right: Extracted Multimodal Elements */}
                  <div className="space-y-4">
                    {/* Extracted text */}
                    <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-300 block">
                        Extracted Text
                      </span>
                      <div className="p-3 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder text-xs text-gray-800 dark:text-gray-200 max-h-[160px] overflow-y-auto font-serif leading-relaxed whitespace-pre-line">
                        {pageData?.page?.page_text || 'No text on this page.'}
                      </div>
                    </div>

                    {/* Detected tables or figures on this page */}
                    {pageData?.tables && pageData.tables.length > 0 && (
                      <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block">
                          Detected Structured Table
                        </span>
                        <div className="p-2.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder text-xs overflow-x-auto whitespace-pre leading-relaxed font-serif">
                          {pageData.tables[0].raw_markdown}
                        </div>
                      </div>
                    )}

                    {pageData?.images && pageData.images.length > 0 && (
                      <div className="bg-white dark:bg-hclsurface-darkcard p-4 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-brand-500 dark:text-brand-300 block">
                          Detected Visual Diagram
                        </span>
                        <div className="p-2 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-2">
                          <img
                            src={pageData.images[0].image_path}
                            alt="diagram"
                            className="max-h-28 mx-auto object-contain rounded"
                          />
                          <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                            {pageData.images[0].generated_description}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentLibrary;
