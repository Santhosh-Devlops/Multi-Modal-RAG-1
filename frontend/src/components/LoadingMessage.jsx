import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

const LoadingMessage = ({ text = "Orchestrating 8 Multi-Modal Agents..." }) => {
  return (
    <div className="flex items-center gap-3 p-4 bg-brand-50/70 dark:bg-brand-950/40 border border-brand-200 dark:border-brand-800 rounded-xl my-4 text-brand-800 dark:text-brand-200 text-xs animate-pulse">
      <div className="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
        <Bot className="w-4 h-4 animate-bounce" />
      </div>
      <div>
        <div className="flex items-center gap-1.5 font-bold text-sm text-brand-900 dark:text-brand-100 mb-0.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span>Multimodal Pipeline Active</span>
        </div>
        <p className="text-brand-700 dark:text-brand-300 font-medium">
          {text}
        </p>
      </div>
    </div>
  );
};

export default LoadingMessage;
