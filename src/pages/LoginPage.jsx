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
    <div className={`min-h-screen flex ${isRTL ? 'dir-rtl' : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Left side - Navy background (branding area) - hidden on mobile */}
      <div className="hidden md:flex flex-1 bg-primary md:mr-[500px]">
        {/* Empty navy background - can add branding image here later */}
      </div>

      {/* Right side - White login panel - full width on mobile, fixed 500px on desktop */}
      <div className="w-full md:fixed md:right-0 md:top-0 md:bottom-0 md:w-[500px] bg-white overflow-auto">
        <div className="p-6 sm:p-8 md:p-12 flex flex-col min-h-full">
          {/* Language Toggle */}
          <div className="flex justify-end mb-6 sm:mb-8">
            <button onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} className="text-primary hover:text-accent font-bold text-sm transition-colors">
              {lang === 'en' ? 'العربية' : 'English'}
            </button>
          </div>

          {/* Logo - responsive sizing */}
          <div className="flex justify-center mb-8 sm:mb-12">
            <img src="/header-logo.png" alt="IAU Logo" className="h-16 sm:h-20 md:h-28 w-auto max-w-full object-contain" />
          </div>

          {/* Login Form */}
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-primary mb-8">{t.login}</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{t.username}</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full border border-gray-300 p-3 focus:border-accent focus:outline-none transition-colors"
                  placeholder="someone@example.com"
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
                  placeholder="Password"
                  required
                />
              </div>
              {error && <p className="text-red-600 text-sm bg-red-50 border border-red-200 p-3">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-accent text-white py-3 font-bold hover:bg-accent-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? t.loading : t.login}
              </button>
            </form>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-600">
            {t.footerBuiltBy || 'IAU Employee Portal'}
          </div>
        </div>
      </div>
    </div>
  );
}
