import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, CheckCircle, Users, Settings, LogOut, Menu, X, Building2 } from 'lucide-react';
import { usePortal } from '../context/PortalContext';

const HorizontalNav = ({ user, onLogout }) => {
  const location = useLocation();
  const { lang, t, isRTL } = usePortal();
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

  return (
    <>
      <nav className="bg-primary">
        <div className="px-6">
          {/* Desktop Navigation (hidden on mobile) */}
          <div className="hidden md:flex items-stretch">
            {/* Navigation Links */}
            {navItems.map((item, index) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <React.Fragment key={item.path}>
                  <NavLink
                    to={item.path}
                    className={`flex items-center gap-2 px-6 py-4 transition-colors text-white ${
                      isActive
                        ? 'bg-accent pb-[calc(1rem+10px)]'
                        : 'hover:bg-accent'
                    } ${isRTL ? 'flex-row-reverse' : ''}`}
                  >
                    <Icon size={20} />
                    <span className="font-medium text-sm">{item.label}</span>
                  </NavLink>
                  {index < navItems.length - 1 && (
                    <div className="h-8 w-px bg-white self-center" style={{ opacity: 0.2 }}></div>
                  )}
                </React.Fragment>
              );
            })}

            {/* User Info */}
            <div className={`flex items-center gap-2 ml-auto px-6 py-4 text-white ${isRTL ? 'flex-row-reverse mr-auto ml-0' : ''}`}>
              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="text-sm font-medium">
                  {lang === 'ar' ? user.name_ar : user.name_en}
                </div>
                <div className="text-xs opacity-75">
                  {lang === 'ar' ? user.position_ar : user.position_en}
                </div>
              </div>
            </div>
          </div>

        {/* Mobile Navigation */}
        <div className="md:hidden">
          {/* Mobile Navigation Toggle */}
          <div className="flex items-center justify-between py-4">
            <span className="font-medium text-white">{t.menu || 'القائمة'}</span>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-white"
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
                    className={`flex items-center gap-3 px-4 py-3 transition-colors text-white ${
                      isActive ? 'bg-accent' : 'hover:bg-accent'
                    } ${isRTL ? 'flex-row-reverse' : ''}`}
                  >
                    <Icon size={20} />
                    <span className="font-medium text-sm">{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Separator line - brown/gold accent */}
      <div className="h-[10px] bg-accent"></div>
    </nav>
    </>
  );
};

export default HorizontalNav;
