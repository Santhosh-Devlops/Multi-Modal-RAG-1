import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Search,
  Layers,
  FileText,
  Table,
  Image,
  ExternalLink,
  Zap,
  BarChart2,
  CheckCircle2,
  HelpCircle
} from 'lucide-react';
import { getQueryHistory, getQueryDetails } from '../services/apiService';

const RetrievedEvidence = () => {
  const [searchParams] = useSearchParams();
  const [queries, setQueries] = useState([]);
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await getQueryHistory();
        if (res.status === 'success' && res.history.length > 0) {
          setQueries(res.history);
          const firstId = res.history[0].id;
          const detailRes = await getQueryDetails(firstId);
          if (detailRes.status === 'success') {
            setSelectedQuery(detailRes.query);
          }
        }
      } catch (err) {
        console.error('Error loading evidence history:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handleSelectQuery = async (id) => {
    try {
      const res = await getQueryDetails(id);
      if (res.status === 'success') {
        setSelectedQuery(res.query);
      }
    } catch (err) {
      console.error('Error loading query detail:', err);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="pb-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <Search className="w-5 h-5 text-brand-600 dark:text-brand-400" />
          <span>Retrieved Evidence & Hybrid Scoring Breakdown</span>
        </h1>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Inspect dense vector similarity (70%), sparse keyword matching (30%), and exact document chunk grounding.
        </p>
      </div>

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : queries.length === 0 ? (
        <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-8">
          <Search className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-gray-900 dark:text-white">No query executions recorded yet</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Ask a question on the Assistant page to view evidence score breakdowns.
          </p>
          <div className="mt-4">
            <Link
              to="/assistant"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm"
            >
              <span>Go to Assistant</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Query Selector List */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-2">
            <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2">
              Query Executions ({queries.length})
            </h2>
            <div className="space-y-1.5 max-h-[600px] overflow-y-auto">
              {queries.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSelectQuery(q.id)}
                  className={`w-full text-left p-3 rounded-lg text-xs transition-all border ${
                    selectedQuery?.id === q.id
                      ? 'bg-brand-50 border-brand-300 text-brand-900 dark:bg-brand-950/60 dark:border-brand-800 dark:text-brand-200 font-semibold'
                      : 'bg-gray-50 dark:bg-gray-900/60 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                      {q.domain}
                    </span>
                    <span className="text-[10px] text-gray-400">
                      {new Date(q.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="line-clamp-2 leading-relaxed">{q.question}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Evidence Detail View */}
          <div className="lg:col-span-2 space-y-4">
            {selectedQuery && (
              <>
                <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 block mb-1">
                    Inspecting Query Question
                  </span>
                  <h2 className="text-sm font-bold text-gray-900 dark:text-white mb-2">
                    "{selectedQuery.question}"
                  </h2>
                  <div className="flex flex-wrap gap-2 text-[11px]">
                    <span className="px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 font-medium">
                      Intent: {selectedQuery.intent}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-medium">
                      Status: {selectedQuery.verification_status}
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                    Ranked Evidence Chunks ({selectedQuery.evidence?.length || 0})
                  </h3>

                  {selectedQuery.evidence?.map((ev, idx) => (
                    <div
                      key={ev.id || idx}
                      className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-brand-600 text-white flex items-center justify-center text-[10px] font-bold">
                            #{idx + 1}
                          </span>
                          <span className="text-xs font-bold text-gray-900 dark:text-white">
                            {ev.document_name || `Document #${ev.document_id}`}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                            Page {ev.page_number}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                            {ev.content_type}
                          </span>
                        </div>

                        <Link
                          to={`/explorer?docId=${ev.document_id}&page=${ev.page_number}`}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline"
                        >
                          <span>Explore Page</span>
                          <ExternalLink className="w-3 h-3" />
                        </Link>
                      </div>

                      <div className="p-3 bg-gray-50 dark:bg-gray-900/70 rounded-lg border border-gray-100 dark:border-gray-800 font-mono text-[11px] text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                        {ev.snippet || ev.content_text}
                      </div>

                      {/* Score Breakdown Bar */}
                      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-100 dark:border-gray-700 text-center text-[11px]">
                        <div className="p-1.5 bg-blue-50 dark:bg-blue-950/40 rounded border border-blue-100 dark:border-blue-900">
                          <span className="text-gray-500 dark:text-gray-400 block text-[10px]">Semantic (70%)</span>
                          <span className="font-bold text-blue-700 dark:text-blue-300">{(ev.semantic_score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="p-1.5 bg-purple-50 dark:bg-purple-950/40 rounded border border-purple-100 dark:border-purple-900">
                          <span className="text-gray-500 dark:text-gray-400 block text-[10px]">Keyword (30%)</span>
                          <span className="font-bold text-purple-700 dark:text-purple-300">{(ev.keyword_score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="p-1.5 bg-emerald-50 dark:bg-emerald-950/40 rounded border border-emerald-100 dark:border-emerald-900">
                          <span className="text-gray-500 dark:text-gray-400 block text-[10px]">Hybrid Score</span>
                          <span className="font-bold text-emerald-700 dark:text-emerald-300">{(ev.hybrid_score * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RetrievedEvidence;
