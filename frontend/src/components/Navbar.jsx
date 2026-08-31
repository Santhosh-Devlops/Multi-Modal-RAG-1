import React from 'react';
import { Link } from 'react-router-dom';
import { Bot, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from './ThemeToggle';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-white dark:bg-hclsurface-darkcard border-b border-gray-200 dark:border-hclsurface-darkborder shadow-sm transition-colors">
      <div className="flex items-center gap-3">
        <Link to="/assistant" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-brand-500 flex items-center justify-center text-white shadow-md group-hover:bg-brand-600 transition-colors">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <span className="text-base font-bold text-gray-900 dark:text-white tracking-tight block leading-tight">
              HCLTech Multimodal RAG Assistant
            </span>
            <span className="text-xs font-semibold text-brand-500 dark:text-brand-300 block leading-none mt-0.5">
              Multi-Agent Document Intelligence
            </span>
          </div>
        </Link>

        <div className="hidden md:flex items-center gap-2 ml-6 pl-6 border-l border-gray-200 dark:border-hclsurface-darkborder">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
            <span className="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
            8 Sequential Agents Online
          </span>
          <span className="text-xs text-gray-600 dark:text-gray-400 font-semibold">
            Real-Time Ingestion &amp; Q&amp;A
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />

        {user && (
          <div className="flex items-center gap-3 pl-3 border-l border-gray-200 dark:border-hclsurface-darkborder">
            <div className="hidden sm:flex flex-col items-end">
              <span className="text-xs font-bold text-gray-900 dark:text-white">
                {user.full_name || 'Manufacturing Engineer'}
              </span>
              <span className="text-[11px] text-gray-500 dark:text-gray-400 capitalize">
                {user.role || 'Operator'}
              </span>
            </div>
            
            <div className="w-9 h-9 rounded-full bg-brand-500 text-white flex items-center justify-center text-xs font-bold shadow-sm">
              {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'H'}
            </div>

            <button
              onClick={logout}
              title="Logout session"
              className="p-1.5 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-hclsurface-dark rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
