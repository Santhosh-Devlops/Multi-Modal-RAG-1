import React, { useState, useEffect } from 'react';
import {
  Bot,
  ShieldCheck,
  CheckCircle2,
  Workflow,
  FileText,
  Image,
  Table,
  Search,
  MessageSquare
} from 'lucide-react';
import { getAgents, getAgentActivity } from '../services/apiService';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [activities, setActivities] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentRes, actRes] = await Promise.all([
          getAgents(),
          getAgentActivity({ limit: 40 }),
        ]);
        if (agentRes.status === 'success') {
          setAgents(agentRes.agents);
          if (agentRes.agents.length > 0) {
            setSelectedAgent(agentRes.agents[0]);
          }
        }
        if (actRes.status === 'success') {
          setActivities(actRes.activity_logs);
        }
      } catch (err) {
        console.error('Error loading agents:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getAgentIcon = (key) => {
    switch (key) {
      case 'document_agent': return <FileText className="w-5 h-5 text-brand-500" />;
      case 'image_agent': return <Image className="w-5 h-5 text-brand-500" />;
      case 'table_agent': return <Table className="w-5 h-5 text-brand-500" />;
      case 'query_agent': return <MessageSquare className="w-5 h-5 text-brand-500" />;
      case 'retrieval_agent': return <Search className="w-5 h-5 text-brand-500" />;
      case 'evidence_agent': return <ShieldCheck className="w-5 h-5 text-brand-500" />;
      case 'answer_agent': return <Bot className="w-5 h-5 text-brand-500" />;
      case 'verification_agent': return <CheckCircle2 className="w-5 h-5 text-brand-500" />;
      default: return <Bot className="w-5 h-5 text-brand-500" />;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 font-serif">
      {/* Header */}
      <div className="pb-4 border-b border-gray-200 dark:border-hclsurface-darkborder">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <Workflow className="w-6 h-6 text-brand-500" />
          <span>Sequential Multi-Agent Architecture &amp; Telemetry</span>
        </h1>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Explore the 8 specialized agents operating in sequential order to ingest, extract, retrieve, synthesize, and verify document answers.
        </p>
      </div>

      {/* Sequential Agents Pipeline Grid */}
      <div className="space-y-4">
        <h2 className="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">
          The 8 Sequential Pipeline Agents
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent, idx) => (
            <div
              key={agent.id}
              onClick={() => setSelectedAgent(agent)}
              className={`p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between ${
                selectedAgent?.id === agent.id
                  ? 'bg-brand-50 dark:bg-hclsurface-dark border-brand-500 shadow-md'
                  : 'bg-white dark:bg-hclsurface-darkcard border-gray-200 dark:border-hclsurface-darkborder hover:border-brand-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 bg-brand-50 dark:bg-hclsurface-dark rounded-xl border border-brand-100 dark:border-brand-900">
                    {getAgentIcon(agent.agent_key)}
                  </div>
                  <span className="w-6 h-6 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold text-xs">
                    {idx + 1}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-1">
                  {agent.agent_name}
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                  {agent.role_description}
                </p>
              </div>

              <div className="pt-3 mt-3 border-t border-gray-100 dark:border-hclsurface-darkborder flex items-center justify-between text-xs text-gray-500 font-bold">
                <span className="text-emerald-600 dark:text-emerald-400">● {agent.status || 'Active'}</span>
                <span>{agent.total_tasks_executed || 0} runs</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Agent Details & Live Telemetry Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Selected Agent Specification */}
        {selectedAgent && (
          <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-4">
            <div className="flex items-center gap-3 pb-3 border-b border-gray-100 dark:border-hclsurface-darkborder">
              <div className="p-2.5 bg-brand-50 dark:bg-hclsurface-dark rounded-xl">
                {getAgentIcon(selectedAgent.agent_key)}
              </div>
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  {selectedAgent.agent_name}
                </h3>
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold">
                  Status: Ready &amp; Online
                </span>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-300 block mb-1">
                  Role &amp; Objective
                </span>
                <p className="text-gray-800 dark:text-gray-200 leading-relaxed bg-gray-50 dark:bg-hclsurface-dark p-3 rounded-xl border border-gray-200 dark:border-hclsurface-darkborder text-xs">
                  {selectedAgent.role_description}
                </p>
              </div>

              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-300 block mb-1">
                  Input Contract
                </span>
                <p className="text-gray-800 dark:text-gray-200 text-xs bg-gray-50 dark:bg-hclsurface-dark p-2.5 rounded-xl border border-gray-200 dark:border-hclsurface-darkborder font-serif">
                  {selectedAgent.input_type}
                </p>
              </div>

              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 dark:text-brand-300 block mb-1">
                  Output Contract
                </span>
                <p className="text-gray-800 dark:text-gray-200 text-xs bg-gray-50 dark:bg-hclsurface-dark p-2.5 rounded-xl border border-gray-200 dark:border-hclsurface-darkborder font-serif">
                  {selectedAgent.output_type}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Right: Live Telemetry Audit Feed */}
        <div className="lg:col-span-2 bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-hclsurface-darkborder">
              <h3 className="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">
                Live Agent Execution Telemetry Feed ({activities.length})
              </h3>
              <span className="text-xs text-gray-500 font-bold">Sequential Execution Logs</span>
            </div>

            <div className="space-y-2 mt-4 max-h-[380px] overflow-y-auto">
              {activities.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-8">
                  Upload a document or ask a question to view real-time sequential agent execution logs.
                </p>
              ) : (
                activities.map((act) => (
                  <div
                    key={act.id}
                    className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder text-xs space-y-1 font-serif"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-gray-900 dark:text-white text-sm">
                        {act.agent_name}
                      </span>
                      <span className="text-xs font-bold text-brand-600 dark:text-brand-300">
                        {act.execution_time_ms.toFixed(1)}ms
                      </span>
                    </div>

                    <p className="text-xs text-gray-700 dark:text-gray-300 font-medium leading-relaxed">
                      {act.action}: {act.output_summary}
                    </p>

                    <div className="text-[11px] text-gray-500">
                      Trace ID: {act.trace_id}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Agents;
