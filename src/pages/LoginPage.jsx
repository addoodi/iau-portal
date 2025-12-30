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
    <div className={`min-h-screen flex items-center justify-center bg-bg-page ${isRTL ? 'dir-rtl' : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="bg-white p-8 border border-gray-200 w-full max-w-md border-t-4 border-primary">
        <div className="flex justify-end mb-4">
           <button onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} className="text-primary font-bold text-sm">
             {lang === 'en' ? 'العربية' : 'English'}
           </button>
        </div>

        <div className="flex justify-center mb-8">
           <img src="/logo.png" alt="IAU Logo" className="w-full max-w-xs object-contain" />
        </div>

        <h2 className="text-2xl font-bold text-primary mb-2">{t.login}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.username}</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full border p-2 focus:ring-2 focus:ring-primary" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.password}</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full border p-2 focus:ring-2 focus:ring-primary" required />
          </div>
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <button type="submit" disabled={loading} className="w-full bg-primary text-white py-2 font-medium hover:bg-primary-hover disabled:bg-gray-400">
            {loading ? t.loading : t.login}
          </button>
        </form>
      </div>
    </div>
  );
}
