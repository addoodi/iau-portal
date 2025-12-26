
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePortal } from '../context/PortalContext';

const SetupPage = () => {
    const { initializeAdmin } = usePortal();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        first_name_ar: '',
        last_name_ar: '',
        first_name_en: '',
        last_name_en: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        setLoading(true);
        try {
            await initializeAdmin({
                email: formData.email,
                password: formData.password,
                first_name_ar: formData.first_name_ar,
                last_name_ar: formData.last_name_ar,
                first_name_en: formData.first_name_en,
                last_name_en: formData.last_name_en,
            });
            alert('Admin user created successfully! Please log in.');
            navigate('/login');
        } catch (err) {
            setError(err.message || 'Failed to create admin user. The application might already be set up.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h1 className="text-2xl font-bold mb-6 text-center">Initial Admin Setup</h1>
                <p className="text-center text-gray-600 mb-6">
                    Welcome! Since this is the first time running the application, please create the primary admin account.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-lg"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="block text-gray-700">First Name (EN)</label>
                            <input
                                type="text"
                                name="first_name_en"
                                value={formData.first_name_en}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700">Last Name (EN)</label>
                            <input
                                type="text"
                                name="last_name_en"
                                value={formData.last_name_en}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="block text-gray-700">First Name (AR)</label>
                            <input
                                type="text"
                                name="first_name_ar"
                                value={formData.first_name_ar}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700">Last Name (AR)</label>
                            <input
                                type="text"
                                name="last_name_ar"
                                value={formData.last_name_ar}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                    </div>
                    <div className="mb-4">
                        <label className="block text-gray-700">Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-lg"
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700">Confirm Password</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border rounded-lg"
                        />
                    </div>
                    {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
                    >
                        {loading ? 'Creating Account...' : 'Create Admin Account'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default SetupPage;
