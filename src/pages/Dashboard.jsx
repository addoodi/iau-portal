import React, { useState, useEffect } from 'react';
import { FileDown, CheckCircle, LogIn, LogOut, AlertTriangle, AlertCircle, Clock, ChevronDown, CalendarClock, CheckSquare } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { downloadDashboardReport, getExpiringContracts, getContractsNeedingVerification } from '../api';
import { useNavigate } from 'react-router-dom';
import DashboardTimeline from '../components/DashboardTimeline';
import { getAllSubordinates } from '../utils/hierarchy';

export default function Dashboard() {
  const { user, employees, requests, t, lang, attendance, loading, formatDate, dateSystem } = usePortal();
  const navigate = useNavigate();

  // Report filter state
  const [reportFilter, setReportFilter] = useState('ytd');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);

  // Contract management state
  const [expiringContracts, setExpiringContracts] = useState([]);
  const [contractsNeedingVerification, setContractsNeedingVerification] = useState([]);

  // Fetch contract notifications for managers/admins
  useEffect(() => {
    const fetchContractNotifications = async () => {
      if (user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') {
        try {
          const [expiring, needingVerification] = await Promise.all([
            getExpiringContracts(105),
            getContractsNeedingVerification()
          ]);
          setExpiringContracts(expiring.expiring_contracts || []);
          setContractsNeedingVerification(needingVerification.needing_verification || []);
        } catch (error) {
          console.error('Failed to fetch contract notifications:', error);
        }
      }
    };

    fetchContractNotifications();
  }, [user.role]);

  // Calculate balances
  const availableBalance = user.vacation_balance || 0;
  const usedBalance = requests
    .filter(r => r.employee_id === user.id && r.status === 'Approved')
    .reduce((acc, curr) => acc + curr.duration, 0);
  const totalEarned = availableBalance + usedBalance;
  
  // Contract Warning
  const showContractWarning = user.days_remaining_in_contract !== undefined && user.days_remaining_in_contract <= 40;

  // Filter team members (Admin sees all except themselves, Manager sees direct and indirect reports)
  const teamMembers = employees.filter(u => {
      if (user.role?.toLowerCase() === 'admin') return u.id !== user.id;
      if (user.role?.toLowerCase() === 'manager') {
          // Get all subordinates (direct and indirect) using hierarchy utility
          const subordinateIds = getAllSubordinates(user.id, employees, true);
          return subordinateIds.includes(u.id);
      }
      return false;
  });

  // Count pending requests for managers/admins
  const pendingRequests = requests.filter(r => {
    if (user.role?.toLowerCase() === 'admin') return r.status === 'Pending';
    if (user.role?.toLowerCase() === 'manager') {
      const employee = employees.find(e => e.id === r.employee_id);
      if (!employee) return false;
      // Check if employee is a subordinate (direct or indirect)
      const subordinateIds = getAllSubordinates(user.id, employees, true);
      return r.status === 'Pending' && subordinateIds.includes(employee.id);
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
  
  const getFilterLabel = () => {
    const labels = {
      'ytd': t.ytd || 'Year to Date',
      'last_30': t.last30Days || 'Last 30 Days',
      'last_60': t.last60Days || 'Last 60 Days',
      'last_90': t.last90Days || 'Last 90 Days',
      'full_year': t.fullYear || 'Full Contract Year',
      'custom': t.custom || 'Custom Range'
    };
    return labels[reportFilter] || labels['ytd'];
  };

  const handleDownloadReport = async () => {
    try {
      const filterData = {
        filter_type: reportFilter,
        language: lang,
        date_system: lang === 'ar' ? 'hijri' : 'gregorian', // Auto-use Hijri for Arabic
        ...(reportFilter === 'custom' && {
          start_date: customStartDate,
          end_date: customEndDate
        })
      };
      await downloadDashboardReport(filterData);
      setShowFilterDropdown(false);
    } catch (error) {
      console.error("Failed to download report", error);
      alert(t.reportDownloadFailed || "Failed to download report");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-primary">{t.dashboard}</h1>
        <div className="flex gap-2 items-center relative">
          {/* Report Filter Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 hover:bg-gray-50 transition-colors text-sm"
            >
              <span className="text-gray-700">{t.reportPeriod || "Period"}:</span>
              <span className="font-medium text-primary">{getFilterLabel()}</span>
              <ChevronDown size={16} className="text-gray-500" />
            </button>

            {showFilterDropdown && (
              <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 z-50">
                <div className="p-3 space-y-2">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">{t.selectPeriod || "Select Period"}</p>

                  {[
                    { value: 'ytd', label: t.ytd || 'Year to Date' },
                    { value: 'last_30', label: t.last30Days || 'Last 30 Days' },
                    { value: 'last_60', label: t.last60Days || 'Last 60 Days' },
                    { value: 'last_90', label: t.last90Days || 'Last 90 Days' },
                    { value: 'full_year', label: t.fullYear || 'Full Contract Year' },
                    { value: 'custom', label: t.custom || 'Custom Range' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setReportFilter(option.value)}
                      className={`w-full text-left px-3 py-2 text-sm transition-colors ${
                        reportFilter === option.value
                          ? 'bg-primary text-white font-medium'
                          : 'hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}

                  {reportFilter === 'custom' && (
                    <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">{t.startDate || "Start Date"}</label>
                        <input
                          type="date"
                          value={customStartDate}
                          onChange={(e) => setCustomStartDate(e.target.value)}
                          className="w-full px-2 py-1 border border-gray-300 text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">{t.endDate || "End Date"}</label>
                        <input
                          type="date"
                          value={customEndDate}
                          onChange={(e) => setCustomEndDate(e.target.value)}
                          className="w-full px-2 py-1 border border-gray-300 text-sm"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Download Button */}
          <button
            onClick={handleDownloadReport}
            className="p-2 text-primary bg-white border border-gray-200 hover:bg-gray-50 transition-colors"
            title={t.downloadReport || "Download Report"}
          >
            <FileDown size={18}/>
          </button>
        </div>
      </div>

      {showContractWarning && (
        <div className="bg-orange-50 border border-orange-200 p-4 flex items-start gap-3">
            <AlertTriangle className="text-orange-600 shrink-0 mt-1" size={24} />
            <div>
                <h3 className="font-bold text-orange-800 text-lg">{t.contractExpiring || "Contract Expiring Soon"}</h3>
                <p className="text-sm text-orange-700 mt-1">
                    {(t.contractWarningMessage || "Your contract ends in {days} days. Please note that you have {balance} vacation days remaining, which will be lost if not used before the contract renewal.")
                      .replace('{days}', user.days_remaining_in_contract)
                      .replace('{balance}', availableBalance)}
                </p>
            </div>
        </div>
      )}

      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') && pendingCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 flex items-start gap-3 cursor-pointer hover:bg-yellow-100 transition-colors" onClick={() => navigate('/approvals')}>
            <Clock className="text-yellow-600 shrink-0 mt-1" size={24} />
            <div className="flex-1">
                <h3 className="font-bold text-yellow-800 text-lg">{t.pendingApprovals || "Pending Approvals"}</h3>
                <p className="text-sm text-yellow-700 mt-1">
                    {t.pendingApprovalsMessage?.replace('{count}', pendingCount) || `You have ${pendingCount} pending leave request${pendingCount > 1 ? 's' : ''} awaiting your approval.`}
                </p>
            </div>
            <button className="shrink-0 px-4 py-2 bg-yellow-600 text-white text-sm font-semibold hover:bg-yellow-700 transition-colors">
                {t.reviewNow || "Review Now"}
            </button>
        </div>
      )}

      {/* Expiring Contracts Notification */}
      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') && expiringContracts.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 p-4 flex items-start gap-3">
            <CalendarClock className="text-blue-600 shrink-0 mt-1" size={24} />
            <div className="flex-1">
                <h3 className="font-bold text-blue-800 text-lg">
                  {t.contractsExpiringTitle || "Contracts Expiring Soon"}
                </h3>
                <p className="text-sm text-blue-700 mt-1">
                    {t.contractsExpiringMessage?.replace('{count}', expiringContracts.length) ||
                     `${expiringContracts.length} team member${expiringContracts.length > 1 ? 's have' : ' has'} contract${expiringContracts.length > 1 ? 's' : ''} expiring within 105 days. Please initiate the renewal process.`}
                </p>
                <div className="mt-2 space-y-1">
                  {expiringContracts.slice(0, 3).map((contract) => (
                    <div key={contract.employee_id} className="text-xs text-blue-600">
                      • {lang === 'ar' ? contract.name_ar : contract.name_en} - {contract.days_remaining} {t.daysRemaining || "days remaining"}
                    </div>
                  ))}
                  {expiringContracts.length > 3 && (
                    <div className="text-xs text-blue-600">
                      + {expiringContracts.length - 3} {t.more || "more"}
                    </div>
                  )}
                </div>
            </div>
        </div>
      )}

      {/* Contracts Needing Verification Notification */}
      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin') && contractsNeedingVerification.length > 0 && (
        <div className="bg-purple-50 border border-purple-200 p-4 flex items-start gap-3 cursor-pointer hover:bg-purple-100 transition-colors" onClick={() => navigate('/team')}>
            <CheckSquare className="text-purple-600 shrink-0 mt-1" size={24} />
            <div className="flex-1">
                <h3 className="font-bold text-purple-800 text-lg">
                  {t.contractsNeedVerificationTitle || "Contracts Need Verification"}
                </h3>
                <p className="text-sm text-purple-700 mt-1">
                    {t.contractsNeedVerificationMessage?.replace('{count}', contractsNeedingVerification.length) ||
                     `${contractsNeedingVerification.length} contract${contractsNeedingVerification.length > 1 ? 's have' : ' has'} been auto-renewed and require${contractsNeedingVerification.length === 1 ? 's' : ''} your verification.`}
                </p>
                <div className="mt-2 space-y-1">
                  {contractsNeedingVerification.slice(0, 3).map((contract) => (
                    <div key={contract.employee_id} className="text-xs text-purple-600">
                      • {lang === 'ar' ? contract.name_ar : contract.name_en} - {t.newEndDate || "New end date"}: {contract.contract_end_date}
                    </div>
                  ))}
                  {contractsNeedingVerification.length > 3 && (
                    <div className="text-xs text-purple-600">
                      + {contractsNeedingVerification.length - 3} {t.more || "more"}
                    </div>
                  )}
                </div>
            </div>
            <button className="shrink-0 px-4 py-2 bg-purple-600 text-white text-sm font-semibold hover:bg-purple-700 transition-colors">
                {t.verifyNow || "Verify Now"}
            </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Status Widget - Colored Background */}
        <div className={`${statusBgColor} p-6 border ${isOnLeave ? 'border-orange-200' : 'border-green-200'} flex flex-col items-center justify-center min-h-[140px]`}>
          <h3 className={`text-xs font-semibold uppercase tracking-wider mb-3 ${statusTextColor}`}>
            {t.status || "Status"}
          </h3>
          <div className={`text-center text-lg font-bold ${statusTextColor}`}>
            {statusText}
          </div>
        </div>

        {/* Vacation Balance Widget - With Contract End */}
        <div className="bg-white p-4 border border-gray-200 lg:col-span-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3 tracking-wider">{t.vacationBalance}</h3>
          <div className="grid grid-cols-3 gap-3 mb-3">
            <div className="p-3 bg-green-50 border border-green-200 text-center">
              <div className="text-2xl font-bold text-primary">{totalEarned}</div>
              <div className="text-xs text-gray-500 font-medium">{t.totalEarned}</div>
            </div>
            <div className="p-3 bg-red-50 border border-red-200 text-center">
              <div className="text-2xl font-bold text-red-600">{usedBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.used}</div>
            </div>
            <div className="p-3 bg-blue-50 border border-blue-200 text-center">
              <div className="text-2xl font-bold text-blue-600">{availableBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.available}</div>
            </div>
          </div>
          {user.days_remaining_in_contract !== undefined && (
            <div className="bg-gray-50 p-2 border border-gray-200 flex items-center justify-between text-sm">
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