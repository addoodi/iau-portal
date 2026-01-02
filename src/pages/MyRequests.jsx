import React from 'react';
import { Download, XCircle, Paperclip } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { downloadRequestForm, downloadAttachment } from '../api';

export default function MyRequests() {
  const { user, requests, t, updateRequestStatus, formatDate, isRTL } = usePortal();
  const myRequests = requests.filter(r => r.employee_id === user.id);

  const generateDocx = async (req) => {
    try {
        await downloadRequestForm(req.id);
    } catch (e) {
        console.error(e);
        alert("Failed to download");
    }
  };

  const handleCancel = async (id) => {
      if (window.confirm("Are you sure you want to cancel this request?")) {
          await updateRequestStatus(id, 'Cancelled');
      }
  };

  const handleAttachmentDownload = async (req) => {
      if (req.attachments && req.attachments.length > 0) {
          try {
              const filePath = req.attachments[0];
              const filename = filePath.split(/[\\/]/).pop(); // Handle both slash types
              await downloadAttachment(req.id, filename);
          } catch (e) {
              console.error(e);
              alert("Failed to download attachment");
          }
      }
  };

  return (
    <div className="bg-white border border-gray-200">
      <div className="p-6 border-b border-gray-200 bg-gray-50">
        <h2 className="text-xl font-bold text-primary">{t.myRequests}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 text-xs font-bold text-gray-500 uppercase">
            <tr>
              <th className="px-6 py-4">{t.type}</th>
              <th className="px-6 py-4">{t.date}</th>
              <th className="px-6 py-4">{t.status}</th>
              <th className={`px-6 py-4 ${isRTL ? 'text-left' : 'text-right'}`}>{t.actions}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {myRequests.map(req => (
                <tr key={req.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-bold text-primary capitalize flex items-center gap-2">
                        {t[req.vacation_type] || req.vacation_type}
                        {req.attachments && req.attachments.length > 0 && (
                            <button
                                onClick={() => handleAttachmentDownload(req)}
                                className="text-blue-500 hover:text-blue-700"
                                title={t.viewAttachment}
                            >
                                <Paperclip size={14} />
                            </button>
                        )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-700">
                      {formatDate(req.start_date)}
                      {isRTL ? ' ← ' : ' → '}
                      {formatDate(req.end_date)}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border
                      ${req.status === 'Approved' ? 'bg-green-100 text-green-800 border-green-200' : 
                        req.status === 'Rejected' ? 'bg-red-100 text-red-800 border-red-200' : 
                        'bg-yellow-100 text-yellow-800 border-yellow-200'}`}>
                      {t[req.status.toLowerCase()] || req.status}
                    </span>
                    {req.status === 'Rejected' && req.rejection_reason && (
                        <div className="text-xs text-red-600 mt-1">
                            <strong>{t.refusalReason}:</strong> {req.rejection_reason}
                        </div>
                    )}
                  </td>
                  <td className="px-6 py-4 flex gap-2 justify-end">
                    {(req.status === 'Approved' || req.status === 'Rejected') && ( // Allow download for Approved and Rejected
                      <button
                        onClick={() => generateDocx(req)}
                        className={`flex items-center gap-2 px-3 py-1.5 text-primary hover:bg-primary/10 border border-gray-200 font-medium transition-colors ${
                          isRTL ? 'flex-row-reverse' : ''
                        }`}
                      >
                        <Download size={18} />
                        <span className="text-sm">{t.downloadForm}</span>
                      </button>
                    )}
                    {req.status === 'Pending' && (
                      <button onClick={() => handleCancel(req.id)} className="text-red-500 hover:bg-red-50 p-2 rounded-full" title={t.cancel}>
                        <XCircle size={18} />
                      </button>
                    )}
                  </td>
                </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}