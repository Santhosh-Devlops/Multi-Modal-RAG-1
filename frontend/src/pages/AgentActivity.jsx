import React, { useState, useEffect } from 'react';
import {
  Activity,
  Bot,
  Filter,
  Clock,
  Zap,
  CheckCircle2,
  AlertCircle,
  Search,
  RefreshCw
} from 'lucide-react';
import { getAgentActivity } from '../services/apiService';

const AGENT_NAMES = [
  'All',
  'Document Processing Agent',
  'Image Understanding Agent',
  'Table Understanding Agent',
  'Query Understanding Agent',
  'Retrieval Agent',
  'Evidence Validation Agent',
  'RAG Answer Agent',
  'Response Verification Agent'
];

const AgentActivity = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agentFilter, setAgentFilter] = useState('All');
  const [traceSearch, setTraceSearch] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await getAgentActivity({
        agent_name: agentFilter !== 'All' ? agentFilter : undefined,
        trace_id: traceSearch.trim() || undefined,
        limit: 100
      });
      if (res.status === 'success') {
        setLogs(res.activity_logs);
      }
    } catch (err) {
      console.error('Error fetching agent activity:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [agentFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchLogs();
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            <span>Multi-Agent Activity & Telemetry Audit</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Real-time execution log of every agent action, input payload, output summary, and execution latency.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by trace ID (e.g. trace_...)"
            value={traceSearch}
            onChange={(e) => setTraceSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500"
          />
        </form>

        <div className="flex items-center gap-2 text-xs w-full sm:w-auto">
          <span className="text-gray-500 dark:text-gray-400 font-medium">Filter Agent:</span>
          <select
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
            className="px-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white font-medium"
          >
            {AGENT_NAMES.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Activity Timeline List */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
            Telemetry Events ({logs.length})
          </h2>
          <span className="text-[11px] text-gray-400">Continuous Ingestion & Query Telemetry</span>
        </div>

        {loading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 text-gray-400 text-xs">
            No activity logs found for selected filter.
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700/60 max-h-[700px] overflow-y-auto">
            {logs.map((log) => (
              <div key={log.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300 flex items-center justify-center font-bold text-xs">
                      <Bot className="w-3.5 h-3.5" />
                    </span>
                    <span className="text-xs font-bold text-gray-900 dark:text-white">
                      {log.agent_name}
                    </span>
                    <span className="text-[11px] text-gray-400 font-mono">
                      [{log.trace_id}]
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    <span className="flex items-center gap-1 text-gray-500 dark:text-gray-400 font-mono text-[11px]">
                      <Clock className="w-3 h-3" />
                      <span>{log.execution_time_ms.toFixed(1)}ms</span>
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        log.status === 'Success'
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                          : log.status === 'Warning'
                          ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800'
                          : 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                      }`}
                    >
                      {log.status}
                    </span>
                  </div>
                </div>

                <div className="text-xs">
                  <span className="font-semibold text-brand-700 dark:text-brand-300">Action: </span>
                  <span className="text-gray-800 dark:text-gray-200 font-medium">{log.action}</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                  {log.input_summary && (
                    <div className="p-2 bg-gray-50 dark:bg-gray-900/60 rounded border border-gray-100 dark:border-gray-800">
                      <span className="text-[10px] font-semibold text-gray-400 block uppercase">Input Spec</span>
                      <span className="text-gray-700 dark:text-gray-300 font-mono line-clamp-2">{log.input_summary}</span>
                    </div>
                  )}
                  {log.output_summary && (
                    <div className="p-2 bg-gray-50 dark:bg-gray-900/60 rounded border border-gray-100 dark:border-gray-800">
                      <span className="text-[10px] font-semibold text-gray-400 block uppercase">Output Result</span>
                      <span className="text-gray-700 dark:text-gray-300 font-mono line-clamp-2">{log.output_summary}</span>
                    </div>
                  )}
                </div>

                <div className="text-[10px] text-gray-400 text-right">
                  {new Date(log.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentActivity;
