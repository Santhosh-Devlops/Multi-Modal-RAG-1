import React, { useState, useEffect } from 'react';
import { 
  X, 
  Search, 
  FileText, 
  Image as ImageIcon, 
  TrendingUp, 
  Table as TableIcon, 
  Hash, 
  FunctionSquare,
  RefreshCw, 
  AlertCircle,
  Eye,
  Copy,
  Check,
  Layers
} from 'lucide-react';
import { fetchExtractorData } from '../services/apiService';

const ExtractorModal = ({ isOpen, onClose, documentId, documentName, initialTab = 'text' }) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');
  const [error, setError] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  useEffect(() => {
    if (isOpen && documentId) {
      loadData(activeTab);
    }
  }, [isOpen, documentId, activeTab]);

  const loadData = async (type) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchExtractorData(documentId, type);
      setData(res);
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to load ${type} extractor data`);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (!isOpen) return null;

  const tabs = [
    { id: 'text', label: 'Text Extractor', icon: FileText, count: data?.total_pages },
    { id: 'images', label: 'Image Extractor', icon: ImageIcon, count: data?.total_images },
    { id: 'graphs', label: 'Graphs & Visuals', icon: TrendingUp, count: data?.total_graphs },
    { id: 'tables', label: 'Table Extractor', icon: TableIcon, count: data?.total_tables },
    { id: 'equations', label: 'Equation Extractor', icon: FunctionSquare, count: data?.total_equations },
    { id: 'numericals', label: 'Numerical Extractor', icon: Hash, count: data?.total_numericals },
  ];

  // Helper to parse raw markdown table string into clean headers & rows
  const parseMarkdownTable = (mdStr) => {
    if (!mdStr || !mdStr.includes('|')) return null;
    const lines = mdStr.split('\n').filter(l => l.trim().startsWith('|'));
    if (lines.length < 2) return null;
    const headers = lines[0].split('|').map(c => c.trim()).filter(Boolean);
    const rows = lines.slice(2).map(line => 
      line.split('|').map(c => c.trim()).filter(Boolean)
    ).filter(r => r.length > 0);
    return { headers, rows };
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 md:p-6 bg-black/75 backdrop-blur-md animate-in fade-in duration-200 select-none">
      
      {/* Expanded Modal Window (Large 96vw / 94vh) */}
      <div className="bg-white dark:bg-[#120E24] border border-slate-300 dark:border-[#282252] rounded-3xl w-[96vw] max-w-[1400px] h-[94vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header Bar */}
        <div className="px-8 py-5 border-b border-slate-200 dark:border-[#282252] flex items-center justify-between bg-slate-50 dark:bg-[#0D0A1C]/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-brand-600 text-white shadow-md shadow-brand-500/25">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                  Extractor Inspector: <span className="text-brand-600 dark:text-brand-400">{documentName || 'Document'}</span>
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-brand-100 text-brand-700 dark:bg-brand-900/60 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  Open-Source Multi-Model Extraction
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Inspect extracted tables (images & HTML), mathematical equations, visual diagrams, and document text.
              </p>
            </div>
          </div>

          {/* Prominent Close Marker Button */}
          <button
            onClick={onClose}
            className="p-2.5 rounded-full bg-slate-100 dark:bg-[#1A1435] text-slate-500 hover:text-white hover:bg-red-500 dark:hover:bg-red-600 border border-slate-300 dark:border-[#2E2557] transition-all shadow-sm group"
            title="Close Window (Esc)"
          >
            <X className="w-5 h-5 group-hover:scale-110 transition-transform" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 dark:border-[#282252] px-8 bg-slate-100/60 dark:bg-[#0D0A1C]/50 gap-2 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2.5 py-3.5 px-5 border-b-2 font-extrabold text-sm transition-all whitespace-nowrap ${
                  isActive
                    ? 'border-brand-500 text-brand-600 dark:text-brand-400 bg-white dark:bg-[#120E24] shadow-sm'
                    : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/40 dark:hover:bg-slate-800/30'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {data && activeTab === tab.id && (
                  <span className="ml-1 text-xs px-2 py-0.5 rounded-full bg-slate-200 dark:bg-[#201A40] text-slate-700 dark:text-slate-300 font-extrabold">
                    {tab.count !== undefined ? tab.count : ''}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Search & Filter Bar */}
        <div className="px-8 py-3.5 border-b border-slate-200 dark:border-[#282252] flex items-center justify-between gap-4 bg-white dark:bg-[#120E24]">
          <div className="relative flex-1 max-w-lg">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder={`Search within extracted ${activeTab}...`}
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-xs bg-slate-50 dark:bg-[#0D0A1C] border border-slate-300 dark:border-[#282252] rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => loadData(activeTab)}
              className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-[#1A1435] hover:bg-slate-200 dark:hover:bg-[#251E4E] rounded-xl transition-colors border border-slate-300 dark:border-[#2E2557] shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 p-8 overflow-y-auto bg-[#F9F9FB] dark:bg-[#0D0A1C]/40">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center gap-3">
              <RefreshCw className="w-9 h-9 text-brand-500 animate-spin" />
              <p className="text-sm font-bold text-slate-600 dark:text-slate-400">Extracting {activeTab} from document...</p>
            </div>
          ) : error ? (
            <div className="p-5 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-2xl text-red-700 dark:text-red-300 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm font-bold">{error}</p>
            </div>
          ) : !data ? (
            <div className="text-center py-16 text-slate-500 font-bold">No extracted content found.</div>
          ) : (
            <div>

              {/* TAB 1: TEXT EXTRACTOR */}
              {activeTab === 'text' && (
                <div className="space-y-5">
                  {data.pages
                    ?.filter((p) => p.page_text?.toLowerCase().includes(searchFilter.toLowerCase()))
                    .map((p) => (
                      <div key={p.id} className="p-6 bg-white dark:bg-[#16122E] border border-slate-200 dark:border-[#282252] rounded-2xl shadow-sm space-y-3">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-[#201A40]">
                          <div className="flex items-center gap-2">
                            <span className="px-3 py-1 text-xs font-extrabold bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-300 rounded-lg border border-brand-200 dark:border-brand-800">
                              Page {p.page_number}
                            </span>
                            <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                              Document Text Layer
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-slate-400 font-medium">
                              {p.page_text?.split(/\s+/).length || 0} words
                            </span>
                            <button
                              onClick={() => handleCopy(p.id, p.page_text)}
                              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-[#201A40]"
                              title="Copy Page Text"
                            >
                              {copiedId === p.id ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed font-sans select-text">
                          {p.page_text}
                        </p>
                      </div>
                    ))}
                </div>
              )}

              {/* TAB 2: IMAGE EXTRACTOR */}
              {activeTab === 'images' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {data.images
                    ?.filter((img) => (img.generated_description + ' ' + (img.ocr_text || '')).toLowerCase().includes(searchFilter.toLowerCase()))
                    .map((img) => (
                      <div key={img.id} className="p-5 bg-white dark:bg-[#16122E] border border-slate-200 dark:border-[#282252] rounded-2xl shadow-sm flex flex-col gap-3 group">
                        
                        {/* High Resolution Rendered Image Thumbnail */}
                        <div className="relative w-full h-52 rounded-xl overflow-hidden bg-slate-100 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] flex items-center justify-center">
                          {img.image_path ? (
                            <img
                              src={img.image_path}
                              alt={img.image_name || 'Extracted Image'}
                              className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300 cursor-pointer"
                              onClick={() => setPreviewImage(img.image_path)}
                              onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%238E57D8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
                              }}
                            />
                          ) : (
                            <div className="text-slate-400 flex flex-col items-center gap-1">
                              <ImageIcon className="w-10 h-10 text-slate-400" />
                              <span className="text-xs">Diagram Preview</span>
                            </div>
                          )}
                          <button
                            onClick={() => setPreviewImage(img.image_path)}
                            className="absolute bottom-2.5 right-2.5 px-3 py-1.5 bg-black/75 hover:bg-black text-white rounded-lg text-xs font-bold flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>Zoom</span>
                          </button>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="px-3 py-1 text-xs font-extrabold bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 rounded-lg border border-blue-200 dark:border-blue-800">
                            Page {img.page_number} • {img.image_type}
                          </span>
                          <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold">
                            Confidence: {Math.round((img.confidence_score || 0.9) * 100)}%
                          </span>
                        </div>

                        <div className="p-3.5 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl border border-slate-100 dark:border-[#201A40]">
                          <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Vision Description ({img.image_name})</p>
                          <p className="text-xs font-medium text-slate-800 dark:text-slate-200 leading-relaxed">{img.generated_description}</p>
                        </div>

                        {img.ocr_text && (
                          <div className="p-3.5 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl border border-slate-100 dark:border-[#201A40]">
                            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Extracted OCR Text</p>
                            <p className="text-xs text-slate-700 dark:text-slate-300 font-mono select-text">{img.ocr_text}</p>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}

              {/* TAB 3: GRAPHS & VISUALS */}
              {activeTab === 'graphs' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {data.graphs
                    ?.filter((gr) => (gr.title + ' ' + gr.visual_explanation).toLowerCase().includes(searchFilter.toLowerCase()))
                    .map((gr) => (
                      <div key={gr.id} className="p-6 bg-white dark:bg-[#16122E] border border-slate-200 dark:border-[#282252] rounded-2xl shadow-sm space-y-4">
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                            <h4 className="text-base font-extrabold text-slate-900 dark:text-white">{gr.title}</h4>
                          </div>
                          <span className="px-3 py-1 text-xs font-extrabold bg-purple-50 dark:bg-purple-950 text-purple-700 dark:text-purple-300 rounded-lg border border-purple-200 dark:border-purple-800">
                            Page {gr.page_number} • {gr.graph_type}
                          </span>
                        </div>

                        {/* Rendered Visual Diagram Crop */}
                        <div className="relative w-full h-64 rounded-2xl overflow-hidden bg-slate-100 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] flex items-center justify-center group">
                          {gr.image_path ? (
                            <img
                              src={gr.image_path}
                              alt={gr.title}
                              className="w-full h-full object-contain p-2 cursor-pointer group-hover:scale-105 transition-transform duration-300"
                              onClick={() => setPreviewImage(gr.image_path)}
                            />
                          ) : (
                            <div className="text-slate-400 flex flex-col items-center gap-1">
                              <TrendingUp className="w-10 h-10 text-brand-500" />
                              <span className="text-xs">Diagram Preview</span>
                            </div>
                          )}
                          <button
                            onClick={() => setPreviewImage(gr.image_path)}
                            className="absolute bottom-3 right-3 px-3.5 py-1.5 bg-black/75 hover:bg-black text-white rounded-xl text-xs font-bold flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                          >
                            <Eye className="w-4 h-4" />
                            <span>Zoom Preview</span>
                          </button>
                        </div>

                        <p className="text-xs md:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                          {gr.visual_explanation}
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                          <div className="p-3.5 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl border border-slate-100 dark:border-[#201A40]">
                            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Mapping</p>
                            <p className="text-xs font-medium text-slate-800 dark:text-slate-200 mt-1">{gr.axis_info || 'Process flow mapping'}</p>
                          </div>
                          <div className="p-3.5 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl border border-slate-100 dark:border-[#201A40]">
                            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Extracted Trend & Flow</p>
                            <p className="text-xs font-medium text-slate-800 dark:text-slate-200 mt-1">{gr.trend_summary || 'Multi-stage sequence flow'}</p>
                          </div>
                        </div>

                      </div>
                    ))}
                </div>
              )}

              {/* TAB 4: TABLE EXTRACTOR (VISUAL CROPPED IMAGE + STRUCTURED HTML TABLE) */}
              {activeTab === 'tables' && (
                <div className="space-y-8">
                  {data.tables
                    ?.filter((t) => (t.title + ' ' + t.natural_language_text).toLowerCase().includes(searchFilter.toLowerCase()))
                    .map((t) => {
                      const parsed = parseMarkdownTable(t.raw_markdown);
                      return (
                        <div key={t.id} className="p-6 bg-white dark:bg-[#16122E] border border-slate-200 dark:border-[#282252] rounded-3xl shadow-sm space-y-5">
                          
                          {/* Table Header Row */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <TableIcon className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                              <h3 className="text-base font-extrabold text-slate-900 dark:text-white">{t.title}</h3>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="px-3 py-1 text-xs font-extrabold bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 rounded-lg border border-emerald-200 dark:border-emerald-800">
                                Page {t.page_number} • {t.row_count} Rows × {t.column_count} Cols
                              </span>
                              <button
                                onClick={() => handleCopy(t.id, t.raw_markdown)}
                                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-[#201A40]"
                                title="Copy Markdown Table"
                              >
                                {copiedId === t.id ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                              </button>
                            </div>
                          </div>

                          {/* 1. Visual Cropped Table Preview (If available) */}
                          {t.image_path && (
                            <div className="relative w-full rounded-2xl overflow-hidden bg-slate-100 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] flex items-center justify-center p-3 group">
                              <img
                                src={t.image_path}
                                alt="Visual table image crop"
                                className="max-h-64 object-contain rounded-xl cursor-pointer group-hover:scale-[1.02] transition-transform"
                                onClick={() => setPreviewImage(t.image_path)}
                              />
                              <button
                                onClick={() => setPreviewImage(t.image_path)}
                                className="absolute bottom-3 right-3 px-3 py-1 bg-black/75 hover:bg-black text-white rounded-lg text-xs font-bold flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <Eye className="w-3.5 h-3.5" />
                                <span>Zoom Table Image</span>
                              </button>
                            </div>
                          )}

                          {/* 2. REAL STRUCTURED HTML DATA TABLE */}
                          {parsed && parsed.headers.length > 0 ? (
                            <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-[#282252] bg-white dark:bg-[#0D0A1C]">
                              <table className="w-full text-left text-xs border-collapse">
                                <thead className="bg-slate-100 dark:bg-[#1A1435] text-slate-900 dark:text-white uppercase font-extrabold tracking-wider border-b border-slate-200 dark:border-[#282252]">
                                  <tr>
                                    <th className="py-3.5 px-4 w-12 text-center text-slate-400">#</th>
                                    {parsed.headers.map((head, h_i) => (
                                      <th key={h_i} className="py-3.5 px-4">{head}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 dark:divide-[#201A40]">
                                  {parsed.rows.map((row, r_i) => (
                                    <tr key={r_i} className="hover:bg-purple-50/40 dark:hover:bg-slate-800/30 transition-colors">
                                      <td className="py-3 px-4 text-center font-bold text-slate-400">{r_i + 1}</td>
                                      {row.map((cell, c_i) => (
                                        <td key={c_i} className={`py-3 px-4 ${c_i === 0 ? 'font-bold text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300'}`}>
                                          {cell}
                                        </td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <div className="p-4 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl text-xs font-mono whitespace-pre-wrap">
                              {t.raw_markdown}
                            </div>
                          )}

                          <p className="text-xs text-slate-500 dark:text-slate-400 italic">
                            Natural Language Representation: {t.natural_language_text}
                          </p>
                        </div>
                      );
                    })}
                </div>
              )}

              {/* TAB 5: DYNAMIC EQUATION EXTRACTOR (REAL LATEX FORMULAS FROM SOURCE DOCUMENT) */}
              {activeTab === 'equations' && (
                <div className="space-y-6">
                  
                  {/* Header Banner */}
                  <div className="p-5 bg-purple-50/80 dark:bg-[#16122E] border border-brand-200 dark:border-[#282252] rounded-2xl flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-extrabold text-brand-900 dark:text-brand-300 flex items-center gap-2">
                        <FunctionSquare className="w-4 h-4" />
                        <span>Dynamic Mathematical Equations & Formula Models</span>
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                        All equations are parsed directly from the uploaded document text and rendered in LaTeX mathematical syntax ($$...$$).
                      </p>
                    </div>
                  </div>

                  {/* Math Formula Display Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {data.equations
                      ?.filter((eq) => (eq.parameter_name + ' ' + eq.context_sentence).toLowerCase().includes(searchFilter.toLowerCase()))
                      .map((eq, idx) => (
                        <div key={idx} className="p-6 bg-white dark:bg-[#16122E] border border-brand-200 dark:border-[#282252] rounded-3xl shadow-sm space-y-4">
                          
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400 truncate max-w-[240px]">
                              {eq.parameter_name}
                            </h4>
                            <span className="px-2.5 py-0.5 rounded-md bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-300 text-xs font-extrabold">
                              {eq.equation_number || `Eq. (P.${eq.page_number})`} • Page {eq.page_number}
                            </span>
                          </div>

                          {/* Mathematical Equation Display Box */}
                          <div className="p-5 bg-purple-50/60 dark:bg-[#0D0A1C] border border-brand-200/80 dark:border-[#2E2557] rounded-2xl text-center overflow-x-auto">
                            <span className="font-serif text-lg md:text-xl font-extrabold text-brand-900 dark:text-brand-200 tracking-wide select-text">
                              {eq.equation_expression.replace(/\$\$/g, '')}
                            </span>
                          </div>

                          {/* Context Sentence */}
                          <div className="p-3.5 bg-slate-50 dark:bg-[#0D0A1C] rounded-xl border border-slate-100 dark:border-[#201A40]">
                            <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1">Source Document Context</p>
                            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">{eq.context_sentence}</p>
                          </div>

                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* TAB 6: NUMERICAL EXTRACTOR */}
              {activeTab === 'numericals' && (
                <div className="space-y-6">
                  <div className="bg-white dark:bg-[#16122E] border border-slate-200 dark:border-[#282252] rounded-3xl overflow-hidden shadow-sm">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-slate-100 dark:bg-[#1A1435] text-slate-900 dark:text-white uppercase font-extrabold tracking-wider border-b border-slate-200 dark:border-[#282252]">
                        <tr>
                          <th className="py-4 px-5">Page</th>
                          <th className="py-4 px-5">Parameter Specification</th>
                          <th className="py-4 px-5">Measured Value & Unit</th>
                          <th className="py-4 px-5">Category</th>
                          <th className="py-4 px-5">Physical Context Sentence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-[#201A40]">
                        {data.numericals
                          ?.filter((num) => (num.parameter_name + ' ' + num.context_sentence).toLowerCase().includes(searchFilter.toLowerCase()))
                          .map((num) => (
                            <tr key={num.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                              <td className="py-3.5 px-5 font-bold text-slate-400">P.{num.page_number}</td>
                              <td className="py-3.5 px-5 font-extrabold text-slate-900 dark:text-white">{num.parameter_name}</td>
                              <td className="py-3.5 px-5 font-mono font-extrabold text-brand-600 dark:text-brand-400 text-sm">
                                {num.numerical_value} {num.unit}
                              </td>
                              <td className="py-3.5 px-5">
                                <span className="px-3 py-1 text-xs rounded-full font-extrabold bg-purple-50 dark:bg-[#201A40] text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-[#2E2557]">
                                  {num.category}
                                </span>
                              </td>
                              <td className="py-3.5 px-5 text-xs text-slate-600 dark:text-slate-300 max-w-md truncate" title={num.context_sentence}>
                                {num.context_sentence}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </div>

      {/* Expanded Image Zoom Modal */}
      {previewImage && (
        <div 
          className="fixed inset-0 z-60 bg-black/90 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setPreviewImage(null)}
        >
          <div className="relative max-w-5xl max-h-[90vh] bg-slate-950 p-3 rounded-3xl border border-slate-700 shadow-2xl">
            <button
              onClick={() => setPreviewImage(null)}
              className="absolute -top-3.5 -right-3.5 p-2 bg-brand-600 hover:bg-brand-700 text-white rounded-full shadow-xl border-2 border-white/20"
            >
              <X className="w-5 h-5" />
            </button>
            <img 
              src={previewImage} 
              alt="Expanded Preview" 
              className="max-h-[85vh] max-w-full rounded-2xl object-contain"
            />
          </div>
        </div>
      )}

    </div>
  );
};

export default ExtractorModal;
