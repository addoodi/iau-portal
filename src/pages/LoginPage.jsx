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
    <div className={`min-h-screen flex items-center justify-center bg-[#f8f9fa] ${isRTL ? 'dir-rtl' : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md border-t-4 border-[#0f5132]">
        <div className="flex justify-between items-center mb-8">
           <img src="/logo.png" alt="IAU Logo" className="h-16 object-contain" />
           <button onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} className="text-[#0f5132] font-bold text-sm">
             {lang === 'en' ? 'العربية' : 'English'}
           </button>
        </div>
        
        <h2 className="text-2xl font-bold text-[#1e2c54] mb-2">{t.login}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.username}</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full border rounded-md p-2 focus:ring-2 focus:ring-[#0f5132]" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.password}</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full border rounded-md p-2 focus:ring-2 focus:ring-[#0f5132]" required />
          </div>
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <button type="submit" disabled={loading} className="w-full bg-[#0f5132] text-white py-2 rounded-md font-medium hover:bg-[#0b3b25] disabled:bg-gray-400">
            {loading ? t.loading : t.login}
          </button>
        </form>
      </div>
    </div>
  );
}
