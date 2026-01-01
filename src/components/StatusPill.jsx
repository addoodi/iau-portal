import React, { useState } from 'react';
import { usePortal } from '../context/PortalContext';

const StatusPill = ({ attendance }) => {
  const { t, lang } = usePortal();
  const [showTooltip, setShowTooltip] = useState(false);

  const isOnLeave = attendance?.status === "On Leave";

  // Color logic: green for present, orange for on leave
  const pillBgColor = isOnLeave ? "bg-orange-500" : "bg-green-500";
  const pillTextColor = "text-white";

  const statusText = isOnLeave
    ? (t.onLeave || "On Leave")
    : (t.onDuty || "On Duty");

  return (
    <div className="relative inline-block">
      <span
        className={`${pillBgColor} ${pillTextColor} px-3 py-1 text-xs font-semibold uppercase tracking-wide ${isOnLeave && attendance?.return_to_work_date ? 'cursor-help' : ''}`}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {statusText}
      </span>

      {/* Tooltip showing return date when on leave */}
      {showTooltip && isOnLeave && attendance?.return_to_work_date && (
        <div className="absolute z-50 px-3 py-2 bg-gray-900 text-white text-xs rounded shadow-lg whitespace-nowrap"
             style={{
               top: '100%',
               left: lang === 'ar' ? 'auto' : '0',
               right: lang === 'ar' ? '0' : 'auto',
               marginTop: '4px'
             }}>
          {t.returnToWorkDate || "Return to Work Date"}: {attendance.return_to_work_date}
          {/* Small arrow */}
          <div
            className="absolute w-2 h-2 bg-gray-900 transform rotate-45"
            style={{
              top: '-4px',
              left: lang === 'ar' ? 'auto' : '12px',
              right: lang === 'ar' ? '12px' : 'auto'
            }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default StatusPill;
