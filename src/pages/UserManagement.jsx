import React, { useState } from 'react';
import { usePortal } from '../context/PortalContext';
import AddUserModal from '../components/AddUserModal';

export default function UserManagement() {

  const { employees, t, refreshData, isRTL, deleteUser, user } = usePortal();

  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);

  const [selectedUser, setSelectedUser] = useState(null);



  const handleUserAdded = () => {

    refreshData();

  };



  const handleClose = () => {

      setIsAddUserModalOpen(false);

      setSelectedUser(null);

  };



  const handleEdit = (emp) => {

      setSelectedUser(emp);

      setIsAddUserModalOpen(true);

  };



  const handleDelete = async (emp) => {

      if (window.confirm(t.confirmDeleteUser || `Are you sure you want to delete ${isRTL ? emp.name_ar : emp.name_en}? This action cannot be undone.`)) {

          const success = await deleteUser(emp.user_id);

          if (success) {

              // Notification handled by context or just refresh

          }

      }

  };



  return (

    <>

      {isAddUserModalOpen && (

        <AddUserModal 

          onClose={handleClose}

          onUserAdded={handleUserAdded}

          initialUser={selectedUser}

        />

      )}

      <div className="bg-white border border-gray-200">

        <div className="p-6 border-b border-gray-200 bg-gray-50 flex justify-between items-center">

          <h2 className="text-xl font-bold text-primary">{t.userManagement}</h2>

          <button

            onClick={() => setIsAddUserModalOpen(true)}

            className="bg-accent text-white px-3 py-1.5 text-sm font-bold hover:bg-accent-hover"

          >

            + {t.addUser}

          </button>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-left">

            <thead className="bg-gray-50 text-xs font-bold text-gray-500 uppercase">

              <tr>

                <th className="px-6 py-4">{t.name}</th>

                <th className="px-6 py-4">{t.role}</th>

                <th className="px-6 py-4">{t.unit}</th>

                <th className="px-6 py-4 text-right">{t.actions}</th>

              </tr>

            </thead>

            <tbody className="divide-y divide-gray-100 text-sm">

              {employees.map(emp => (

                <tr key={emp.id} className="hover:bg-gray-50">

                  <td className="px-6 py-4">

                    <div className="font-bold text-primary">{isRTL ? emp.name_ar : emp.name_en}</div>

                    <div className="text-xs text-gray-500">{isRTL ? emp.position_ar : emp.position_en}</div>

                  </td>

                  <td className="px-6 py-4">

                    <span className={`px-2 py-1 rounded text-xs font-semibold border ${

                      emp.role === 'admin' 

                      ? 'bg-red-50 text-red-600 border-red-200' 

                      : 'bg-gray-100 text-gray-600 border-gray-200'

                    }`}>

                      {emp.role}

                    </span>

                  </td>

                  <td className="px-6 py-4 text-gray-600">{isRTL ? emp.unit_name_ar : emp.unit_name_en}</td>

                  <td className="px-6 py-4 text-right text-gray-400 space-x-2">

                    <button onClick={() => handleEdit(emp)} className="hover:text-primary font-medium text-sm">{t.edit || 'Edit'}</button>

                    {emp.user_id !== user.user_id && (

                        <button onClick={() => handleDelete(emp)} className="hover:text-red-600 font-medium text-sm text-red-400">{t.delete || 'Delete'}</button>

                    )}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

    </>

  );

}
