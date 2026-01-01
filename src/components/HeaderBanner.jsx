import { usePortal } from '../context/PortalContext';
import { Calendar, LogOut } from 'lucide-react';
import bannerImage from '../assets/images/banners/dashboard_header.jpg';

const HeaderBanner = ({ user, onLogout, isSticky }) => {
  const { lang, t, toggleLanguage, isRTL, dateSystem, toggleDateSystem, logout } = usePortal();

  const handleLogout = async () => {
    await logout();
    onLogout();
  };

  return (
    <div>
      {/* Top Bar - Navy with controls (only shown when NOT sticky) */}
      {!isSticky && (
        <div className="bg-primary px-6 py-3 flex items-center justify-end">
          <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
            {/* Date System Toggle */}
            <button
              onClick={toggleDateSystem}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-xs transition-colors flex items-center gap-2"
              title={dateSystem === 'gregorian' ? t.switchToHijri : t.switchToGregorian}
            >
              <Calendar size={16} />
              {dateSystem === 'gregorian' ? (lang === 'ar' ? 'هجري' : 'Hijri') : (lang === 'ar' ? 'ميلادي' : 'Gregorian')}
            </button>

            {/* Language Switcher */}
            <button
              onClick={toggleLanguage}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-sm transition-colors"
            >
              {lang === 'ar' ? 'English' : 'العربية'}
            </button>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-white/10 hover:bg-red-600 text-white font-medium text-sm transition-colors flex items-center gap-2"
            >
              <LogOut size={16} />
              {t.logout}
            </button>
          </div>
        </div>
      )}

      {/* Logo Bar - Light brown/beige background (only shown when NOT sticky) */}
      {!isSticky && (
        <div className="bg-bg-page px-6 py-4">
          <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
            <img
              src="/header-logo.png"
              alt="IAU Logo"
              className="h-24 w-auto"
            />
          </div>
        </div>
      )}

      {/* Banner Image Section (only shown when NOT sticky) */}
      {!isSticky && (
        <div className="relative h-32 overflow-hidden">
          <img
            src={bannerImage}
            alt="IAU Banner"
            className="w-full h-full object-cover"
          />
        </div>
      )}
    </div>
  );
};

export default HeaderBanner;
