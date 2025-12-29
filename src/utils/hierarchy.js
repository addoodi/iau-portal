/**
 * Manager hierarchy utilities for recursive subordinate lookups.
 * Frontend version of the backend hierarchy module.
 */

/**
 * Get all subordinate employee IDs for a manager (direct and indirect)
 * @param {string} managerId - The manager's employee ID
 * @param {Array} allEmployees - All employees in the system
 * @param {boolean} includeIndirect - Include subordinates of subordinates (recursive)
 * @returns {Array} List of employee IDs that report to this manager
 *
 * @example
 * // Manager1 -> Manager2 -> Employee
 * const subordinates = getAllSubordinates(manager1Id, allEmployees, true);
 * // Returns [manager2Id, employeeId]
 */
export function getAllSubordinates(managerId, allEmployees, includeIndirect = true) {
    const subordinateIds = new Set();
    const visited = new Set(); // Prevent infinite loops from circular references

    function findSubordinates(mgrId) {
        // Prevent infinite recursion from circular references
        if (visited.has(mgrId)) {
            return;
        }
        visited.add(mgrId);

        // Find direct reports
        const directReports = allEmployees.filter(emp => emp.manager_id === mgrId);

        for (const employee of directReports) {
            // Skip if this would create a circular reference
            if (employee.id === mgrId) {
                continue;
            }

            subordinateIds.add(employee.id);

            // Recursively find their subordinates if includeIndirect is true
            if (includeIndirect) {
                findSubordinates(employee.id);
            }
        }
    }

    findSubordinates(managerId);
    return Array.from(subordinateIds);
}

/**
 * Check if an employee is a subordinate of a manager
 * @param {string} employeeId - Employee to check
 * @param {string} managerId - Manager to check against
 * @param {Array} allEmployees - All employees in the system
 * @returns {boolean} True if employee is a subordinate (directly or indirectly)
 *
 * @example
 * // Manager1 -> Manager2 -> Employee
 * isSubordinateOf(employeeId, manager1Id, allEmployees);
 * // Returns true
 */
export function isSubordinateOf(employeeId, managerId, allEmployees) {
    const subordinates = getAllSubordinates(managerId, allEmployees, true);
    return subordinates.includes(employeeId);
}
