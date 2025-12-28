import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePortal } from '../context/PortalContext';
import { Calendar, Briefcase, ArrowLeft } from 'lucide-react';

export default function EmployeeDetailView() {
    const { employeeId } = useParams();
    const navigate = useNavigate();
    const { employees, updateEmployee, user, t, lang } = usePortal();

    const employee = employees.find(e => e.id === employeeId);
    const [isEditing, setIsEditing] = useState(false);
    const [startDate, setStartDate] = useState(employee?.start_date || '');
    const [loading, setLoading] = useState(false);

    // Only managers and admins can access
    const isManager = user.role?.toLowerCase() === 'manager';
    const isAdmin = user.role?.toLowerCase() === 'admin';

    if (!isManager && !isAdmin) {
        return <div>Not authorized</div>;
    }

    // Verify manager can only see their reports
    if (isManager && employee?.manager_id !== user.id) {
        return <div>Not authorized to view this employee</div>;
    }

    if (!employee) {
        return <div>Employee not found</div>;
    }

    const handleSave = async () => {
        setLoading(true);
        const result = await updateEmployee(employee.id, { start_date: startDate });
        setLoading(false);

        if (result) {
            setIsEditing(false);
        } else {
            alert(t.updateFailed || 'Failed to update employee');
        }
    };

    const handleCancel = () => {
        setStartDate(employee.start_date);
        setIsEditing(false);
    };

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
                >
                    <ArrowLeft size={20} className="mr-2" />
                    {t.backToDashboard || 'Back to Dashboard'}
                </button>
                <h1 className="text-2xl font-bold text-gray-900">
                    {lang === 'ar' ? employee.name_ar : employee.name_en}
                </h1>
                <p className="text-gray-600">
                    {lang === 'ar' ? employee.position_ar : employee.position_en}
                </p>
            </div>

            {/* Employee Information Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Vacation Balance Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center mb-4">
                        <Calendar className="text-blue-600 mr-2" size={24} />
                        <h2 className="text-lg font-semibold text-gray-900">
                            {t.vacationBalance || 'Vacation Balance'}
                        </h2>
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">{t.totalEarned || 'Total Earned'}:</span>
                            <span className="font-semibold">{employee.vacation_balance?.toFixed(1) || 0} {t.days || 'days'}</span>
                        </div>
                    </div>
                </div>

                {/* Contract Information Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="flex items-center mb-4">
                        <Briefcase className="text-green-600 mr-2" size={24} />
                        <h2 className="text-lg font-semibold text-gray-900">
                            {t.contractInformation || 'Contract Information'}
                        </h2>
                    </div>
                    <div className="space-y-3">
                        <div>
                            <label className="text-sm text-gray-600">{t.startDate || 'Start Date'}:</label>
                            {isEditing ? (
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            ) : (
                                <div className="font-semibold">{employee.start_date}</div>
                            )}
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">{t.endDate || 'End Date'}:</span>
                            <span className="font-semibold">{employee.contract_end_date || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">{t.daysRemaining || 'Days Remaining'}:</span>
                            <span className="font-semibold">{employee.days_remaining_in_contract || 'N/A'}</span>
                        </div>
                    </div>

                    {/* Edit/Save Buttons */}
                    <div className="mt-4 flex gap-2">
                        {!isEditing ? (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                {t.editContractDate || 'Edit Contract Date'}
                            </button>
                        ) : (
                            <>
                                <button
                                    onClick={handleSave}
                                    disabled={loading}
                                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                                >
                                    {loading ? (t.saving || 'Saving...') : (t.save || 'Save')}
                                </button>
                                <button
                                    onClick={handleCancel}
                                    disabled={loading}
                                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 disabled:opacity-50"
                                >
                                    {t.cancel || 'Cancel'}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
