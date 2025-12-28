import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { usePortal } from '../context/PortalContext';
import { convertToHijri, getHijriMonthNames } from '../utils/hijriUtils';

export default function DashboardTimeline({ teamMembers, requests }) {
  const { t, lang, isHijri, isRTL } = usePortal();
  const [currentDate, setCurrentDate] = useState(new Date());

  // Generate 60 days starting from current date
  const days = useMemo(() => {
    const result = [];
    const start = new Date(currentDate);
    start.setDate(1); // Start from first of month

    for (let i = 0; i < 60; i++) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      result.push(date);
    }
    return result;
  }, [currentDate]);

  // Navigate to previous/next month
  const goToPreviousMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() - 1);
    setCurrentDate(newDate);
  };

  const goToNextMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + 1);
    setCurrentDate(newDate);
  };

  // Check if date is weekend (Friday/Saturday)
  const isWeekend = (date) => {
    const day = date.getDay();
    return day === 5 || day === 6; // Friday = 5, Saturday = 6
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Get status for a specific employee on a specific date
  const getStatusForDate = (employeeId, date) => {
    const dayRequests = requests.filter(r => {
      if (r.employee_id !== employeeId) return false;
      const startDate = new Date(r.start_date);
      const endDate = new Date(r.end_date);
      return date >= startDate && date <= endDate;
    });

    if (dayRequests.length === 0) return null;

    // Check for approved request
    const approved = dayRequests.find(r => r.status === 'Approved');
    if (approved) return { status: 'Approved', type: approved.vacation_type };

    // Check for pending request
    const pending = dayRequests.find(r => r.status === 'Pending');
    if (pending) return { status: 'Pending', type: pending.vacation_type };

    return null;
  };

  // Get cell background color based on status
  const getCellClass = (employeeId, date) => {
    const status = getStatusForDate(employeeId, date);
    const weekend = isWeekend(date);
    const today = isToday(date);

    let bgClass = 'bg-white';
    if (weekend) bgClass = 'bg-gray-100';
    if (status?.status === 'Approved') bgClass = 'bg-green-100';
    if (status?.status === 'Pending') bgClass = 'bg-yellow-100';

    const borderClass = today ? 'border-2 border-blue-500' : 'border border-gray-200';

    return `${bgClass} ${borderClass} h-12 min-w-[40px] text-center text-xs`;
  };

  // Check if employee is on leave today
  const getEmployeeCurrentStatus = (employeeId) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const onLeaveToday = requests.find(r => {
      if (r.employee_id !== employeeId || r.status !== 'Approved') return false;
      const startDate = new Date(r.start_date);
      const endDate = new Date(r.end_date);
      startDate.setHours(0, 0, 0, 0);
      endDate.setHours(0, 0, 0, 0);
      return today >= startDate && today <= endDate;
    });

    return onLeaveToday ? 'on-leave' : 'present';
  };

  // Format date for display
  const formatDateHeader = (date) => {
    if (isHijri) {
      const hijriDate = convertToHijri(date);
      return `${hijriDate.day}`;
    }
    return date.getDate();
  };

  // Get month name
  const getMonthName = () => {
    if (isHijri) {
      const hijriDate = convertToHijri(currentDate);
      const hijriMonths = getHijriMonthNames(lang);
      return `${hijriMonths[hijriDate.month - 1]} ${hijriDate.year}`;
    }
    return currentDate.toLocaleDateString(lang === 'ar' ? 'ar-SA' : 'en-US', { month: 'long', year: 'numeric' });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#1e2c54]">{t.teamTimeline || "Team Timeline"}</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">{getMonthName()}</span>
          <div className="flex gap-1">
            <button
              onClick={isRTL ? goToNextMonth : goToPreviousMonth}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title={isRTL ? (t.nextMonth || "Next Month") : (t.previousMonth || "Previous Month")}
            >
              <ChevronLeft size={20} />
            </button>
            <button
              onClick={isRTL ? goToPreviousMonth : goToNextMonth}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title={isRTL ? (t.previousMonth || "Previous Month") : (t.nextMonth || "Next Month")}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="p-3 border-b border-gray-100 flex items-center gap-4 text-xs bg-gray-50">
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
          <span className="text-gray-600">{t.approved || "Approved"}</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
          <span className="text-gray-600">{t.pending || "Pending"}</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
          <span className="text-gray-600">{t.weekend || "Weekend"}</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-4 bg-white border-2 border-blue-500 rounded"></div>
          <span className="text-gray-600">{t.today || "Today"}</span>
        </div>
      </div>

      {/* Timeline Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th className="sticky left-0 bg-gray-50 z-20 p-2 text-left text-xs font-semibold text-gray-600 min-w-[200px] border-r border-gray-200">
                {t.employee || "Employee"} ({t.balance || "Balance"})
              </th>
              {days.map((date, idx) => (
                <th key={idx} className="p-1 text-xs font-normal text-gray-600 min-w-[40px]">
                  <div className="text-center">{formatDateHeader(date)}</div>
                  <div className="text-[10px] text-gray-400">
                    {date.toLocaleDateString(lang === 'ar' ? 'ar-SA' : 'en-US', { weekday: 'narrow' })}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {teamMembers.map((member) => {
              const currentStatus = getEmployeeCurrentStatus(member.id);
              const cellBgColor = currentStatus === 'on-leave' ? 'bg-orange-50' : 'bg-green-50';
              const cellBorderColor = currentStatus === 'on-leave' ? 'border-orange-200' : 'border-green-200';

              return (
              <tr key={member.id} className="hover:bg-gray-50 transition-colors">
                <td className={`sticky left-0 ${cellBgColor} z-10 p-2 text-sm border-r-2 ${cellBorderColor} border-b border-gray-100`}>
                  <Link to={`/employee/${member.id}`} className="block">
                    <div className="flex items-center justify-between cursor-pointer hover:opacity-80">
                      <span className="font-medium text-gray-800">
                        {lang === 'ar' ? member.name_ar : member.name_en}
                      </span>
                      <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        {member.vacation_balance || 0}
                      </span>
                    </div>
                  </Link>
                </td>
                {days.map((date, idx) => {
                  const status = getStatusForDate(member.id, date);
                  return (
                    <td
                      key={idx}
                      className={getCellClass(member.id, date)}
                      title={status ? `${status.status}: ${t[status.type] || status.type}` : ''}
                    >
                      {status && (
                        <div className="flex items-center justify-center h-full">
                          {status.status === 'Approved' ? '✓' : '?'}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {teamMembers.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          {t.noTeamMembers || "No team members to display"}
        </div>
      )}
    </div>
  );
}
