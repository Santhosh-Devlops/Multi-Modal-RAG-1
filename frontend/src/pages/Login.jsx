import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Mail, Lock, User, ArrowRight, ShieldCheck } from 'lucide-react';
import { login, register } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';

const Login = () => {
  const navigate = useNavigate();
  const { saveAuthSession } = useAuth();
  
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      if (isRegister) {
        const res = await register(email.trim(), password, fullName.trim() || 'Document Operator');
        if (res.status === 'success') {
          saveAuthSession(res.access_token, res.user);
          navigate('/');
        }
      } else {
        const res = await login(email.trim(), password);
        if (res.status === 'success') {
          saveAuthSession(res.access_token, res.user);
          navigate('/');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || (isRegister ? 'Registration failed.' : 'Invalid email or password.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] dark:bg-[#0D0A1C] flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors font-sans">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-14 h-14 rounded-2xl bg-brand-500 flex items-center justify-center text-white shadow-xl shadow-brand-500/20">
            <Bot className="w-8 h-8" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          DocuMind AI
        </h2>
        <p className="mt-1 text-center text-xs text-brand-600 dark:text-brand-400 font-bold uppercase tracking-wider">
          Private Multimodal Document Intelligence Assistant
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-[#16122E] py-8 px-6 shadow-xl border border-slate-200 dark:border-[#282252] sm:rounded-2xl sm:px-10">
          
          {/* Tab Switcher: Sign In vs Create Account */}
          <div className="flex rounded-xl bg-slate-100 dark:bg-[#0D0A1C] p-1 mb-6 border border-slate-200 dark:border-[#282252]">
            <button
              type="button"
              onClick={() => { setIsRegister(false); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                !isRegister
                  ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setIsRegister(true); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                isRegister
                  ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs font-bold text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          {successMsg && (
            <div className="mb-4 p-3.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl text-xs font-bold text-emerald-700 dark:text-emerald-300">
              {successMsg}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {isRegister && (
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  Full Name
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="block w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-[#282252] rounded-xl bg-white dark:bg-[#0D0A1C] text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 font-sans"
                    placeholder="e.g. Alex Smith"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Email Address
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-[#282252] rounded-xl bg-white dark:bg-[#0D0A1C] text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 font-sans"
                  placeholder="name@org.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                Password
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-[#282252] rounded-xl bg-white dark:bg-[#0D0A1C] text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 font-sans"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-xl shadow-lg shadow-brand-500/20 text-sm font-bold text-white bg-brand-500 hover:bg-brand-600 active:scale-[0.99] focus:outline-none transition-all disabled:opacity-50 mt-2 font-sans"
            >
              <span>{loading ? 'Authenticating...' : isRegister ? 'Create Account & Open Assistant' : 'Sign In to Workspace'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-200 dark:border-[#282252] flex items-center justify-center gap-2 text-xs font-bold text-emerald-600 dark:text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <span>Private User-Scoped Knowledge Base</span>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;
