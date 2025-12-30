import { usePortal } from '../context/PortalContext';
import logoImage from '../assets/images/logos/ud_logo.png';
import bannerImage from '../assets/images/banners/eservices-banner2024.jpg';

const HeaderBanner = ({ user, onLogout }) => {
  const { lang, t, toggleLanguage, isRTL } = usePortal();

  return (
    <div className="bg-primary text-white">
      {/* Top Bar with Logo and University Name */}
      <div className="container mx-auto px-6 py-4 flex items-center justify-between">
        <div className={`flex items-center gap-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <img
            src={logoImage}
            alt="IAU Logo"
            className="h-16 w-auto"
          />
          <div className={isRTL ? 'text-right' : 'text-left'}>
            <h1 className="text-2xl font-bold font-arabic">
              {t.universityName || 'جامعة الإمام عبدالرحمن بن فيصل'}
            </h1>
            <p className="text-sm opacity-90">
              {t.portalSubtitle || 'بوابة الخدمات الإلكترونية'}
            </p>
          </div>
        </div>

        {/* Language & User Info */}
        <div className={`flex items-center gap-6 ${isRTL ? 'flex-row-reverse' : ''}`}>
          {/* Language Switcher */}
          <button
            onClick={toggleLanguage}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium text-sm transition-colors"
          >
            {lang === 'ar' ? 'English' : 'العربية'}
          </button>

          {/* User Info */}
          {user && (
            <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="text-sm font-medium">
                  {lang === 'ar' ? user.name_ar : user.name_en}
                </div>
                <div className="text-xs opacity-75">
                  {t[user.role] || user.role}
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
