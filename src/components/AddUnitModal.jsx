import React, { useState, useEffect } from 'react';
import { usePortal } from '../context/PortalContext';

export default function AddUnitModal({ isOpen, onClose, unitToEdit = null }) {
  const { addUnit, editUnit, t, isRTL } = usePortal();
  const [formData, setFormData] = useState({
    name_en: '',
    name_ar: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (unitToEdit) {
      setFormData({
        name_en: unitToEdit.name_en,
        name_ar: unitToEdit.name_ar,
      });
    } else {
      setFormData({
        name_en: '',
        name_ar: '',
      });
    }
    setError('');
  }, [unitToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let success;
      if (unitToEdit) {
        success = await editUnit(unitToEdit.id, formData);
      } else {
        success = await addUnit(formData);
      }

      if (success) {
        onClose();
      } else {
        setError('Failed to save unit. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white border border-gray-300 w-full max-w-md overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-primary text-white">
          <h3 className="text-xl font-bold">
            {unitToEdit ? (t.editUnit || 'Edit Unit') : (t.addUnit || 'Add Unit')}
          </h3>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 transition-colors p-1"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-3 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t.unitNameEn || 'Unit Name (English)'}
            </label>
            <input
              type="text"
              required
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t.unitNameAr || 'Unit Name (Arabic)'}
            </label>
            <input
              type="text"
              required
              value={formData.name_ar}
              onChange={(e) => setFormData({ ...formData, name_ar: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 focus:border-primary focus:outline-none"
              dir="rtl"
            />
          </div>

          <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium"
            >
              {t.cancel || 'Cancel'}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-primary text-white px-6 py-2 hover:bg-primary-hover font-bold disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading && <div className="w-4 h-4 border-2 border-white/30 border-t-white animate-spin" />}
              {unitToEdit ? (t.saveChanges || 'Save Changes') : (t.addUnit || 'Add Unit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
