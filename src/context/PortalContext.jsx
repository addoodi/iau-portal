import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { TRANSLATIONS } from '../utils/translations';
import {
  fetchUsers,
  fetchEmployees,
  fetchRequests,
  fetchUnits,
  login as apiLogin,
  createRequest as apiCreateRequest,
  updateRequest as apiUpdateRequest,
  fetchMe,
  initializeAdmin as apiInitializeAdmin,
  createUnit as apiCreateUnit,
  updateUnit as apiUpdateUnit,
  deleteUnit as apiDeleteUnit,
  updateEmployee as apiUpdateEmployee,
  uploadSignature as apiUploadSignature,
  deleteSignature as apiDeleteSignature,
  getTodayAttendance as apiGetTodayAttendance,
  deleteUser as apiDeleteUser,
} from '../api';

const PortalContext = createContext();

export const PortalProvider = ({ children }) => {
  const [lang, setLang] = useState('en');
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [requests, setRequests] = useState([]);
  const [units, setUnits] = useState([]);
  const [attendance, setAttendance] = useState(null);
  const [dateSystem, setDateSystem] = useState('gregorian');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  const toggleDateSystem = () => {
      setDateSystem(prev => prev === 'gregorian' ? 'hijri' : 'gregorian');
  };

  const formatDate = (dateString, options = {}) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      const locale = dateSystem === 'hijri' 
          ? (lang === 'ar' ? 'ar-SA-u-ca-islamic' : 'en-US-u-ca-islamic') 
          : (lang === 'ar' ? 'ar-SA' : 'en-US');
      
      return date.toLocaleDateString(locale, { year: 'numeric', month: 'long', day: 'numeric', ...options });
  };

  const userRole = user?.role;
  const userId = user?.user_id;

  const refreshData = useCallback(async () => {
    if (!userId) {
      setUsers([]);
      setEmployees([]);
      setRequests([]);
      setUnits([]);
      return;
    }
    try {
      setLoading(true);
      const isAdmin = userRole?.toLowerCase() === 'admin';
      
      const [usersResult, employeesResult, requestsResult, unitsResult, attendanceResult] = await Promise.all([
        isAdmin ? fetchUsers().catch(e => { console.error("fetchUsers failed", e); return []; }) : Promise.resolve([]),
        fetchEmployees().catch(e => { console.error("fetchEmployees failed", e); return []; }),
        fetchRequests().catch(e => { console.error("fetchRequests failed", e); return []; }),
        fetchUnits().catch(e => { console.error("fetchUnits failed", e); return []; }),
        apiGetTodayAttendance().catch(e => { console.error("getAttendance failed", e); return null; }),
      ]);

      const usersData = usersResult || [];
      const employeesData = employeesResult || [];
      const requestsData = requestsResult || [];
      const unitsData = unitsResult || [];
      
      const combinedEmployees = employeesData.map(emp => {
          const userAccount = usersData.find(u => u.id === emp.user_id);
          const unit = unitsData.find(u => u.id === emp.unit_id);
          return {
              ...userAccount,
              ...emp,
              id: emp.id,
              name: `${emp.first_name_ar} ${emp.last_name_ar}`,
              name_ar: `${emp.first_name_ar} ${emp.last_name_ar}`,
              name_en: `${emp.first_name_en} ${emp.last_name_en}`,
              balance: emp.vacation_balance,
              unit_name_ar: unit ? unit.name_ar : 'N/A',
              unit_name_en: unit ? unit.name_en : 'N/A',
          };
      });

      const fullCurrentUserProfile = combinedEmployees.find(emp => emp.user_id === userId);
      if (fullCurrentUserProfile) {
          setUser(prevUser => ({...prevUser, ...fullCurrentUserProfile}));
      }

      setUsers(usersData);
      setEmployees(combinedEmployees);
      setRequests(requestsData);
      setUnits(unitsData);
      setAttendance(attendanceResult);
      setError(null);
    } catch (err) {
      console.error("refreshData failed:", err);
      setError(err.message || 'Failed to fetch data');
      // logout(); // Removed to prevent logout loops on partial failures
    }
    finally {
      setLoading(false);
    }
  }, [userId, userRole]);

  useEffect(() => {
    const checkAuth = async () => {
      setLoading(true);
      try {
        const loggedInUser = await fetchMe();
        if (loggedInUser) {
            loggedInUser.name_ar = `${loggedInUser.first_name_ar || ''} ${loggedInUser.last_name_ar || ''}`.trim();
            loggedInUser.name_en = `${loggedInUser.first_name_en || ''} ${loggedInUser.last_name_en || ''}`.trim();
            loggedInUser.name = loggedInUser.name_ar || loggedInUser.name_en;
        }
        setUser(loggedInUser);
      } catch (err) {
        setUser(null);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const t = TRANSLATIONS[lang];
  const isRTL = lang === 'ar';

  const login = async (email, password) => {
    try {
      setLoading(true);
      await apiLogin(email, password);
      console.log("apiLogin successful.");
      const loggedInUser = await fetchMe();
      if (loggedInUser) {
        loggedInUser.name_ar = `${loggedInUser.first_name_ar || ''} ${loggedInUser.last_name_ar || ''}`.trim();
        loggedInUser.name_en = `${loggedInUser.first_name_en || ''} ${loggedInUser.last_name_en || ''}`.trim();
        loggedInUser.name = loggedInUser.name_ar || loggedInUser.name_en;
      }
      setUser(loggedInUser);
      setError(null);
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      setError(error.message || 'Invalid credentials');
      localStorage.removeItem('token');
      setUser(null);
      setLoading(false);
      return false;
    }
  };

  const createRequest = async (requestData) => {
    if (!user) {
      setError("You must be logged in to create a request.");
      return false;
    }
    try {
      const newRequestData = {
        vacation_type: requestData.type,
        start_date: requestData.startDate,
        end_date: requestData.endDate,
      };
      const newRequest = await apiCreateRequest(newRequestData);
      setRequests([newRequest, ...requests]);
      return newRequest; // Return the object instead of true
    } catch (error) {
      console.error("Failed to create request:", error);
      setError(error.message || "Failed to create request");
      return null;
    }
  };

  const updateRequestStatus = async (reqId, newStatus, reason = null) => {
    try {
      const updateData = { status: newStatus };
      if (newStatus === 'Rejected' && reason) {
        updateData.rejection_reason = reason;
      }
      const updatedRequest = await apiUpdateRequest(reqId, updateData);
      setRequests(requests.map(r => (r.id === reqId ? updatedRequest : r)));
      return true;
    } catch (error) {
      console.error("Failed to update request:", error);
      setError(error.message || "Failed to update request");
      return false;
    }
  };

  const addUnit = async (unitData) => {
    try {
        setLoading(true);
        await apiCreateUnit(unitData);
        await refreshData();
        return true;
    } catch (error) {
        console.error("Failed to add unit:", error);
        setError(error.message || "Failed to add unit");
        return false;
    } finally {
        setLoading(false);
    }
  };

  const editUnit = async (unitId, unitData) => {
    try {
        setLoading(true);
        await apiUpdateUnit(unitId, unitData);
        await refreshData();
        return true;
    } catch (error) {
        console.error("Failed to update unit:", error);
        setError(error.message || "Failed to update unit");
        return false;
    } finally {
        setLoading(false);
    }
  };

  const deleteUnit = async (unitId) => {
    try {
        setLoading(true);
        await apiDeleteUnit(unitId);
        await refreshData();
        return { success: true };
    } catch (error) {
        const errorMessage = error.message || "Failed to delete unit";
        setError(errorMessage);
        return { success: false, error: errorMessage };
    } finally {
        setLoading(false);
    }
  };

  const updateEmployee = async (employeeId, employeeData) => {
    try {
        setLoading(true);
        const updated = await apiUpdateEmployee(employeeId, employeeData);
        await refreshData();
        return updated;
    } catch (error) {
        console.error("Failed to update employee:", error);
        setError(error.message || "Failed to update employee");
        return null;
    } finally {
        setLoading(false);
    }
  };

  const uploadSignature = async (base64) => {
    try {
        setLoading(true);
        await apiUploadSignature(base64);
        await refreshData(); // To get the new signature path if needed, though frontend uses base64 preview usually.
        // Actually, refreshing might update the user object with the new signature path URL if we served it back.
        // For now, let's just refresh.
        return true;
    } catch (error) {
        console.error("Failed to upload signature:", error);
        setError(error.message || "Failed to upload signature");
        return false;
    } finally {
        setLoading(false);
    }
  };

  const deleteSignature = async () => {
    try {
        setLoading(true);
        await apiDeleteSignature();
        await refreshData();
        return true;
    } catch (error) {
        console.error("Failed to delete signature:", error);
        setError(error.message || "Failed to delete signature");
        return false;
    } finally {
        setLoading(false);
    }
  };

  const deleteUser = async (userId) => {
      try {
          setLoading(true);
          await apiDeleteUser(userId);
          await refreshData();
          return true;
      } catch (error) {
          console.error("Failed to delete user:", error);
          setError(error.message || "Failed to delete user");
          return false;
      } finally {
          setLoading(false);
      }
  };

  const initializeAdmin = async (adminData) => {
    return await apiInitializeAdmin(adminData);
  };

  const isHijri = dateSystem === 'hijri';

  return (
    <PortalContext.Provider value={{
      user, users, employees, requests, units, attendance, lang, t, isRTL, loading, error,
      setLang, login, logout, createRequest, updateRequestStatus, uploadSignature, deleteSignature,
      initializeAdmin, refreshData, addUnit, editUnit, deleteUnit, updateEmployee, deleteUser,
      dateSystem, toggleDateSystem, formatDate, isHijri
    }}>
      {children}
    </PortalContext.Provider>
  );
};

export const usePortal = () => useContext(PortalContext);
