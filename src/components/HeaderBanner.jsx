import { usePortal } from '../context/PortalContext';
import { Calendar, LogOut } from 'lucide-react';
import bannerImage from '../assets/images/banners/dashboard_header.jpg';

const HeaderBanner = ({ user, onLogout }) => {
  const { lang, t, toggleLanguage, isRTL, dateSystem, toggleDateSystem, logout } = usePortal();

  const handleLogout = async () => {
    await logout();
    onLogout();
  };

  return (
    <div className="bg-primary text-white">
      {/* Top Bar with Logo and University Name */}
      <div className="px-6 py-4 flex items-center justify-between">
        <div className={`flex items-center ${isRTL ? 'flex-row-reverse' : ''}`}>
          <img
            src="/logo.png"
            alt="IAU Logo"
            className="h-24 w-auto"
          />
        </div>

        {/* Language, Date System, Logout & User Info */}
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

          {/* User Info */}
          {user && (
            <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="text-sm font-medium">
                  {lang === 'ar' ? user.name_ar : user.name_en}
                </div>
                <div className="text-xs opacity-75">
                  {lang === 'ar' ? user.position_ar : user.position_en}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Banner Image Section */}
      <div className="relative h-32 overflow-hidden">
        <img
          src={bannerImage}
          alt="IAU Banner"
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  );
};

export default HeaderBanner;
