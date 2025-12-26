import React from 'react';
import { Calendar, Globe, Menu } from 'lucide-react';
import { usePortal } from '../context/PortalContext';

export default function TopBar({ toggleSidebar }) {
  const { user, lang, setLang, t, dateSystem, toggleDateSystem, formatDate } = usePortal();

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shadow-sm z-10">
      <div className="flex items-center gap-4">
        <button onClick={toggleSidebar} className="md:hidden text-gray-500">
          <Menu size={24} />
        </button>
        <div className="hidden md:flex items-center text-sm text-gray-500 bg-gray-50 px-3 py-1 rounded-full border border-gray-200">
          <Calendar size={14} className="mr-2" />
          <span className="font-medium">
            {formatDate(new Date(), { weekday: 'long' })}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button 
          onClick={toggleDateSystem} 
          className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 px-3 py-1 rounded-md transition-colors"
        >
          <Calendar size={16} />
          {dateSystem === 'gregorian' ? (t.gregorian || 'Gregorian') : (t.hijri || 'Hijri')}
        </button>
        <button 
          onClick={() => setLang(lang === 'en' ? 'ar' : 'en')} 
          className="flex items-center gap-2 text-sm font-medium text-[#0f5132] hover:bg-[#f0fdf4] px-3 py-1 rounded-md transition-colors"
        >
          <Globe size={16} />
          {lang === 'en' ? 'العربية' : 'English'}
        </button>
        <div className="w-px h-6 bg-gray-200 mx-1"></div>
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-bold text-[#1e2c54]">{lang === 'ar' ? user.name_ar : user.name_en}</div>
            <div className="text-xs text-gray-500">{t[`role_${user.role?.toLowerCase()}`] || user.role}</div>
          </div>
          <div className="h-10 w-10 rounded-full bg-[#0f5132] text-white flex items-center justify-center font-bold text-lg shadow-md border-2 border-white">
            {(lang === 'ar' ? user.name_ar : user.name_en)?.charAt(0)}
          </div>
        </div>
      </div>
    </header>
  );
}