import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { PortalProvider, usePortal } from './context/PortalContext';
import { getSetupStatus } from './api';

// Pages & Components
import LoginPage from './pages/LoginPage';
import SetupPage from './pages/SetupPage';
import Dashboard from './pages/Dashboard';
import MyRequests from './pages/MyRequests';
import Approvals from './pages/Approvals';
import UserManagement from './pages/UserManagement';
import UnitManagement from './pages/UnitManagement';
import Profile from './pages/Profile';
import RequestModal from './components/RequestModal';
import HeaderBanner from './components/HeaderBanner'; // Import HeaderBanner
import HorizontalNav from './components/HorizontalNav'; // Import HorizontalNav
import SiteSettings from './pages/SiteSettings'; // Import SiteSettings
import EmployeeDetailView from './pages/EmployeeDetailView';

// --- Setup & Auth Flow ---

function SetupCheck({ children }) {
  const [isSetup, setIsSetup] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await getSetupStatus();
        setIsSetup(status.is_setup);
      } catch (err) {
        setError('Could not connect to the server. Please ensure the backend is running.');
      }
    };
    checkStatus();
  }, []);

  if (error) {
    return <div className="h-screen w-screen flex items-center justify-center bg-red-100 text-red-700">{error}</div>;
  }

  if (isSetup === null) {
    return <div className="h-screen w-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isSetup) {
    return <Navigate to="/setup" replace />;
  }

  return children;
}

function ProtectedRoute({ children }) {
    const { user, loading } = usePortal();
    const location = useLocation();

    if (loading) {
        return <div className="h-screen w-screen flex items-center justify-center">Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
}


// --- Main Application Layout ---

function MainLayout() {
  const { t, isRTL, user, setUser } = usePortal();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className={`min-h-screen flex flex-col font-sans ${isRTL ? 'dir-rtl' : ''}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Container wrapper for header and content */}
      <div className="max-w-7xl mx-auto w-full shadow-2xl">
        {/* University Header with Logo & Banner */}
        <HeaderBanner user={user} onLogout={handleLogout} />

        {/* Horizontal Navigation Bar */}
        <HorizontalNav user={user} onLogout={handleLogout} />

        {/* Main Content Area */}
        <main className="flex-1 px-6 py-8 bg-bg-page min-h-screen">
          <div className="space-y-6">
            <Outlet /> {/* Child routes will render here */}
          </div>
        </main>

        {/* Footer */}
        <footer className="pt-6 pb-4 border-t border-gray-200 bg-white">
          <div className="px-6 text-center text-sm text-gray-600">
            {t.footerBuiltBy}
          </div>
        </footer>
      </div>

      {/* Floating New Request Button */}
      <button
        onClick={() => setIsModalOpen(true)}
        className={`fixed bottom-8 ${isRTL ? 'left-8' : 'right-8'} bg-accent hover:bg-accent-hover text-white p-4 shadow-lg z-50 flex items-center gap-2`}
      >
        <Plus size={24} />
        <span className="font-bold hidden md:inline">{t.newRequest}</span>
      </button>

      {isModalOpen && <RequestModal onClose={() => setIsModalOpen(false)} />}
    </div>
  );
}

// --- App Router ---

export default function App() {
  return (
    <PortalProvider>
        <BrowserRouter>
            <Routes>
                <Route path="/setup" element={<SetupPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route
                    path="/*"
                    element={
                        <SetupCheck>
                            <ProtectedRoute>
                                <Routes>
                                    <Route path="/" element={<MainLayout />}>
                                        <Route index element={<Navigate to="/dashboard" replace />} />
                                        <Route path="dashboard" element={<Dashboard />} />
                                        <Route path="my-requests" element={<MyRequests />} />
                                        <Route path="approvals" element={<Approvals />} />
                                        <Route path="users" element={<UserManagement />} />
                                        <Route path="units" element={<UnitManagement />} />
                                        <Route path="profile" element={<Profile />} />
                                        <Route path="site-settings" element={<SiteSettings />} />
                                        <Route path="employee/:employeeId" element={<EmployeeDetailView />} />
                                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                                    </Route>
                                </Routes>
                            </ProtectedRoute>
                        </SetupCheck>
                    }
                />
            </Routes>
        </BrowserRouter>
    </PortalProvider>
  );
}
