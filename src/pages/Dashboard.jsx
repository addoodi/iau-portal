import React from 'react';
import { FileDown, CheckCircle, LogIn, LogOut, AlertTriangle, AlertCircle, Clock } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { downloadDashboardReport } from '../api';
import { useNavigate } from 'react-router-dom';
import DashboardTimeline from '../components/DashboardTimeline';

export default function Dashboard() {
  const { user, employees, requests, t, lang, attendance, loading, formatDate } = usePortal();
  const navigate = useNavigate();

  // Calculate balances
  const availableBalance = user.vacation_balance || 0;
  const usedBalance = requests
    .filter(r => r.employee_id === user.id && r.status === 'Approved')
    .reduce((acc, curr) => acc + curr.duration, 0);
  const totalEarned = availableBalance + usedBalance;
  
  // Contract Warning
  const showContractWarning = user.days_remaining_in_contract !== undefined && user.days_remaining_in_contract <= 40;

  // Filter team members (Admin sees all except themselves, Manager sees their direct reports)
  const teamMembers = employees.filter(u => {
      if (user.role?.toLowerCase() === 'admin') return u.id !== user.id;
      if (user.role?.toLowerCase() === 'manager') return u.manager_id === user.id;
      return false;
  });

  // Count pending requests for managers/admins
  const pendingRequests = requests.filter(r => {
    if (user.role?.toLowerCase() === 'admin') return r.status === 'Pending';
    if (user.role?.toLowerCase() === 'manager') {
      const employee = employees.find(e => e.id === r.employee_id);
      return r.status === 'Pending' && employee?.manager_id === user.id;
    }
    return false;
  });
  const pendingCount = pendingRequests.length;

  const formatTime = (isoString) => {
    if (!isoString) return '--:--';
    return new Date(isoString).toLocaleTimeString(lang === 'ar' ? 'ar-SA' : 'en-US', { hour: '2-digit', minute: '2-digit' });
  };

  // Determine attendance status
  const isOnLeave = attendance?.status === "On Leave";
  const statusBgColor = isOnLeave ? "bg-orange-100" : "bg-green-100";
  const statusTextColor = isOnLeave ? "text-orange-800" : "text-green-800";
  const statusText = isOnLeave
    ? `${t.onLeave || "On Leave"} (${t[attendance.vacation_type] || attendance.vacation_type})`
    : t.present || "Present";
  
  const handleDownloadReport = async () => {
      try {
          await downloadDashboardReport();
      } catch (error) {
          console.error("Failed to download report", error);
          alert("Failed to download report");
      }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-[#1e2c54]">{t.dashboard}</h1>
        <div className="flex gap-2">
            <button 
                onClick={handleDownloadReport}
                className="p-2 text-[#0f5132] bg-white border border-gray-200 rounded hover:bg-gray-50 transition-colors"
                title="Download Dashboard Report"
            >
                <FileDown size={18}/>
            </button>
        </div>
      </div>

      {showContractWarning && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-start gap-3 shadow-sm">
            <AlertTriangle className="text-orange-600 shrink-0 mt-1" size={24} />
            <div>
                <h3 className="font-bold text-orange-800 text-lg">{t.contractExpiring || "Contract Expiring Soon"}</h3>
                <p className="text-sm text-orange-700 mt-1">
                    {t.contractWarningMessage || `Your contract ends in ${user.days_remaining_in_contract} days. Please note that you have ${availableBalance} vacation days remaining, which will be lost if not used before the contract renewal.`}
                </p>
            </div>
        </div>
      )}

      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') && pendingCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-start gap-3 shadow-sm cursor-pointer hover:bg-yellow-100 transition-colors" onClick={() => navigate('/approvals')}>
            <Clock className="text-yellow-600 shrink-0 mt-1" size={24} />
            <div className="flex-1">
                <h3 className="font-bold text-yellow-800 text-lg">{t.pendingApprovals || "Pending Approvals"}</h3>
                <p className="text-sm text-yellow-700 mt-1">
                    {t.pendingApprovalsMessage?.replace('{count}', pendingCount) || `You have ${pendingCount} pending leave request${pendingCount > 1 ? 's' : ''} awaiting your approval.`}
                </p>
            </div>
            <button className="shrink-0 px-4 py-2 bg-yellow-600 text-white text-sm font-semibold rounded-lg hover:bg-yellow-700 transition-colors">
                {t.reviewNow || "Review Now"}
            </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Status Widget - Colored Background */}
        <div className={`${statusBgColor} p-3 rounded-xl shadow-sm border ${isOnLeave ? 'border-orange-200' : 'border-green-200'}`}>
          <h3 className={`text-xs font-semibold uppercase tracking-wider mb-2 ${statusTextColor}`}>
            {t.status || "Status"}
          </h3>
          <div className={`text-center text-lg font-bold ${statusTextColor}`}>
            {statusText}
          </div>
        </div>

        {/* Vacation Balance Widget - With Contract End */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 lg:col-span-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3 tracking-wider">{t.vacationBalance}</h3>
          <div className="grid grid-cols-3 gap-3 mb-3">
            <div className="p-3 bg-green-50 rounded-lg text-center">
              <div className="text-2xl font-bold text-[#0f5132]">{totalEarned}</div>
              <div className="text-xs text-gray-500 font-medium">{t.earned}</div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-600">{usedBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.used}</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{availableBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.available}</div>
            </div>
          </div>
          {user.days_remaining_in_contract !== undefined && (
            <div className="bg-gray-50 p-2 rounded-lg flex items-center justify-between text-sm">
              <span className="text-gray-600">{t.contractEndsIn || "Contract ends in"}</span>
              <span className="font-semibold text-gray-800">{user.days_remaining_in_contract} {t.days || "days"}</span>
            </div>
          )}
        </div>
      </div>

      {/* Timeline Calendar for Managers/Admins */}
      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') && teamMembers.length > 0 && (
        <DashboardTimeline teamMembers={teamMembers} requests={requests} />
      )}
    </div>
  );
}