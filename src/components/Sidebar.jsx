import React, { useEffect } from 'react';
import { LogOut, User, Home, Send, UserCheck, Users, Building, Settings } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar({ isOpen, toggleSidebar }) {
  const { user, logout, t, lang } = usePortal();
  const location = useLocation();

  // Auto-close on mobile when route changes
  useEffect(() => {
    const isMobile = window.innerWidth < 768;
    if (isMobile && isOpen) {
      toggleSidebar(); // Close sidebar
    }
  }, [location.pathname]); // Run when route changes

  const menuItems = [
    { id: 'dashboard', path: '/dashboard', icon: Home, label: t.dashboard, roles: ['admin', 'manager', 'employee'] },
    { id: 'my-requests', path: '/my-requests', icon: Send, label: t.myRequests, roles: ['admin', 'manager', 'employee'] },
    { id: 'approvals', path: '/approvals', icon: UserCheck, label: t.approvals, roles: ['admin', 'manager'] },
    { id: 'users', path: '/users', icon: Users, label: t.userManagement, roles: ['admin'] },
    { id: 'units', path: '/units', icon: Building, label: t.unitManagement, roles: ['admin'] },
    { id: 'site-settings', path: '/site-settings', icon: Settings, label: t.siteSettings, roles: ['admin'] },
  ];

  const filteredItems = menuItems.filter(item => item.roles.includes(user.role.toLowerCase()));

  const getLinkClass = (path) => (
    `w-full flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
    location.pathname.startsWith(path)
        ? 'bg-[#f0fdf4] text-[#0f5132] border-r-4 border-[#0f5132]'
        : 'text-gray-600 hover:bg-gray-50 hover:text-[#0f5132]'
    }`
  );

  return (
    <aside className={`w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm z-20 ${isOpen ? 'flex' : 'hidden'} md:flex`}>
      <div className="p-6 border-b border-gray-100 flex items-center justify-center">
        <img src="/logo.png" alt="IAU Logo" className="h-20 object-contain" />
      </div>

      <div className="p-4">
        <div className="text-xs font-semibold text-gray-400 uppercase mb-2 tracking-wider">{t.welcome}</div>
        <div className="text-[#1e2c54] font-semibold text-base">{(lang === 'ar' ? user.name_ar : user.name_en)?.split(' ')[0]}</div>
        <div className="text-xs text-gray-500">{t[`role_${user.role?.toLowerCase()}`] || user.role}</div>
      </div>

      <nav className="flex-1 px-2 space-y-1">
        {filteredItems.map(item => (
          <Link
            key={item.id}
            to={item.path}
            className={getLinkClass(item.path)}
          >
            <item.icon size={18} className={`mx-3 ${location.pathname.startsWith(item.path) ? 'text-[#0f5132]' : 'text-gray-400'}`} />
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <Link
          to="/profile"
          className={`flex items-center w-full px-4 py-2 text-sm text-gray-600 hover:text-[#0f5132] mb-2 ${location.pathname === '/profile' ? 'text-[#0f5132] font-bold' : ''}`}
        >
          <User size={18} className="mx-3" />
          {t.profile}
        </Link>
        <button
          onClick={logout}
          className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
        >
          <LogOut size={18} className="mx-3" />
          {t.signOut}
        </button>
      </div>
    </aside>
  );
}