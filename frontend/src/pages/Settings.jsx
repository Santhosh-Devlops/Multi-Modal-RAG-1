import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Moon,
  Sun,
  Sliders,
  Shield,
  Key,
  User,
  CheckCircle2,
  Save
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  const [defaultDomain, setDefaultDomain] = useState('Manufacturing');
  const [topK, setTopK] = useState(5);
  const [semanticWeight, setSemanticWeight] = useState(0.7);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="pb-6 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <SettingsIcon className="w-5 h-5 text-brand-600 dark:text-brand-400" />
          <span>System & Workspace Settings</span>
        </h1>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Configure application theme, default domain preferences, hybrid retrieval weights, and model parameters.
        </p>
      </div>

      {saved && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-center gap-2 text-xs text-emerald-800 dark:text-emerald-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Preferences updated successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Appearance Settings */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4">
          <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
            Appearance & Interface Theme
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 block">
                Light / Dark Theme Mode
              </span>
              <span className="text-[11px] text-gray-500 dark:text-gray-400">
                Current active theme: <strong className="capitalize">{theme} Mode</strong>
              </span>
            </div>

            <button
              type="button"
              onClick={toggleTheme}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-xs font-semibold text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-all"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
              <span>Switch to {theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
            </button>
          </div>
        </div>

        {/* Retrieval & RAG Weights */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4">
          <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
            Hybrid Retrieval Tuning
          </h2>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between font-semibold mb-1 text-gray-800 dark:text-gray-200">
                <span>Default Evidence Retrieval Depth (Top-K Chunks):</span>
                <span className="text-brand-600 dark:text-brand-400">{topK} Chunks</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-semibold mb-1 text-gray-800 dark:text-gray-200">
                <span>Dense Semantic Embedding Weight:</span>
                <span className="text-brand-600 dark:text-brand-400">{(semanticWeight * 100).toFixed(0)}% (Keyword: {((1 - semanticWeight) * 100).toFixed(0)}%)</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.1"
                value={semanticWeight}
                onChange={(e) => setSemanticWeight(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-800 dark:text-gray-200 mb-1">
                Default Domain on Startup:
              </label>
              <select
                value={defaultDomain}
                onChange={(e) => setDefaultDomain(e.target.value)}
                className="w-full sm:w-64 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white"
              >
                <option value="Manufacturing">Manufacturing</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Finance">Finance</option>
                <option value="Education">Education</option>
                <option value="Defence">Defence</option>
              </select>
            </div>
          </div>
        </div>

        {/* Model Service Information */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3 text-xs">
          <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
            AI Model Integration Status
          </h2>
          <div className="space-y-2 text-gray-600 dark:text-gray-400">
            <p><strong>Text Generation:</strong> <code className="font-mono text-[11px] bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">mistralai/Mistral-7B-Instruct-v0.2</code></p>
            <p><strong>Embedding Vectorizer:</strong> <code className="font-mono text-[11px] bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">sentence-transformers/all-MiniLM-L6-v2</code></p>
            <p><strong>Vision Captioning:</strong> <code className="font-mono text-[11px] bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">Salesforce/blip-image-captioning-large</code></p>
            <p><strong>Fallback Mode:</strong> Deterministic Grounded Evidence Synthesis Engine (Active)</p>
          </div>
        </div>

        {/* User Account Info */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3 text-xs">
          <h2 className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
            User Account Details
          </h2>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300 flex items-center justify-center font-bold text-sm">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <span className="font-bold text-gray-900 dark:text-white block">{user?.full_name || 'Student Intern'}</span>
              <span className="text-gray-500 dark:text-gray-400 text-[11px]">{user?.email || 'student@university.edu'}</span>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition-colors"
        >
          <Save className="w-4 h-4" />
          <span>Save System Settings</span>
        </button>
      </form>
    </div>
  );
};

export default Settings;
