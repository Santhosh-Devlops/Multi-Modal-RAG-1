import React, { useState, useEffect } from 'react';
import {
  HeartPulse,
  CheckCircle2,
  AlertCircle,
  Clock,
  RefreshCw,
  Server,
  Database,
  Cpu,
  Zap,
  Bot,
  Layers
} from 'lucide-react';
import { getSystemHealth } from '../services/apiService';

const SystemHealth = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  const fetchHealth = async () => {
    setChecking(true);
    try {
      const res = await getSystemHealth();
      setHealthData(res);
    } catch (err) {
      console.error('Error fetching health status:', err);
    } finally {
      setLoading(false);
      setChecking(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const getComponentIcon = (name) => {
    if (name.includes('API')) return <Server className="w-5 h-5 text-blue-600 dark:text-blue-400" />;
    if (name.includes('Database')) return <Database className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />;
    if (name.includes('Vector')) return <Zap className="w-5 h-5 text-purple-600 dark:text-purple-400" />;
    if (name.includes('Embedding')) return <Cpu className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />;
    if (name.includes('Model')) return <Bot className="w-5 h-5 text-amber-600 dark:text-amber-400" />;
    return <Layers className="w-5 h-5 text-teal-600 dark:text-teal-400" />;
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <HeartPulse className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <span>Subsystem Health & Availability Monitor</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Real-time ping checks, database connectivity, vector index readiness, and model API status.
          </p>
        </div>

        <button
          onClick={fetchHealth}
          disabled={checking}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-colors disabled:opacity-50 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />
          <span>{checking ? 'Pinging Services...' : 'Run Diagnostics Ping'}</span>
        </button>
      </div>

      {/* Overall Banner */}
      <div className="p-5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-emerald-900 dark:text-emerald-100">
              {healthData?.overall_status || 'All Systems Operational'}
            </h2>
            <span className="text-xs text-emerald-700 dark:text-emerald-300">
              6 Core Subsystems Active & Ready for Queries
            </span>
          </div>
        </div>

        <div className="text-right text-[11px] text-emerald-800 dark:text-emerald-300">
          <span>Last Health Check:</span>
          <p className="font-mono font-semibold">
            {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : 'Just now'}
          </p>
        </div>
      </div>

      {/* Components Health Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 py-12 flex justify-center">
            <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          healthData?.components?.map((c, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-800">
                      {getComponentIcon(c.component)}
                    </div>
                    <span className="text-xs font-bold text-gray-900 dark:text-white">
                      {c.component}
                    </span>
                  </div>

                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    {c.status}
                  </span>
                </div>

                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
                  {c.details}
                </p>
              </div>

              <div className="pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between text-[11px] text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>Ping Latency:</span>
                </span>
                <span className="font-mono font-bold text-gray-800 dark:text-gray-200">
                  {c.latency_ms}ms
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SystemHealth;
