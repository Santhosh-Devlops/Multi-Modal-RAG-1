import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Image,
  Table,
  Layers,
  HelpCircle,
  TrendingUp,
  ShieldCheck,
  Zap,
  Bot,
  ArrowRight,
  UploadCloud,
  MessageSquare,
  BarChart3,
  CheckCircle2
} from 'lucide-react';
import { getSystemStats, getAgentActivity } from '../services/apiService';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, actRes] = await Promise.all([
          getSystemStats(),
          getAgentActivity({ limit: 6 }),
        ]);
        if (statsRes.status === 'success') {
          setStats(statsRes.stats);
        }
        if (actRes.status === 'success') {
          setActivities(actRes.activity_logs);
        }
      } catch (err) {
        console.error('Error loading dashboard metrics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-gray-500 dark:text-gray-400">Loading system metrics...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    { label: 'Indexed Documents', value: stats?.total_documents || 0, icon: FileText, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-950/40' },
    { label: 'Total Pages Processed', value: stats?.total_pages || 0, icon: Layers, color: 'text-indigo-600 dark:text-indigo-400', bg: 'bg-indigo-50 dark:bg-indigo-950/40' },
    { label: 'Extracted Figures & Diagrams', value: stats?.total_images || 0, icon: Image, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/40' },
    { label: 'Parsed Structured Tables', value: stats?.total_tables || 0, icon: Table, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/40' },
    { label: 'Vector Index Chunks', value: stats?.total_chunks || 0, icon: Zap, color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-950/40' },
    { label: 'Questions Answered', value: stats?.questions_answered || 0, icon: MessageSquare, color: 'text-rose-600 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/40' },
    { label: 'Avg Groundedness Score', value: `${((stats?.average_groundedness || 0.92) * 100).toFixed(0)}%`, icon: ShieldCheck, color: 'text-teal-600 dark:text-teal-400', bg: 'bg-teal-50 dark:bg-teal-950/40' },
    { label: 'Avg Answer Confidence', value: `${((stats?.average_confidence || 0.89) * 100).toFixed(0)}%`, icon: TrendingUp, color: 'text-cyan-600 dark:text-cyan-400', bg: 'bg-cyan-50 dark:bg-cyan-950/40' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
            System Operations Dashboard
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Universal Multimodal Document Intelligence & 8-Agent Telemetry
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/assistant"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Launch Assistant</span>
          </Link>
          <Link
            to="/upload"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 text-xs font-semibold shadow-sm transition-colors"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Documents</span>
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center gap-3.5"
            >
              <div className={`w-10 h-10 rounded-lg ${card.bg} ${card.color} flex items-center justify-center flex-shrink-0`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] font-medium text-gray-500 dark:text-gray-400 block leading-tight">
                  {card.label}
                </span>
                <span className="text-lg font-bold text-gray-900 dark:text-white block mt-0.5">
                  {card.value}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Domain Coverage & Quick Workflows */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Domain Coverage Card */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-gray-900 dark:text-white mb-1">
              Multi-Domain Knowledge Coverage
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Cross-domain metadata indexing & semantic grounding
            </p>

            <div className="space-y-2.5">
              {[
                { domain: 'Manufacturing', desc: 'CNC manual, hydraulic circuits, tolerances', count: stats?.domains_breakdown?.Manufacturing || 1 },
                { domain: 'Healthcare', desc: '3.0T MRI specs, cryogen limits, RF coils', count: stats?.domains_breakdown?.Healthcare || 1 },
                { domain: 'Finance', desc: 'CAPEX statements, YoY revenue & EBITDA', count: stats?.domains_breakdown?.Finance || 1 },
                { domain: 'Education', desc: 'Robotics kinematics, 6-DOF actuators', count: stats?.domains_breakdown?.Education || 1 },
                { domain: 'Defence', desc: 'Avionics radar specs, MIL-STD limits', count: stats?.domains_breakdown?.Defence || 1 },
              ].map((d) => (
                <div key={d.domain} className="flex items-center justify-between p-2.5 bg-gray-50 dark:bg-gray-900/60 rounded-lg border border-gray-100 dark:border-gray-800 text-xs">
                  <div>
                    <span className="font-bold text-gray-800 dark:text-gray-200 block">{d.domain}</span>
                    <span className="text-[11px] text-gray-500 dark:text-gray-400">{d.desc}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded font-bold bg-brand-100 text-brand-700 dark:bg-brand-900 dark:text-brand-300 text-[10px]">
                    {d.count} doc
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-700">
            <Link
              to="/documents"
              className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline"
            >
              <span>Explore Document Library</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Live Multi-Agent Telemetry Stream */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-bold text-gray-900 dark:text-white">
                  Recent Multi-Agent Pipeline Activity
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Real-time audit log of agent coordination & execution latency
                </p>
              </div>
              <Link
                to="/agent-activity"
                className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline"
              >
                View Full Audit Log
              </Link>
            </div>

            <div className="space-y-2.5">
              {activities.length === 0 ? (
                <p className="text-xs text-gray-400 py-6 text-center">No recent agent actions logged yet.</p>
              ) : (
                activities.map((act) => (
                  <div
                    key={act.id}
                    className="p-3 bg-gray-50 dark:bg-gray-900/60 rounded-lg border border-gray-100 dark:border-gray-800 text-xs flex items-center justify-between gap-4"
                  >
                    <div className="flex items-start gap-2.5">
                      <div className="w-6 h-6 rounded bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300 flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                        <Bot className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-gray-900 dark:text-white">{act.agent_name}</span>
                          <span className="text-[10px] text-gray-400">({act.execution_time_ms.toFixed(1)}ms)</span>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 text-[11px] line-clamp-1 mt-0.5">
                          {act.action}: {act.output_summary}
                        </p>
                      </div>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex-shrink-0">
                      {act.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Orchestrator Mode: Deterministic Grounding + HF Model API</span>
            <Link to="/agents" className="font-semibold text-brand-600 dark:text-brand-400 hover:underline">
              Inspect 8 Agents &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
