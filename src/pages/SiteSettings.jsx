import React, { useState, useEffect } from 'react';
import { usePortal } from '../context/PortalContext';
import {
  getEmailSettings,
  createEmailSettings,
  updateEmailSettings,
  testEmailSettings,
} from '../api';
import { Mail, Server, Key, Send, AlertTriangle, CheckCircle, User } from 'lucide-react';

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
    </div>
  );
}
