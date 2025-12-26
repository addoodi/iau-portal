import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, Paperclip } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { API_BASE_URL } from '../api';

export default function Approvals() {
  const { user, employees, requests, updateRequestStatus, t, isRTL, formatDate } = usePortal();

  const [rejectingRequestId, setRejectingRequestId] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectError, setRejectError] = useState('');

  // "user" in context is the Employee profile (after refreshData), so user.id is "IAU-XXX".
  // user.role comes from the User account.

  // Filter employees who report to this user
  const teamEmployeeIds = employees
    .filter(e => {
        // Direct reports
        if (e.manager_id === user?.id) return true;
        // Admins and Deans see all (or specific logic) - for now let's stick to manager hierarchy + Admin override
        if (user?.role === 'admin' && e.id !== user.id) return true; 
        if (user?.role === 'dean' && e.id !== user.id) return true;
        return false;
    })
    .map(e => e.id);

  const pendingRequests = requests.filter(r => teamEmployeeIds.includes(r.employee_id) && r.status === 'Pending');

  const handleRejectClick = (reqId) => {
    setRejectingRequestId(reqId);
    setRejectionReason('');
    setRejectError('');
  };

  const handleConfirmReject = async () => {
    if (!rejectionReason.trim()) {
      setRejectError(t.enterRefusalReason || 'Please enter a refusal reason.');
      return;
    }
    await updateRequestStatus(rejectingRequestId, 'Rejected', rejectionReason);
    setRejectingRequestId(null);
    setRejectionReason('');
    setRejectError('');
  };

  const handleCancelReject = () => {
    setRejectingRequestId(null);
    setRejectionReason('');
    setRejectError('');
  };

  const getAttachmentUrl = (req) => {
      if (req.attachments && req.attachments.length > 0) {
          const filePath = req.attachments[0]; 
          const filename = filePath.split(/[\\/]/).pop();
          return `${API_BASE_URL}/requests/${req.id}/attachments/${filename}`;
      }
      return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 min-h-[500px]">
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-xl font-bold text-[#1e2c54]">{t.approvals}</h2>
      </div>
      <div className="divide-y divide-gray-100">
        {pendingRequests.length === 0 ? (
          <div className="p-12 text-center text-gray-400">
            <CheckCircle size={48} className="mx-auto mb-4 text-gray-200" />
            <p>{t.noPendingRequests || "All caught up! No pending requests."}</p>
          </div>
        ) : (
          pendingRequests.map(req => {
             const requester = employees.find(e => e.id === req.employee_id);
             
             // Conflict Detection
             const conflicts = requests.filter(r => {
                 if (r.status !== 'Approved') return false;
                 // Check if the other request is from a team member (or any employee if Admin)
                 // We want to know if *other* people in the team are away.
                 if (!teamEmployeeIds.includes(r.employee_id)) return false;
                 if (r.employee_id === req.employee_id) return false;
                 
                 const startA = new Date(req.start_date);
                 const endA = new Date(req.end_date);
                 const startB = new Date(r.start_date);
                 const endB = new Date(r.end_date);
                 
                 return startA <= endB && endA >= startB;
             });

             return (
              <div key={req.id} className="p-6 flex flex-col md:flex-row justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                   <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold shrink-0">
                     {(isRTL ? requester?.first_name_ar : requester?.first_name_en)?.charAt(0)}
                   </div>
                   <div className="flex-1">
                     <div className="font-bold text-[#1e2c54]">
                        {isRTL ? `${requester?.first_name_ar} ${requester?.last_name_ar}` : `${requester?.first_name_en} ${requester?.last_name_en}`}
                     </div>
                     <div className="text-xs text-gray-500 mb-2">
                        {isRTL ? requester?.position_ar : requester?.position_en}
                     </div>
                     <div className="bg-gray-100 p-2 rounded text-sm text-gray-700 inline-block border border-gray-200 mb-2">
                        <span className="flex items-center gap-2">
                            {req.duration} {t.days || 'Days'}: {t[req.vacation_type] || req.vacation_type} ({formatDate(req.start_date)} {t.to || 'to'} {formatDate(req.end_date)})
                            {req.attachments && req.attachments.length > 0 && (
                                <a href={getAttachmentUrl(req)} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-700" title={t.viewAttachment}>
                                    <Paperclip size={14} />
                                </a>
                            )}
                        </span>
                     </div>
                     
                     {conflicts.length > 0 && (
                        <div className="mt-2 text-xs text-orange-800 bg-orange-50 p-3 rounded border border-orange-200">
                            <div className="flex items-center gap-1 font-bold mb-1">
                                <AlertTriangle size={14} className="text-orange-600"/>
                                {t.conflicts || "Conflicts"}: {conflicts.length} {t.othersOnLeave || "other(s) on leave"}
                            </div>
                            <ul className="list-disc list-inside space-y-1 ml-1 text-orange-700">
                                {conflicts.map(c => {
                                    const cUser = employees.find(e => e.id === c.employee_id);
                                    const cName = isRTL ? `${cUser?.first_name_ar} ${cUser?.last_name_ar}` : `${cUser?.first_name_en} ${cUser?.last_name_en}`;
                                    return <li key={c.id}>{cName} ({formatDate(c.start_date)} - {formatDate(c.end_date)})</li>
                                })}
                            </ul>
                        </div>
                     )}
                   </div>
                </div>
                <div className="flex gap-2 self-end md:self-center">
                   {rejectingRequestId === req.id ? (
                     <div className="flex flex-col gap-2 p-2 bg-red-50 rounded-md">
                       <textarea
                         value={rejectionReason}
                         onChange={(e) => setRejectionReason(e.target.value)}
                         placeholder={t.enterRefusalReason || "Enter refusal reason"}
                         className="w-full p-2 text-sm border rounded focus:ring-red-500"
                         rows="2"
                       ></textarea>
                       {rejectError && <p className="text-red-600 text-xs">{rejectError}</p>}
                       <div className="flex gap-2">
                         <button onClick={handleConfirmReject} className="flex-1 px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors">{t.confirmReject || 'Confirm Reject'}</button>
                         <button onClick={handleCancelReject} className="flex-1 px-3 py-1.5 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-md hover:bg-red-100 transition-colors">{t.cancel || 'Cancel'}</button>
                       </div>
                     </div>
                   ) : (
                     <>
                       <button onClick={() => handleRejectClick(req.id)} className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors">{t.reject || 'Reject'}</button>
                       <button onClick={() => updateRequestStatus(req.id, 'Approved')} className="px-4 py-2 text-sm font-medium text-white bg-[#0f5132] rounded-md hover:bg-[#0b3d26] transition-colors">{t.approve || 'Approve'}</button>
                     </>
                   )}
                </div>
              </div>
             );
          })
        )}
      </div>
    </div>
  );
}
