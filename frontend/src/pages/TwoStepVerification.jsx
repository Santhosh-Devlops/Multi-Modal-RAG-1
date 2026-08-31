import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, KeyRound, ArrowRight, ArrowLeft } from 'lucide-react';
import { verifyTwoFactor } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';

const TwoStepVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { saveAuthSession } = useAuth();

  const email = location.state?.email || 'student@university.edu';
  const tempToken = location.state?.tempToken || '';
  const demoHintCode = location.state?.demoHintCode || '123456';

  const [code, setCode] = useState(demoHintCode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await verifyTwoFactor(email, tempToken, code.trim());
      if (res.status === 'success') {
        saveAuthSession(res.access_token, res.user);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code. Please enter 123456.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md">
            <ShieldCheck className="w-7 h-7" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          Two-Step Verification
        </h2>
        <p className="mt-1 text-center text-xs text-gray-600 dark:text-gray-400">
          Security step required to access multimodal intelligence pipeline
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-gray-800 py-8 px-6 shadow-sm border border-gray-200 dark:border-gray-700 sm:rounded-2xl sm:px-10">
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300">
              {error}
            </div>
          )}

          <div className="mb-5 p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs text-emerald-800 dark:text-emerald-300">
            <p className="font-semibold mb-1">Demo Code Activated:</p>
            <p>
              Enter the 6-digit security code: <strong className="font-mono text-sm tracking-wider text-emerald-900 dark:text-emerald-100">{demoHintCode}</strong>
            </p>
          </div>

          <form className="space-y-4" onSubmit={handleVerify}>
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                6-Digit Security Passcode
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <KeyRound className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 text-center font-mono tracking-widest text-lg font-bold border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500"
                  placeholder="123456"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none transition-colors disabled:opacity-50"
            >
              <span>{loading ? 'Verifying Code...' : 'Complete Verification'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Login</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoStepVerification;
