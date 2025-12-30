import React, { useState } from 'react';
import { usePortal } from '../context/PortalContext';
import AddUnitModal from '../components/AddUnitModal';

export default function UnitManagement() {
  const { units, employees, deleteUnit, t, isRTL, user, lang } = usePortal();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [unitToEdit, setUnitToEdit] = useState(null);

  const isAdmin = user?.role === 'admin';

  const handleEdit = (unit) => {
    setUnitToEdit(unit);
    setIsModalOpen(true);
  };

  const handleAdd = () => {
    setUnitToEdit(null);
    setIsModalOpen(true);
  };

  const handleDeleteUnit = async (unit) => {
    if (!window.confirm(`${t.confirmDeleteUnit || 'Are you sure you want to delete this unit?'} "${lang === 'ar' ? unit.name_ar : unit.name_en}"?`)) {
        return;
    }

    const result = await deleteUnit(unit.id);
    if (!result.success) {
        alert(result.error);
    }
  };
  
  return (
    <div className="space-y-6">
       <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-primary">{t.unitManagement}</h2>
        {isAdmin && (
            <button 
                onClick={handleAdd}
                className="bg-accent text-white px-4 py-2 text-sm font-bold hover:bg-accent-hover transition-colors"
            >
            + {t.addUnit || 'Add Unit'}
            </button>
        )}
      </div>
      
      <div className="grid gap-6">
        {units.map(unit => {
            const unitEmployees = employees.filter(e => e.unit_id === unit.id);
            return (
                <div key={unit.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <h3 className="font-bold text-primary text-lg">{isRTL ? unit.name_ar : unit.name_en}</h3>
                            <span className="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded border border-gray-200">
                                {unitEmployees.length} {t.members || 'Members'}
                            </span>
                        </div>
                        {isAdmin && (
                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleEdit(unit)}
                                    className="text-sm text-blue-600 hover:text-blue-800 font-medium px-3 py-1 hover:bg-blue-50 rounded-lg transition-colors"
                                >
                                    {t.edit || 'Edit'}
                                </button>
                                <button
                                    onClick={() => handleDeleteUnit(unit)}
                                    className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1 hover:bg-red-50 rounded-lg transition-colors"
                                >
                                    {t.delete || 'Delete'}
                                </button>
                            </div>
                        )}
                    </div>
                    <div className="p-4">
                        {unitEmployees.length > 0 ? (
                            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {unitEmployees.map(emp => (
                                    <li key={emp.id} className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg border border-gray-100 hover:border-gray-200 transition-all">
                                        <div className="h-10 w-10 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold shrink-0">
                                            {(isRTL ? emp.name_ar : emp.name_en)?.charAt(0) || '?'}
                                        </div>
                                        <div className="min-w-0">
                                            <div className="text-sm font-bold text-gray-800 truncate">{isRTL ? emp.name_ar : emp.name_en}</div>
                                            <div className="text-xs text-gray-500 truncate">{isRTL ? emp.position_ar : emp.position_en}</div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="text-sm text-gray-400 italic text-center py-4">{t.noMembers || 'No members in this unit'}</div>
                        )}
                    </div>
                </div>
            );
        })}
      </div>
      
      <AddUnitModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        unitToEdit={unitToEdit} 
      />
    </div>
  );
}
