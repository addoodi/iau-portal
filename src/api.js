// API URL configuration
// - In production (Docker): Uses relative path /api (nginx proxies to backend)
// - In development: Uses http://localhost:8000/api (direct backend connection)
const isDevelopment = window.location.port === '3000' || window.location.port === '3001' || window.location.port === '5173' || window.location.port === '3004' || window.location.port === '3005';
export const API_BASE_URL = isDevelopment
  ? 'http://localhost:8000/api'
  : '/api';

// Environment-specific token storage key to prevent conflicts between local and hosted instances
const TOKEN_STORAGE_KEY = isDevelopment ? 'iau_token_dev' : 'iau_token_prod';

// Export the token key for use in other files
export const getTokenStorageKey = () => TOKEN_STORAGE_KEY;

// A utility to get the token from localStorage
export const getToken = () => {
    const tokenData = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!tokenData) return null;
    try {
        const { access_token } = JSON.parse(tokenData);
        return access_token;
    } catch (e) {
        console.error("Failed to parse token:", e);
        return null;
    }
};


const handleResponse = async (response) => {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error or invalid JSON response' }));
        throw new Error(errorData.detail || 'An unknown error occurred');
    }
    // Handle responses that might not have a body
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        return response.json();
    }
    return response.text();
};

const getAuthHeaders = () => {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
    }
};

export const getSetupStatus = async () => {
    const response = await fetch(`${API_BASE_URL}/setup/status`, {
        headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse(response);
}

export const initializeAdmin = async (adminData) => {
    const response = await fetch(`${API_BASE_URL}/setup/initialize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adminData),
    });
    return handleResponse(response);
};

export const login = async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            username: email,
            password: password,
        }),
    });
    const data = await handleResponse(response);
    // Store the token upon successful login
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(data));
    return data;
};

export const fetchUsers = async () => {
    const response = await fetch(`${API_BASE_URL}/users`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const fetchEmployees = async () => {
    const response = await fetch(`${API_BASE_URL}/employees`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const fetchUnits = async () => {
    const response = await fetch(`${API_BASE_URL}/units`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const fetchRequests = async () => {
    const response = await fetch(`${API_BASE_URL}/requests`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const createRequest = async (requestData) => {
    const response = await fetch(`${API_BASE_URL}/requests`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(requestData),
    });
    return handleResponse(response);
};

export const createEmployee = async (employeeData) => {
    const response = await fetch(`${API_BASE_URL}/employees`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(employeeData),
    });
    return handleResponse(response);
};

export const updateEmployee = async (employeeId, employeeData) => {
    const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(employeeData),
    });
    return handleResponse(response);
};

export const createUnit = async (unitData) => {
    const response = await fetch(`${API_BASE_URL}/units`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(unitData),
    });
    return handleResponse(response);
};

export const updateUnit = async (unitId, unitData) => {
    const response = await fetch(`${API_BASE_URL}/units/${unitId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(unitData),
    });
    return handleResponse(response);
};

export const deleteUnit = async (unitId) => {
    const response = await fetch(`${API_BASE_URL}/units/${unitId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });

    if (response.status === 204) {
        return true; // Success, no content
    }

    return handleResponse(response);
};

export const uploadSignature = async (base64Image) => {
    const response = await fetch(`${API_BASE_URL}/users/me/signature`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ image_base64: base64Image }),
    });
    return handleResponse(response);
};

export const deleteSignature = async () => {
    const response = await fetch(`${API_BASE_URL}/users/me/signature`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const getTodayAttendance = async () => {
    const response = await fetch(`${API_BASE_URL}/attendance/today`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const changePassword = async (passwordData) => {
    const response = await fetch(`${API_BASE_URL}/users/me/password`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(passwordData),
    });
    return handleResponse(response);
};

export const updateRequest = async (requestId, updateData) => {
    const response = await fetch(`${API_BASE_URL}/requests/${requestId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updateData),
    });
    return handleResponse(response);
};


export const fetchMe = async () => {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: getAuthHeaders(),
    });
    return handleResponse(response);
};

export const downloadRequestForm = async (requestId) => {

    const response = await fetch(`${API_BASE_URL}/requests/${requestId}/download`, {

        headers: getAuthHeaders(),

    });



    if (!response.ok) {

        const errorData = await response.json().catch(() => ({ detail: 'Network error or invalid JSON response' }));

        throw new Error(errorData.detail || 'An unknown error occurred');

    }



    // Handle the file download

    const blob = await response.blob();

    const contentDisposition = response.headers.get('content-disposition');

    let filename = `request-${requestId}.docx`; // Default filename

    if (contentDisposition) {

        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);

        if (filenameMatch && filenameMatch.length > 1) {

            filename = filenameMatch[1];

        }

    }



    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');

    a.href = url;

    a.download = filename;

    document.body.appendChild(a);

    a.click();

    a.remove();

    window.URL.revokeObjectURL(url);



        return { success: true, filename };



    };



    



export const downloadDashboardReport = async (filterData = { filter_type: 'ytd' }) => {
    const token = getToken();

    const response = await fetch(`${API_BASE_URL}/reports/dashboard`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify(filterData),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
        throw new Error(errorData.detail || 'Failed to download report');
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get('content-disposition');
    let filename = `dashboard-report-${new Date().toISOString().split('T')[0]}.docx`;
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length > 1) {
            filename = filenameMatch[1];
        }
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    return true;
};

// Contract Management API
export const getExpiringContracts = async (daysThreshold = 105) => {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/contracts/expiring?days_threshold=${daysThreshold}`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch expiring contracts');
    }

    return await response.json();
};

export const getContractsNeedingVerification = async () => {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/contracts/needing-verification`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch contracts needing verification');
    }

    return await response.json();
};







    export const deleteUser = async (userId) => {



    



    



    



        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {



    



            method: 'DELETE',



    



            headers: getAuthHeaders(),



    



        });



    



        if (!response.ok) {



    



            const errorData = await response.json().catch(() => ({ detail: 'Network error' }));



    



            throw new Error(errorData.detail || 'An unknown error occurred');



    



        }



    



        return true;



    



    };



    



    



    



    // Email Settings API Calls



    



    export const getEmailSettings = async () => {



    



        const response = await fetch(`${API_BASE_URL}/email/settings`, {



    



            headers: getAuthHeaders(),



    



        });



    



        return handleResponse(response);



    



    };



    



    



    



    export const createEmailSettings = async (settingsData) => {



    



        const response = await fetch(`${API_BASE_URL}/email/settings`, {



    



            method: 'POST',



    



            headers: getAuthHeaders(),



    



            body: JSON.stringify(settingsData),



    



        });



    



        return handleResponse(response);



    



    };



    



    



    



    export const updateEmailSettings = async (settingsData) => {



    



        const response = await fetch(`${API_BASE_URL}/email/settings`, {



    



            method: 'PUT',



    



            headers: getAuthHeaders(),



    



            body: JSON.stringify(settingsData),



    



        });



    



        return handleResponse(response);



    



    };



    



    



    



        export const testEmailSettings = async (settingsData) => {



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



            const response = await fetch(`${API_BASE_URL}/email/test`, {



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



                method: 'POST',



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



                headers: getAuthHeaders(),



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



                body: JSON.stringify(settingsData),



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



            });



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



            return handleResponse(response);



    



    



    



    



    



    



    



    



    



    



    



    



    



    



    



        };



    



    



    



    



    



    



    



        export const uploadAttachment = async (requestId, file) => {



    



    



    



            const formData = new FormData();



    



    



    



            formData.append('file', file);



    



    



    



    



    



    



    



            const response = await fetch(`${API_BASE_URL}/requests/${requestId}/attachments`, {



    



    



    



                method: 'POST',



    



    



    



                headers: {



    



    



    



                    ...(getToken() && { 'Authorization': `Bearer ${getToken()}` }), // Don't set Content-Type for FormData, browser does it



    



    



    



                },



    



    



    



                body: formData,



    



    



    



            });



    



    



    



            return handleResponse(response);



    



    



    



        };
