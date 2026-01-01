import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, CheckCircle, Users, Settings, LogOut, Menu, X, Building2, Calendar } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import StatusPill from './StatusPill';

const HorizontalNav = ({ user, onLogout, isSticky }) => {
  const location = useLocation();
  const { lang, t, isRTL, attendance, toggleLanguage, dateSystem, toggleDateSystem, logout } = usePortal();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    onLogout();
  };

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
                    className={`flex items-center gap-2 px-6 ${isSticky ? 'py-2' : 'py-4'} transition-colors text-white ${
                      isActive
                        ? `bg-accent ${isSticky ? 'pb-[calc(0.5rem+10px)]' : 'pb-[calc(1rem+10px)]'}`
                        : 'hover:bg-accent'
                    } ${isRTL ? 'flex-row-reverse' : ''}`}
                  >
                    <Icon size={isSticky ? 18 : 20} />
                    <span className="font-medium text-sm">{item.label}</span>
                  </NavLink>
                  {index < navItems.length - 1 && (
                    <div className={`${isSticky ? 'h-6' : 'h-8'} w-px bg-white self-center`} style={{ opacity: 0.2 }}></div>
                  )}
                </React.Fragment>
              );
            })}

            {/* User Info with Status Pill */}
            <div className={`flex items-center gap-3 ml-auto px-6 ${isSticky ? 'py-2' : 'py-4'} text-white ${isRTL ? 'flex-row-reverse mr-auto ml-0' : ''}`}>
              {/* Status Pill - shown before name in English, after in Arabic */}
              {!isRTL && <StatusPill attendance={attendance} />}

              <div className={isRTL ? 'text-right' : 'text-left'}>
                <div className="text-sm font-medium">
                  {lang === 'ar' ? user.name_ar : user.name_en}
                </div>
                {!isSticky && (
                  <div className="text-xs opacity-75">
                    {lang === 'ar' ? user.position_ar : user.position_en}
                  </div>
                )}
              </div>

              {isRTL && <StatusPill attendance={attendance} />}

              {/* Controls (Language, Calendar, Logout) - shown when sticky */}
              {isSticky && (
                <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''} ${isRTL ? 'mr-4' : 'ml-4'}`}>
                  {/* Date System Toggle */}
                  <button
                    onClick={toggleDateSystem}
                    className="px-2 py-1 bg-white/10 hover:bg-white/20 text-white font-medium text-xs transition-colors flex items-center gap-1"
                    title={dateSystem === 'gregorian' ? t.switchToHijri : t.switchToGregorian}
                  >
                    <Calendar size={14} />
                    {dateSystem === 'gregorian' ? (lang === 'ar' ? 'هجري' : 'Hijri') : (lang === 'ar' ? 'ميلادي' : 'Gregorian')}
                  </button>

                  {/* Language Switcher */}
                  <button
                    onClick={toggleLanguage}
                    className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white font-medium text-xs transition-colors"
                  >
                    {lang === 'ar' ? 'English' : 'العربية'}
                  </button>

                  {/* Logout Button */}
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 bg-white/10 hover:bg-red-600 text-white font-medium text-xs transition-colors flex items-center gap-1"
                  >
                    <LogOut size={14} />
                    {t.logout}
                  </button>
                </div>
              )}
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
