const BASE_URL = APP_CONFIG.api.baseURL;

async function request(url, options = {}) {
    const defaults = { headers: { 'Content-Type': 'application/json' } };
    const merged = { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } };
    const res = await fetch(BASE_URL + url, merged);
    const data = res.headers.get('content-type')?.includes('json') ? await res.json() : await res.text();
    if (!res.ok) throw { status: res.status, message: data?.error?.message || `HTTP ${res.status}`, code: data?.error?.code };
    return data;
}

function getQuery(params) {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
        if (v !== null && v !== undefined && v !== '') q.append(k, v);
    }
    return q.toString();
}

const API = {
    // Systems
    getSystems: () => request('/systems'),
    createSys: (data) => request('/systems', { method: 'POST', body: JSON.stringify(data) }),
    updateSys: (id, data) => request('/systems/' + id, { method: 'PUT', body: JSON.stringify(data) }),
    deleteSys: (id) => request('/systems/' + id, { method: 'DELETE' }),

    // IPs
    getIPs: (sysId) => request('/ips' + (sysId !== null ? '?sys_id=' + sysId : '')),
    createIP: (data) => request('/ips', { method: 'POST', body: JSON.stringify(data) }),
    updateIP: (id, data) => request('/ips/' + id, { method: 'PUT', body: JSON.stringify(data) }),
    deleteIP: (id) => request('/ips/' + id, { method: 'DELETE' }),

    // Cases
    getCases: (params) => request('/cases?' + getQuery(params)),
    createCase: (data) => request('/cases', { method: 'POST', body: JSON.stringify(data) }),
    updateCase: (id, data) => request('/cases/' + id, { method: 'PUT', body: JSON.stringify(data) }),
    deleteCase: (id) => request('/cases/' + id, { method: 'DELETE' }),
    updateCaseStatus: (id, data) => request('/cases/' + id + '/status', { method: 'PUT', body: JSON.stringify(data) }),
    getExecutions: (id) => request('/cases/' + id + '/executions'),

    // Stats
    getConfig: () => request('/stats/config'),
    getStats: () => request('/stats/overview'),
    getStatsBySys: () => request('/stats/by-sys'),

    // Import/Export
    exportCSV: () => window.open(BASE_URL + '/cases/export/csv', '_blank'),
    importCSV: async (file) => {
        const fd = new FormData(); fd.append('file', file);
        const res = await fetch(BASE_URL + '/cases/import/csv', { method: 'POST', body: fd });
        if (!res.ok) { const err = await res.json(); throw { message: err?.error?.message || `HTTP ${res.status}` }; }
        return res.json();
    },
};
