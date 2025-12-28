import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { usePortal } from '../context/PortalContext';

export default function TeamCalendar({ teamMembers, requests }) {
  const { t, lang, formatDate } = usePortal();
  const [currentDate, setCurrentDate] = useState(new Date());

  // Generate 60 days starting from a base date
  const generateCalendarDays = (baseDate) => {
    const days = [];
    const startDate = new Date(baseDate);

    for (let i = 0; i < 60; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const calendarDays = useMemo(() => generateCalendarDays(currentDate), [currentDate]);

  // Navigate months
  const handlePrevMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() - 1);
    setCurrentDate(newDate);
  };

  const handleNextMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + 1);
    setCurrentDate(newDate);
  };

  // Check if date is weekend
  const isWeekend = (date) => {
    const day = date.getDay();
    return day === 5 || day === 6; // Friday and Saturday for Arabic calendar
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Get status for an employee on a specific date
  const getStatusForDate = (memberId, date) => {
    const onLeave = requests.find(r => {
      if (r.employee_id !== memberId) return false;
      if (r.status !== 'Approved' && r.status !== 'Pending') return false;

      const startDate = new Date(r.start_date);
      const endDate = new Date(r.end_date);
      const checkDate = new Date(date);

      // Reset time components for accurate date comparison
      startDate.setHours(0, 0, 0, 0);
      endDate.setHours(0, 0, 0, 0);
      checkDate.setHours(0, 0, 0, 0);

      return checkDate >= startDate && checkDate <= endDate;
    });

    if (onLeave) {
      return {
        status: onLeave.status,
        isApproved: onLeave.status === 'Approved',
        vacationType: onLeave.vacation_type
      };
    }

    return { status: 'Present' };
  };

  // Format day header
  const formatDayHeader = (date) => {
    return formatDate(date, { day: 'numeric' });
  };

  // Format month/year for navigation
  const formatMonthYear = (date) => {
    return formatDate(date, { month: 'long', year: 'numeric' });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 className="text-lg font-bold text-gray-700">
          {t.teamCalendar || "Team Availability Calendar"}
        </h3>
        <div className="flex items-center gap-3">
          <button
            onClick={handlePrevMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label={lang === 'ar' ? "الشهر السابق" : "Previous Month"}
          >
            <ChevronLeft size={20} />
          </button>
          <span className="text-sm font-medium text-gray-600 min-w-[150px] text-center">
            {formatMonthYear(currentDate)}
          </span>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label={lang === 'ar' ? "الشهر التالي" : "Next Month"}
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
          <span className="text-gray-600">{t.approved || "Approved"}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
          <span className="text-gray-600">{t.pending || "Pending"}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
          <span className="text-gray-600">{t.weekend || "Weekend"}</span>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                {/* Employee Name Header - Sticky */}
                <th className="sticky left-0 z-20 bg-gray-50 border-b border-r border-gray-200 p-2 text-left min-w-[150px]">
                  <span className="text-xs font-semibold text-gray-600 uppercase">
                    {t.employee || "Employee"}
                  </span>
                </th>

                {/* Date Headers */}
                {calendarDays.map((day, index) => {
                  const weekend = isWeekend(day);
                  const today = isToday(day);

                  return (
                    <th
                      key={index}
                      className={`border-b border-r border-gray-200 p-2 text-center min-w-[50px] ${
                        today ? 'bg-blue-50' : weekend ? 'bg-gray-100' : 'bg-gray-50'
                      }`}
                    >
                      <div className="text-xs">
                        <div className={`font-semibold ${today ? 'text-blue-600' : 'text-gray-700'}`}>
                          {formatDayHeader(day)}
                        </div>
                        <div className="text-[10px] text-gray-500">
                          {formatDate(day, { weekday: 'short' })}
                        </div>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {teamMembers.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50 transition-colors">
                  {/* Employee Name - Sticky */}
                  <td className="sticky left-0 z-10 bg-white border-b border-r border-gray-200 p-2">
                    <div className="text-sm">
                      <div className="font-medium text-gray-700">
                        {lang === 'ar'
                          ? `${member.first_name_ar} ${member.last_name_ar}`
                          : `${member.first_name_en} ${member.last_name_en}`
                        }
                      </div>
                      <div className="text-xs text-gray-500">
                        {lang === 'ar' ? member.position_ar : member.position_en}
                      </div>
                    </div>
                  </td>

                  {/* Date Cells */}
                  {calendarDays.map((day, dayIndex) => {
                    const weekend = isWeekend(day);
                    const today = isToday(day);
                    const leaveStatus = getStatusForDate(member.id, day);

                    let cellClass = "border-b border-r border-gray-200 p-1 text-center";
                    let bgClass = "";
                    let content = null;

                    if (weekend && leaveStatus.status === 'Present') {
                      bgClass = "bg-gray-100";
                    } else if (leaveStatus.isApproved) {
                      bgClass = "bg-green-100 border-green-300";
                      content = <Check size={16} className="text-green-600 mx-auto" />;
                    } else if (leaveStatus.status === 'Pending') {
                      bgClass = "bg-yellow-100 border-yellow-300";
                      content = <span className="text-yellow-600 text-sm">?</span>;
                    } else if (today) {
                      bgClass = "bg-blue-50";
                    }

                    return (
                      <td
                        key={dayIndex}
                        className={`${cellClass} ${bgClass}`}
                        title={
                          leaveStatus.status !== 'Present'
                            ? `${leaveStatus.vacationType} - ${leaveStatus.status}`
                            : weekend
                            ? (t.weekend || "Weekend")
                            : (t.present || "Present")
                        }
                      >
                        {content}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
