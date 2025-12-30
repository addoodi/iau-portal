import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, CheckCircle, Users, Settings, LogOut, Menu, X, Building2 } from 'lucide-react';
import { usePortal } from '../context/PortalContext';

const HorizontalNav = ({ user, onLogout }) => {
  const location = useLocation();
  const { lang, t, isRTL, logout } = usePortal();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: t.dashboard },
    { path: '/my-requests', icon: FileText, label: t.myRequests },
    ...(user.role?.toLowerCase() !== 'employee'
      ? [{ path: '/approvals', icon: CheckCircle, label: t.approvals }]
      : []
    ),
    ...(user.role?.toLowerCase() === 'admin'
      ? [{ path: '/users', icon: Users, label: t.employees }]
      : []
    ),
    ...(user.role?.toLowerCase() === 'admin'
      ? [{ path: '/units', icon: Building2, label: t.unitManagement }]
      : []
    ),
    ...(user.role?.toLowerCase() === 'admin'
      ? [{ path: '/site-settings', icon: Settings, label: t.settings }]
      : []
    ),
  ];

  const handleLogout = async () => {
    await logout();
    onLogout();
  };

  return (
    <nav className="bg-accent border-b border-gray-300">
      <div className="px-6">
        {/* Desktop Navigation (hidden on mobile) */}
        <div className="hidden md:flex items-center gap-1">
          {/* Navigation Links */}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-6 py-4 transition-colors border-b-2 ${
                  isActive
                    ? 'bg-primary text-white border-primary'
                    : 'text-gray-700 border-transparent hover:bg-primary hover:text-white'
                } ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <Icon size={20} />
                <span className="font-medium text-sm">{item.label}</span>
              </NavLink>
            );
          })}

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className={`flex items-center gap-2 px-6 py-4 text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors ml-auto ${
              isRTL ? 'flex-row-reverse mr-auto ml-0' : ''
            }`}
          >
            <LogOut size={20} />
            <span className="font-medium text-sm">{t.logout}</span>
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden">
          {/* Mobile Navigation Toggle */}
          <div className="flex items-center justify-between py-4">
            <span className="font-medium text-gray-700">{t.menu || 'القائمة'}</span>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Dropdown Menu */}
          {mobileMenuOpen && (
            <div className="pb-4">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:bg-primary hover:text-white'
                    } ${isRTL ? 'flex-row-reverse' : ''}`}
                  >
                    <Icon size={20} />
                    <span className="font-medium text-sm">{item.label}</span>
                  </NavLink>
                );
              })}

              {/* Mobile Logout */}
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 transition-colors ${
                  isRTL ? 'flex-row-reverse' : ''
                }`}
              >
                <LogOut size={20} />
                <span className="font-medium text-sm">{t.logout}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default HorizontalNav;
