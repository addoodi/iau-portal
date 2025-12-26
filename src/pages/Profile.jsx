import React, { useState } from 'react';
import { CheckCircle, FileText, Trash2 } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { changePassword } from '../api';

export default function Profile() {
   const { user, uploadSignature, deleteSignature, t, lang } = usePortal();
   const [currentPassword, setCurrentPassword] = useState('');
   const [newPassword, setNewPassword] = useState('');
   const [message, setMessage] = useState(null);
   const [loading, setLoading] = useState(false);

   const handleFile = async (e) => {
     const file = e.target.files[0];
     if (file) {
       setLoading(true);
       setMessage(null);
       const reader = new FileReader();
       reader.onloadend = async () => {
         try {
            const success = await uploadSignature(reader.result);
            if (success) {
                setMessage({ type: 'success', text: 'Signature uploaded successfully' });
            } else {
                setMessage({ type: 'error', text: 'Failed to upload signature' });
            }
         } catch (err) {
            setMessage({ type: 'error', text: err.message || 'Error uploading signature' });
         } finally {
            setLoading(false);
         }
       };
       reader.readAsDataURL(file);
     }
   };

   const handleDeleteSignature = async () => {
       if (window.confirm("Delete your signature?")) {
           setLoading(true);
           const success = await deleteSignature();
           if (success) setMessage({ type: 'success', text: 'Signature deleted' });
           setLoading(false);
       }
   };

   const handlePasswordChange = async (e) => {
       e.preventDefault();
       setLoading(true);
       setMessage(null);
       try {
           await changePassword({ current_password: currentPassword, new_password: newPassword });
           setMessage({ type: 'success', text: 'Password updated successfully' });
           setCurrentPassword('');
           setNewPassword('');
       } catch (err) {
           setMessage({ type: 'error', text: err.message || 'Failed to update password' });
       } finally {
           setLoading(false);
       }
   };

   return (
     <div className="max-w-2xl mx-auto space-y-6">
       {/* ... Header ... */}
       <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
          {/* ... User Info ... */}
          <div className="h-24 w-24 rounded-full bg-[#0f5132] text-white flex items-center justify-center font-bold text-3xl mx-auto mb-4 border-4 border-green-50 shadow-lg">
             {(lang === 'ar' ? user.name_ar : user.name_en)?.charAt(0)}
          </div>
          <h3 className="text-xl font-bold text-[#1e2c54]">{lang === 'ar' ? user.name_ar : user.name_en}</h3>
          <p className="text-gray-500">{lang === 'ar' ? user.position_ar : user.position_en}</p>
          <span className="inline-block mt-2 px-3 py-1 bg-green-50 text-[#0f5132] text-xs font-bold rounded-full">
            {lang === 'ar' ? user.unit_name_ar : user.unit_name_en}
          </span>
       </div>

       <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-bold text-[#1e2c54]">{t.uploadSignature}</h4>
            {user.signature_path && (
                <button onClick={handleDeleteSignature} className="text-red-500 hover:text-red-700 text-xs flex items-center gap-1">
                    <Trash2 size={14}/> {t.deleteSignature || "Delete Signature"}
                </button>
            )}
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-gray-50 hover:bg-gray-100 transition-colors relative">
            <input 
              type="file" 
              accept="image/*"
              onChange={handleFile}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            {user.signature_path ? (
              <div className="flex flex-col items-center">
                <div className="text-green-600 text-4xl mb-2"><CheckCircle /></div>
                <span className="text-green-600 font-bold flex items-center gap-1">
                   {t.signatureOnFile || "Signature On File"}
                </span>
                <span className="text-xs text-gray-400 mt-2">{t.clickToReplace || "Click to replace"}</span>
              </div>
            ) : (
              <div className="flex flex-col items-center text-gray-500">
                 <div className="p-3 bg-white rounded-full shadow-sm mb-3">
                   <FileText className="text-[#c5a017]" size={24} />
                 </div>
                 <span className="text-sm font-medium">{t.clickToUpload || "Click to upload your digital signature"}</span>
                 <span className="text-xs text-gray-400 mt-1">{t.signatureUsage || "Used for auto-signing documents"}</span>
              </div>
            )}
          </div>
       </div>

       <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
          <h4 className="font-bold text-[#1e2c54] mb-4">{t.changePassword || "Change Password"}</h4>
          {message && <div className={`mb-4 p-2 rounded text-sm ${message.type === 'error' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>{message.text}</div>}
          <form onSubmit={handlePasswordChange} className="space-y-4">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input 
                  type="password" 
                  placeholder={t.currentPassword || "Current Password"} 
                  className="border p-2 rounded focus:ring-2 focus:ring-[#0f5132]"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                />
                <input 
                  type="password" 
                  placeholder={t.newPassword || "New Password"} 
                  className="border p-2 rounded focus:ring-2 focus:ring-[#0f5132]"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
             </div>
             <button type="submit" disabled={loading} className="bg-[#0f5132] text-white px-4 py-2 rounded text-sm font-bold hover:bg-[#0b3d26] disabled:opacity-50">
               {loading ? 'Updating...' : (t.updatePassword || "Update Password")}
             </button>
          </form>
       </div>
     </div>
   );
}