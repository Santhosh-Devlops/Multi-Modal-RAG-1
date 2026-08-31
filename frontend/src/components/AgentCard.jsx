import React from 'react';
import { Bot, CheckCircle2, Clock, Zap } from 'lucide-react';

const AgentCard = ({ agent }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm flex flex-col justify-between hover:border-brand-300 dark:hover:border-brand-700 transition-all">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold">
            <Bot className="w-4 h-4" />
          </div>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            {agent.status || 'Online'}
          </span>
        </div>

        <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-1.5">
          {agent.agent_name}
        </h3>
        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
          {agent.role_description}
        </p>

        <div className="space-y-2 text-xs mb-4">
          <div className="p-2 bg-gray-50 dark:bg-gray-900/60 rounded border border-gray-100 dark:border-gray-800">
            <span className="text-[10px] font-semibold uppercase text-gray-400 dark:text-gray-500 block">Input Contract</span>
            <span className="text-gray-700 dark:text-gray-300 font-medium">{agent.input_type}</span>
          </div>
          <div className="p-2 bg-gray-50 dark:bg-gray-900/60 rounded border border-gray-100 dark:border-gray-800">
            <span className="text-[10px] font-semibold uppercase text-gray-400 dark:text-gray-500 block">Output Contract</span>
            <span className="text-gray-700 dark:text-gray-300 font-medium">{agent.output_type}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400 font-medium">
        <span className="flex items-center gap-1">
          <Zap className="w-3.5 h-3.5 text-amber-500" />
          <span>{agent.total_tasks_executed || 0} tasks executed</span>
        </span>
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          <span>{agent.average_latency_ms ? `${agent.average_latency_ms.toFixed(1)}ms` : '< 5ms'}</span>
        </span>
      </div>
    </div>
  );
};

export default AgentCard;
