import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Play,
  CheckCircle2,
  RefreshCw,
  Award,
  HelpCircle,
  Clock
} from 'lucide-react';
import { getBenchmarkDataset, runEvaluationBenchmark, getEvaluationHistory } from '../services/apiService';

const Evaluation = () => {
  const [benchmarkQuestions, setBenchmarkQuestions] = useState([]);
  const [latestRun, setLatestRun] = useState(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [bmRes, histRes] = await Promise.all([
        getBenchmarkDataset(),
        getEvaluationHistory(),
      ]);
      if (bmRes.benchmark_questions) {
        setBenchmarkQuestions(bmRes.benchmark_questions);
      }
      if (histRes.history && histRes.history.length > 0) {
        setLatestRun(histRes.history[0]);
      }
    } catch (err) {
      console.error('Error fetching evaluation data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRunEvaluation = async () => {
    setRunning(true);
    try {
      const res = await runEvaluationBenchmark();
      if (res.status === 'success') {
        setLatestRun(res.evaluation_run);
        fetchData();
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to run benchmark evaluation.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 font-serif">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-hclsurface-darkborder">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-brand-500" />
            <span>Quantitative Benchmark &amp; Retrieval Evaluation</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Empirical evaluation suite calculating Recall@K, MRR, Hit Rate, Faithfulness, and Citation Accuracy.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={running}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold shadow-md transition-colors disabled:opacity-50 font-serif self-start"
        >
          {running ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Running Evaluation Suite...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Run Live Benchmark</span>
            </>
          )}
        </button>
      </div>

      {/* Aggregate Metric Cards */}
      {latestRun ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-hclsurface-darkcard p-5 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm text-center space-y-1">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
              Recall@5
            </span>
            <span className="text-2xl font-bold text-brand-500">
              {(latestRun.recall_at_k * 100).toFixed(1)}%
            </span>
          </div>

          <div className="bg-white dark:bg-hclsurface-darkcard p-5 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm text-center space-y-1">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
              Mean Reciprocal Rank (MRR)
            </span>
            <span className="text-2xl font-bold text-brand-500">
              {latestRun.mrr.toFixed(3)}
            </span>
          </div>

          <div className="bg-white dark:bg-hclsurface-darkcard p-5 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm text-center space-y-1">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
              Faithfulness / Grounding
            </span>
            <span className="text-2xl font-bold text-brand-500">
              {(latestRun.faithfulness_score * 100).toFixed(1)}%
            </span>
          </div>

          <div className="bg-white dark:bg-hclsurface-darkcard p-5 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm text-center space-y-1">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block">
              Citation Accuracy
            </span>
            <span className="text-2xl font-bold text-brand-500">
              {(latestRun.citation_accuracy * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      ) : (
        <div className="p-6 bg-brand-50 dark:bg-hclsurface-darkcard rounded-2xl border border-brand-200 dark:border-hclsurface-darkborder text-center text-xs text-gray-700 dark:text-gray-300">
          Click <strong>Run Live Benchmark</strong> to compute automated Recall@5, MRR, Faithfulness, and Citation Accuracy metrics across multi-domain queries.
        </div>
      )}

      {/* Benchmark Question Set */}
      <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-4">
        <h2 className="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">
          Standard Benchmark Test Questions ({benchmarkQuestions.length})
        </h2>

        <div className="space-y-2">
          {benchmarkQuestions.map((bm, i) => (
            <div
              key={i}
              className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder text-xs flex items-center justify-between"
            >
              <div className="space-y-0.5 max-w-2xl">
                <span className="font-bold text-gray-900 dark:text-white block text-sm">
                  {i + 1}. {bm.question}
                </span>
                <span className="text-xs text-gray-500">
                  Target: {bm.expected_doc} &bull; Page {bm.expected_page} ({bm.content_type})
                </span>
              </div>

              <span className="px-3 py-1 bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 rounded-lg text-xs font-bold border border-brand-200 dark:border-brand-800">
                {bm.domain}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Evaluation;
