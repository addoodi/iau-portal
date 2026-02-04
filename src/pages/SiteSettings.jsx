import React, { useState, useEffect } from 'react';
import { usePortal } from '../context/PortalContext';
import { API_BASE_URL, getToken, fetchPortalSettings, updatePortalSettings } from '../api';
import { Upload, AlertTriangle, Check, X, Settings } from 'lucide-react';

export default function SiteSettings() {
  const { t, user } = usePortal();

  // Template upload state
  const [templateFile, setTemplateFile] = useState(null);
  const [templateStatus, setTemplateStatus] = useState(null);
  const [uploadingTemplate, setUploadingTemplate] = useState(false);
  const [message, setMessage] = useState(null);

  // Portal settings state
  const [portalSettings, setPortalSettings] = useState({ max_carry_over_days: 15 });
  const [savingPortalSettings, setSavingPortalSettings] = useState(false);

  useEffect(() => {
    fetchTemplateStatus();
    loadPortalSettings();
  }, []);

  const loadPortalSettings = async () => {
    try {
      const data = await fetchPortalSettings();
      setPortalSettings(data);
    } catch (error) {
      console.error('Failed to fetch portal settings:', error);
    }
  };

  const handleSavePortalSettings = async () => {
    setSavingPortalSettings(true);
    setMessage(null);
    try {
      await updatePortalSettings({ max_carry_over_days: portalSettings.max_carry_over_days });
      setMessage({ type: 'success', text: t.portalSettingsSaved || 'Portal settings saved successfully' });
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to save portal settings' });
    } finally {
      setSavingPortalSettings(false);
    }
  };

  const fetchTemplateStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/settings/template/status`, {
        headers: {
          'Authorization': `Bearer ${getToken()}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTemplateStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch template status:', error);
    }
  };

  const handleTemplateUpload = async () => {
    if (!templateFile) return;

    setUploadingTemplate(true);
    setMessage(null);
    const formData = new FormData();
    formData.append('file', templateFile);

    try {
      const response = await fetch(`${API_BASE_URL}/settings/template`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
        },
        body: formData,
      });

      if (response.ok) {
        setMessage({ type: 'success', text: t.templateUploadSuccess || 'Template uploaded successfully' });
        setTemplateFile(null);
        fetchTemplateStatus();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to upload template' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to upload template' });
    } finally {
      setUploadingTemplate(false);
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white border border-gray-200 text-center text-red-600">
        <AlertTriangle size={24} className="mx-auto mb-2" />
        <p>You are not authorized to view this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white border border-gray-200">
      <h2 className="text-xl font-bold text-primary mb-6">{t.templateManagement || 'Template Management'}</h2>

      {message && (
        <div className={`mb-4 p-3 rounded-md flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? <Check size={18} /> : <AlertTriangle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Current Status */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t.currentTemplate || 'Current Template Status'}
        </label>
        {templateStatus?.exists ? (
          <div className="flex items-center text-green-600 bg-green-50 p-3 rounded-lg border border-green-200">
            <Check size={20} className="mr-2" />
            <div>
              <div className="font-medium">{t.templateExists || 'Template exists'}</div>
              <div className="text-xs text-gray-600">
                {t.uploadedAt || 'Uploaded'}: {new Date(templateStatus.uploaded_at).toLocaleString()}
                ({templateStatus.size_kb} KB)
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center text-orange-600 bg-orange-50 p-3 rounded-lg border border-orange-200">
            <X size={20} className="mr-2" />
            <span className="font-medium">{t.noTemplate || 'No template uploaded'}</span>
          </div>
        )}
      </div>

      {/* Upload New Template */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t.uploadNewTemplate || 'Upload New Template'}
        </label>
        <div className="flex items-center gap-3">
          <input
            type="file"
            accept=".docx"
            onChange={(e) => setTemplateFile(e.target.files[0])}
            className="flex-1 px-3 py-2 border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <button
            onClick={handleTemplateUpload}
            disabled={!templateFile || uploadingTemplate}
            className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            <Upload size={18} />
            {uploadingTemplate ? (t.uploading || 'Uploading...') : (t.upload || 'Upload')}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {t.templateHint || 'Upload a .docx file to be used as the vacation request form template'}
        </p>
      </div>

      {/* Portal Settings */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Settings size={20} />
          {t.portalSettings || 'Portal Settings'}
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t.maxCarryOverDays || 'Max Carry-Over Days'}
            </label>
            <p className="text-xs text-gray-500 mb-2">
              Maximum vacation days permanent employees can carry over to the next year.
            </p>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="0"
                max="365"
                value={portalSettings.max_carry_over_days}
                onChange={(e) => setPortalSettings({ ...portalSettings, max_carry_over_days: parseInt(e.target.value) || 0 })}
                className="w-32 px-3 py-2 border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <button
                onClick={handleSavePortalSettings}
                disabled={savingPortalSettings}
                className="px-4 py-2 bg-primary text-white hover:bg-primary-hover disabled:opacity-50 transition-colors"
              >
                {savingPortalSettings ? '...' : (t.save || 'Save')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Email Settings Note */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-primary mb-2">Email Configuration</h3>
        <p className="text-sm text-gray-600">
          Email settings are configured via environment variables in the <code className="bg-gray-100 px-2 py-1 rounded text-xs">.env</code> file.
          Contact your system administrator to update SMTP settings.
        </p>
      </div>
    </div>
  );
}
