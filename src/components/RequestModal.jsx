import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { uploadAttachment } from '../api';

export default function RequestModal({ onClose }) {
  const { user, createRequest, t } = usePortal();
  const [type, setType] = useState('annual');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const calculateDays = () => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; 
  };

  const days = calculateDays();
  const isValid = days > 0 && (type !== 'annual' || days <= user.vacation_balance);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isValid) {
      setIsSubmitting(true);
      const newRequest = await createRequest({ type, startDate, endDate, days, reason });
      
      if (newRequest && file) {
          try {
              await uploadAttachment(newRequest.id, file);
          } catch (err) {
              console.error("Failed to upload attachment", err);
              alert("Request created, but failed to upload attachment.");
          }
      }
      
      setIsSubmitting(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-300 w-full max-w-md overflow-hidden">
        <div className="bg-primary px-6 py-4 border-b border-gray-200 flex justify-between items-center text-white">
          <h3 className="font-bold text-lg">{t.newRequest}</h3>
          <button onClick={onClose} className="hover:bg-white/20 p-1"><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
           <div>
             <label className="block text-sm font-bold text-gray-700 mb-2">{t.requestType}</label>
             <div className="grid grid-cols-4 gap-2">
               {['annual', 'sick', 'emergency', 'exams'].map((rtype) => (
                 <button
                   key={rtype}
                   type="button"
                   onClick={() => setType(rtype)}
                   className={`p-2 text-xs font-bold border ${type === rtype ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-300 hover:border-primary'}`}
                 >
                   {t[rtype]}
                 </button>
               ))}
             </div>
           </div>

           <div className="grid grid-cols-2 gap-4">
             <div>
               <label className="block text-sm font-medium text-gray-600 mb-1">{t.startDate}</label>
               <input type="date" required className="w-full border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
             </div>
             <div>
               <label className="block text-sm font-medium text-gray-600 mb-1">{t.endDate}</label>
               <input type="date" required className="w-full border border-gray-300 p-2 text-sm focus:border-primary focus:outline-none" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
             </div>
           </div>

           {days > 0 && (
             <div className={`text-sm font-medium p-2 border ${days > user.vacation_balance && type === 'annual' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-green-50 text-green-700 border-green-200'}`}>
               Total Duration: <strong>{days} days</strong>
               {days > user.vacation_balance && type === 'annual' && <span className="block text-xs mt-1">Exceeds available balance ({user.vacation_balance})</span>}
             </div>
           )}

           <div>
             <label className="block text-sm font-medium text-gray-600 mb-1">{t.reason}</label>
             <textarea className="w-full border border-gray-300 p-2 text-sm h-24 resize-none focus:border-primary focus:outline-none" value={reason} onChange={(e) => setReason(e.target.value)}></textarea>
           </div>

           <div>
             <label className="block text-sm font-medium text-gray-600 mb-1">{t.uploadDocument}</label>
             <div className="flex items-center border border-gray-300 p-2">
                <Upload size={16} className="text-gray-400 mr-2" />
                <input type="file" className="text-sm w-full" onChange={(e) => setFile(e.target.files[0])} />
             </div>
           </div>

           <div className="pt-2 flex gap-3">
             <button type="button" onClick={onClose} disabled={isSubmitting} className="flex-1 py-2 border border-gray-300 text-gray-700 font-medium hover:bg-gray-50">{t.cancel}</button>
             <button type="submit" disabled={!isValid || isSubmitting} className="flex-1 py-2 bg-primary text-white font-bold hover:bg-primary-hover disabled:opacity-50">
                {isSubmitting ? 'Sending...' : t.submit}
             </button>
           </div>
        </form>
      </div>
    </div>
  );
}