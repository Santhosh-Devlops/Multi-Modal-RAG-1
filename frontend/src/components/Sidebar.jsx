import React from 'react';
import { 
  Bot, 
  FileText, 
  Image as ImageIcon, 
  TrendingUp, 
  Table as TableIcon, 
  Hash, 
  FunctionSquare, 
  PlusCircle, 
  Info, 
  Sun, 
  Moon,
  File,
  LogOut
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Sidebar = ({
  activeDocument,
  onOpenUpload,
  onOpenDocInfo,
  onOpenExtractor,
  onChangeDocument
}) => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  const extractors = [
    { id: 'text', label: 'Text Extractor', icon: FileText },
    { id: 'images', label: 'Image Extractor', icon: ImageIcon },
    { id: 'graphs', label: 'Graphs & Visuals', icon: TrendingUp },
    { id: 'tables', label: 'Table Extractor', icon: TableIcon },
    { id: 'numericals', label: 'Numerical Extractor', icon: Hash },
    { id: 'equations', label: 'Equation Extractor', icon: FunctionSquare },
  ];

  return (
    <aside className="w-64 h-screen flex flex-col bg-[#0B0819] text-slate-300 border-r border-[#1F193B] flex-shrink-0 select-none">
      
      {/* Brand Header */}
      <div className="p-5 pb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-brand-500/20">
          <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          </svg>
        </div>
        <div>
          <h1 className="text-base font-extrabold text-white tracking-tight leading-tight">
            MultiDoc RAG
          </h1>
          <p className="text-[10px] font-semibold text-slate-400">
            Intelligent Document Assistant
          </p>
        </div>
      </div>

      {/* Main Navigation Area */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-6">
        
        {/* Assistant Pill (Active) */}
        <div>
          <button className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl bg-brand-600 text-white font-bold text-xs shadow-md shadow-brand-500/25 transition-all">
            <Bot className="w-4 h-4" />
            <span>Assistant</span>
          </button>
        </div>

        {/* EXTRACTORS SECTION */}
        <div className="space-y-1.5">
          <h3 className="px-3 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase">
            Extractors
          </h3>
          <div className="space-y-0.5">
            {extractors.map((ext) => {
              const Icon = ext.icon;
              return (
                <button
                  key={ext.id}
                  onClick={() => onOpenExtractor(ext.id)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-[#181335] transition-colors text-left"
                >
                  <Icon className="w-4 h-4 text-slate-400" />
                  <span>{ext.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* DOCUMENT SECTION */}
        <div className="space-y-1.5">
          <h3 className="px-3 text-[10px] font-extrabold tracking-wider text-slate-400 uppercase">
            Document
          </h3>
          <div className="space-y-0.5">
            <button
              onClick={onOpenUpload}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-[#181335] transition-colors text-left"
            >
              <PlusCircle className="w-4 h-4 text-slate-400" />
              <span>Upload New Document</span>
            </button>
            <button
              onClick={onOpenDocInfo}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-[#181335] transition-colors text-left"
            >
              <Info className="w-4 h-4 text-slate-400" />
              <span>Document Info</span>
            </button>
          </div>
        </div>

        {/* CURRENT DOCUMENT BOX */}
        <div className="p-3.5 rounded-2xl bg-[#120E27] border border-[#251E46] space-y-3">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Current Document
          </p>
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
              PDF
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-xs font-bold text-white truncate" title={activeDocument?.filename || 'CNC_Machine_Manual.pdf'}>
                {activeDocument?.filename || 'CNC_Machine_Manual.pdf'}
              </h4>
              <p className="text-[10px] text-slate-400 font-medium mt-0.5">
                {activeDocument?.page_count || 25} Pages • {(activeDocument?.file_size ? (activeDocument.file_size / (1024 * 1024)).toFixed(1) : '12.4')} MB
              </p>
              <p className="text-[9px] text-slate-400 mt-0.5">
                Uploaded: 2 hours ago
              </p>
            </div>
          </div>
          
          <button
            onClick={onChangeDocument || onOpenUpload}
            className="w-full py-1.5 px-3 rounded-lg bg-[#1D173E] hover:bg-[#282054] text-slate-200 text-xs font-bold transition-colors border border-[#2E2557]"
          >
            Change Document
          </button>
        </div>

      </div>

      {/* Footer / Theme Toggle */}
      <div className="p-4 border-t border-[#1F193B] flex items-center justify-between">
        <span className="text-xs font-bold text-slate-400">Theme</span>
        <div className="flex items-center gap-2">
          <Sun className={`w-3.5 h-3.5 ${!isDark ? 'text-amber-400' : 'text-slate-500'}`} />
          <button
            onClick={toggleTheme}
            className={`w-9 h-5 rounded-full p-0.5 transition-colors ${
              isDark ? 'bg-brand-600' : 'bg-slate-700'
            }`}
          >
            <div
              className={`w-4 h-4 rounded-full bg-white transition-transform ${
                isDark ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
          <Moon className={`w-3.5 h-3.5 ${isDark ? 'text-brand-400' : 'text-slate-500'}`} />
        </div>
      </div>

    </aside>
  );
};

export default Sidebar;
