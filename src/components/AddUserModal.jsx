import React, { useState } from 'react';
import { X } from 'lucide-react';
import { usePortal } from '../context/PortalContext';
import { createEmployee, updateEmployee } from '../api';

export default function AddUserModal({ onClose, onUserAdded, initialUser = null }) {
  const { t, units, isRTL, employees } = usePortal();
  const [formData, setFormData] = useState({
    email: initialUser?.email || '',
    password: '',
    role: initialUser?.role || 'user',
    first_name_en: initialUser?.first_name_en || '',
    last_name_en: initialUser?.last_name_en || '',
    first_name_ar: initialUser?.first_name_ar || '',
    last_name_ar: initialUser?.last_name_ar || '',
    position_ar: initialUser?.position_ar || '',
    position_en: initialUser?.position_en || '',
    unit_id: initialUser?.unit_id || (units.length > 0 ? units[0].id : ''),
    start_date: initialUser?.start_date || '',
    monthly_vacation_earned: initialUser?.monthly_vacation_earned || 2.5,
    manager_id: initialUser?.manager_id || '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const managers = employees.filter(e => ['manager', 'admin', 'dean'].includes(e.role?.toLowerCase()));

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      // Basic validation with conditional requirements for admin role
      for (const key in formData) {
        if (key === 'password' && initialUser && formData[key] === '') continue; // Skip password check for edit

        // For admin role, skip validation for unit_id, manager_id, and start_date
        if (formData.role === 'admin' && (key === 'unit_id' || key === 'manager_id' || key === 'start_date')) {
          continue;
        }

        if (formData[key] === '' || formData[key] === null) {
          throw new Error(`Please fill in all fields. Missing: ${key}`);
        }
      }
      
      if (initialUser) {
          await updateEmployee(initialUser.id, formData);
      } else {
          await createEmployee(formData);
      }
      onUserAdded();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to save user. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="bg-[#0f5132] p-4 flex justify-between items-center text-white">
          <h3 className="font-bold text-lg">{initialUser ? t.editUser : t.addUser}</h3>
          <button onClick={onClose} className="hover:bg-white/20 p-1 rounded-full"><X size={20} /></button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
          {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">{error}</div>}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* User Info */}
            <div className="space-y-4 p-4 border rounded">
                <h4 className="font-bold text-md text-gray-700 border-b pb-2">{t.userAccount}</h4>
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.email}</label>
                    <input type="email" name="email" required disabled={!!initialUser} className="w-full border rounded p-2 text-sm disabled:bg-gray-100" value={formData.email} onChange={handleChange} />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.password} {initialUser && <span className="text-xs text-gray-400">(Optional)</span>}</label>
                    <input type="password" name="password" required={!initialUser} className="w-full border rounded p-2 text-sm" value={formData.password} onChange={handleChange} placeholder={initialUser ? "Leave blank to keep current" : ""} />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.role}</label>
                    <select name="role" className="w-full border rounded p-2 text-sm bg-white" value={formData.role} onChange={handleChange}>
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                        <option value="employee">Employee</option>
                        <option value="manager">Manager</option>
                    </select>
                </div>
            </div>

            {/* Employee Info */}
            <div className="space-y-4 p-4 border rounded">
                <h4 className="font-bold text-md text-gray-700 border-b pb-2">{t.employeeDetails}</h4>
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.firstNameEn}</label>
                        <input type="text" name="first_name_en" required className="w-full border rounded p-2 text-sm" value={formData.first_name_en} onChange={handleChange} />
                    </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.lastNameEn}</label>
                        <input type="text" name="last_name_en" required className="w-full border rounded p-2 text-sm" value={formData.last_name_en} onChange={handleChange} />
                    </div>
                </div>
                 <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.firstNameAr}</label>
                        <input type="text" name="first_name_ar" required className="w-full border rounded p-2 text-sm" value={formData.first_name_ar} onChange={handleChange} />
                    </div>
                     <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.lastNameAr}</label>
                        <input type="text" name="last_name_ar" required className="w-full border rounded p-2 text-sm" value={formData.last_name_ar} onChange={handleChange} />
                    </div>
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.jobTitleAr}</label>
                    <input type="text" name="position_ar" required className="w-full border rounded p-2 text-sm" value={formData.position_ar} onChange={handleChange} />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.jobTitleEn}</label>
                    <input type="text" name="position_en" required className="w-full border rounded p-2 text-sm" value={formData.position_en} onChange={handleChange} />
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.unit}</label>
                    <select name="unit_id" className="w-full border rounded p-2 text-sm bg-white" value={formData.unit_id} onChange={handleChange}>
                        {units.map(unit => (
                            <option key={unit.id} value={unit.id}>
                                {isRTL ? unit.name_ar : unit.name_en}
                            </option>
                        ))}
                    </select>
                </div>
                 <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">{t.manager}</label>
                    <select name="manager_id" className="w-full border rounded p-2 text-sm bg-white" value={formData.manager_id} onChange={handleChange}>
                        <option value="">{t.selectManager || 'Select Manager'}</option>
                        {managers.map(mgr => (
                            <option key={mgr.id} value={mgr.id}>
                                {isRTL ? mgr.name_ar : mgr.name_en}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.startDate}</label>
                        <input type="date" name="start_date" required className="w-full border rounded p-2 text-sm" value={formData.start_date} onChange={handleChange} />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">{t.monthlyVacationEarned}</label>
                        <input type="number" step="0.1" name="monthly_vacation_earned" required className="w-full border rounded p-2 text-sm" value={formData.monthly_vacation_earned} onChange={handleChange} />
                    </div>
                </div>
            </div>
          </div>

           <div className="pt-2 flex gap-3">
             <button type="button" onClick={onClose} className="w-full py-2 text-gray-600 font-medium hover:bg-gray-100 rounded">{t.cancel}</button>
             <button type="submit" disabled={isLoading} className="w-full py-2 bg-[#0f5132] text-white font-bold rounded shadow-md hover:bg-[#0b3d26] disabled:opacity-50">
                {isLoading ? 'Saving...' : (initialUser ? t.updateUser : t.addUser)}
            </button>
           </div>
        </form>
      </div>
    </div>
  );
}
