import React, { useState, useEffect } from 'react';
import { usePortal } from '../context/PortalContext';
import {
  getEmailSettings,
  createEmailSettings,
  updateEmailSettings,
  testEmailSettings,
  API_BASE_URL,
  getToken,
} from '../api';
import { Mail, Server, Key, Send, AlertTriangle, CheckCircle, User, Upload, FileText, Check, X } from 'lucide-react';

export default function SiteSettings() {
  const { t, user, refreshData } = usePortal();
  const [settings, setSettings] = useState(null);
  const [formData, setFormData] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '', // plaintext for form submission
    sender_email: '',
    is_active: false,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: string }

  // Template upload state
  const [templateFile, setTemplateFile] = useState(null);
  const [templateStatus, setTemplateStatus] = useState(null);
  const [uploadingTemplate, setUploadingTemplate] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true);
      try {
        const fetchedSettings = await getEmailSettings();
        if (fetchedSettings) {
          setSettings(fetchedSettings);
          setFormData(prev => ({
            ...prev,
            smtp_host: fetchedSettings.smtp_host || '',
            smtp_port: fetchedSettings.smtp_port || 587,
            smtp_username: fetchedSettings.smtp_username || '',
            sender_email: fetchedSettings.sender_email || '',
            is_active: fetchedSettings.is_active || false,
            smtp_password: '', // Never pre-fill password from hash
          }));
        }
      } catch (err) {
        console.error("Failed to fetch email settings:", err);
        setMessage({ type: 'error', text: t.connectionFailed || 'Failed to load settings.' });
      } finally {
        setLoading(false);
      }
    };
    if (user?.role === 'admin') {
      fetchSettings();
    }
  }, [user, refreshData, t]);

  useEffect(() => {
    fetchTemplateStatus();
  }, []);

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

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleTestConnection = async () => {
    setLoading(true);
    setMessage(null);
    try {
      // Use current form data for testing, including plaintext password
      const testData = {
        smtp_host: formData.smtp_host,
        smtp_port: parseInt(formData.smtp_port),
        smtp_username: formData.smtp_username,
        smtp_password: formData.smtp_password,
        sender_email: formData.sender_email,
        is_active: formData.is_active,
      };
      await testEmailSettings(testData);
      setMessage({ type: 'success', text: t.connectionSuccessful || 'SMTP connection successful!' });
    } catch (err) {
      console.error("Test connection failed:", err);
      setMessage({ type: 'error', text: err.message || (t.connectionFailed || 'SMTP connection failed.') });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const dataToSubmit = {
        smtp_host: formData.smtp_host,
        smtp_port: parseInt(formData.smtp_port),
        smtp_username: formData.smtp_username,
        sender_email: formData.sender_email,
        is_active: formData.is_active,
      };
      if (formData.smtp_password) {
        dataToSubmit.smtp_password = formData.smtp_password;
      }

      if (settings) {
        await updateEmailSettings(dataToSubmit);
        setMessage({ type: 'success', text: t.saveChanges || 'Settings updated successfully!' });
      } else {
        await createEmailSettings(dataToSubmit);
        setMessage({ type: 'success', text: t.saveChanges || 'Settings saved successfully!' });
      }
      refreshData(); // Refresh context if needed, e.g. for is_active flag
    } catch (err) {
      console.error("Failed to save settings:", err);
      setMessage({ type: 'error', text: err.message || (t.saveChanges || 'Failed to save settings.') });
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100 text-center text-red-600">
        <AlertTriangle size={24} className="mx-auto mb-2" />
        <p>You are not authorized to view this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <h2 className="text-xl font-bold text-[#1e2c54] mb-6">{t.emailSettings}</h2>

      {message && (
        <div className={`mb-4 p-3 rounded-md flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? <CheckCircle size={18} /> : <AlertTriangle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.smtpHost}</label>
            <div className="flex items-center border rounded-md shadow-sm">
              <Server size={18} className="text-gray-400 mx-2" />
              <input
                type="text"
                name="smtp_host"
                value={formData.smtp_host}
                onChange={handleChange}
                required
                className="flex-1 p-2 focus:outline-none bg-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t.smtpPort}</label>
            <div className="flex items-center border rounded-md shadow-sm">
              <input
                type="number"
                name="smtp_port"
                value={formData.smtp_port}
                onChange={handleChange}
                required
                className="flex-1 p-2 focus:outline-none bg-transparent"
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t.smtpUsername}</label>
          <div className="flex items-center border rounded-md shadow-sm">
            <User size={18} className="text-gray-400 mx-2" />
            <input
              type="text"
              name="smtp_username"
              value={formData.smtp_username}
              onChange={handleChange}
              required
              className="flex-1 p-2 focus:outline-none bg-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t.smtpPassword}</label>
          <div className="flex items-center border rounded-md shadow-sm">
            <Key size={18} className="text-gray-400 mx-2" />
            <input
              type="password"
              name="smtp_password"
              value={formData.smtp_password}
              onChange={handleChange}
              placeholder={settings ? "Leave blank to keep current" : ""}
              className="flex-1 p-2 focus:outline-none bg-transparent"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t.senderEmail}</label>
          <div className="flex items-center border rounded-md shadow-sm">
            <Mail size={18} className="text-gray-400 mx-2" />
            <input
              type="email"
              name="sender_email"
              value={formData.sender_email}
              onChange={handleChange}
              required
              className="flex-1 p-2 focus:outline-none bg-transparent"
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            name="is_active"
            checked={formData.is_active}
            onChange={handleChange}
            className="h-4 w-4 text-[#0f5132] focus:ring-[#0f5132] border-gray-300 rounded"
          />
          <label className="text-sm font-medium text-gray-700">{t.isActive}</label>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={handleTestConnection}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#c5a017]"
          >
            {loading ? 'Testing...' : <><Send size={18} /> {t.testConnection}</>}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#0f5132] hover:bg-[#0b3d26] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0f5132]"
          >
            {loading ? 'Saving...' : t.saveSettings}
          </button>
        </div>
      </form>

      {/* Template Upload Section */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <h2 className="text-xl font-bold text-[#1e2c54] mb-6">{t.templateManagement || 'Template Management'}</h2>

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
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0f5132] focus:border-transparent"
            />
            <button
              onClick={handleTemplateUpload}
              disabled={!templateFile || uploadingTemplate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              <Upload size={18} />
              {uploadingTemplate ? (t.uploading || 'Uploading...') : (t.upload || 'Upload')}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {t.templateHint || 'Upload a .docx file to be used as the vacation request form template'}
          </p>
        </div>
      </div>
    </div>
  );
}
