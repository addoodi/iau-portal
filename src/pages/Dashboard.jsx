import React from 'react';
import { FileDown, Clock, CheckCircle, LogIn, LogOut, AlertTriangle } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { downloadDashboardReport } from '../api';

export default function Dashboard() {
  const { user, employees, requests, t, lang, attendance, loading, formatDate } = usePortal();

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

  const formatTime = (isoString) => {
    if (!isoString) return '--:--';
    return new Date(isoString).toLocaleTimeString(lang === 'ar' ? 'ar-SA' : 'en-US', { hour: '2-digit', minute: '2-digit' });
  };

  // Determine attendance status display
  let statusDisplay;
  let statusColor;
  
  if (attendance?.status === "On Leave") {
      statusDisplay = (
        <span className="flex items-center gap-1 text-xs font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">
            <span className="w-2 h-2 rounded-full bg-orange-600"></span>
            {t.onLeave || "On Leave"} ({t[attendance.vacation_type] || attendance.vacation_type})
        </span>
      );
      statusColor = "text-orange-600";
  } else {
      statusDisplay = (
        <span className="flex items-center gap-1 text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded-full animate-pulse">
            <span className="w-2 h-2 rounded-full bg-green-600"></span>
            {t.present || "Present"}
        </span>
      );
      statusColor = "text-[#1e2c54]";
  }
  
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Attendance Widget */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
             <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">{t.todaysAttendance || "Today's Attendance"}</h3>
             {statusDisplay}
          </div>
          
          <div className="flex items-center justify-center my-6">
             <div className="text-center">
                 <div className="text-4xl font-bold mb-2 flex items-center justify-center gap-3">
                     <Clock size={32} className="text-gray-300"/>
                     <span className={statusColor}>
                        {new Date().toLocaleTimeString(lang === 'ar' ? 'ar-SA' : 'en-US', { hour: '2-digit', minute: '2-digit' })}
                     </span>
                 </div>
                 <div className="text-sm text-gray-400">
                    {formatDate(new Date(), { weekday: 'long' })}
                 </div>
             </div>
          </div>
          
          <div className="bg-gray-50 p-3 rounded-lg text-center text-xs text-gray-500">
              {attendance?.status === "On Leave" ? 
                 (t.enjoyVacation || "Enjoy your vacation!") : 
                 (t.autoAttendanceMessage || "Attendance is automatically recorded based on your schedule.")
              }
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-sm font-bold text-gray-500 uppercase mb-4 tracking-wider">{t.vacationBalance}</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-[#0f5132]">{totalEarned}</div>
              <div className="text-xs text-gray-500 font-medium">{t.earned}</div>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{usedBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.used}</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{availableBalance}</div>
              <div className="text-xs text-gray-500 font-medium">{t.available}</div>
            </div>
          </div>
        </div>
      </div>

      {(user.role?.toLowerCase() === 'manager' || user.role?.toLowerCase() === 'admin' || user.role?.toLowerCase() === 'dean') && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <h3 className="text-lg font-bold text-[#1e2c54]">{t.teamOverview}</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {teamMembers.map(member => (
              <div key={member.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                   <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                     {(lang === 'ar' ? member.name_ar : member.name_en)?.charAt(0) || '?'}
                   </div>
                   <div>
                     <div className="text-sm font-bold text-[#1e2c54]">{(lang === 'ar' ? member.name_ar : member.name_en) || 'User'}</div>
                     <div className="text-xs text-gray-500">{(lang === 'ar' ? member.position_ar : member.position_en) || member.role || 'N/A'}</div>
                   </div>
                </div>
                <div className="w-32 md:w-48">
                   <div className="flex justify-between text-xs mb-1">
                     <span className="font-medium text-gray-600">{t.balance}</span>
                     <span className="font-bold text-blue-600">{member.balance || 0}</span>
                   </div>
                   <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div className="bg-[#0f5132] h-full rounded-full" style={{ width: `${((member.balance || 0) / ((member.balance || 0) + 0.1)) * 100}%` }}></div> 
                   </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}