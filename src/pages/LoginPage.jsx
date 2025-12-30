import React, { useState, useEffect } from 'react';
import { usePortal } from '../context/PortalContext';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const { login, lang, setLang, t, isRTL, error, loading, user } = usePortal();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Normalize email to lowercase for case-insensitive login
    await login(email.toLowerCase(), password);
  };

  return (
    <div className={`min-h-screen flex items-center justify-center bg-primary ${isRTL ? 'dir-rtl' : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="bg-white p-8 border border-gray-200 w-full max-w-md">
        <div className="flex justify-end mb-6">
           <button onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} className="text-primary hover:text-accent font-bold text-sm transition-colors">
             {lang === 'en' ? 'العربية' : 'English'}
           </button>
        </div>

        <div className="flex justify-center mb-8">
           <img src="/header-logo.png" alt="IAU Logo" className="h-24 w-auto object-contain" />
        </div>

        <h2 className="text-2xl font-bold text-primary mb-6 text-center">{t.login}</h2>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t.username}</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 p-3 focus:border-accent focus:outline-none transition-colors"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t.password}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 p-3 focus:border-accent focus:outline-none transition-colors"
              required
            />
          </div>
          {error && <p className="text-red-600 text-sm text-center bg-red-50 border border-red-200 p-3">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-white py-3 font-bold hover:bg-accent-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? t.loading : t.login}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
          {t.footerBuiltBy || 'IAU Employee Portal'}
        </div>
      </div>
    </div>
  );
}
