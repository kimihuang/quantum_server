/**
 * 响应式状态管理 — 树形结构版
 */
class Store {
    constructor(initialState = {}) {
        this._listeners = new Map();
        this.state = this._makeReactive(initialState);
    }

    _makeReactive(obj) {
        const self = this;
        for (const key of Object.keys(obj)) {
            if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
                obj[key] = new Proxy(obj[key], {
                    set(target, k, v) { target[k] = v; self._notify(key, obj[key]); return true; }
                });
            }
        }
        return new Proxy(obj, {
            set(target, key, value) {
                const old = target[key];
                target[key] = value;
                if (old !== value) self._notify(key, value, old);
                return true;
            }
        });
    }

    on(key, callback) {
        if (!this._listeners.has(key)) this._listeners.set(key, new Set());
        this._listeners.get(key).add(callback);
        return () => this.off(key, callback);
    }
    off(key, callback) { this._listeners.get(key)?.delete(callback); }
    _notify(key, value, oldValue) {
        this._listeners.get(key)?.forEach(cb => cb(value, oldValue));
    }
}

const appStore = new Store({
    systems: [],            // SYS 列表
    ips: [],                // IP 列表（按 SYS 筛选）
    cases_by_ip: {},        // { ip_id: [Case数组] }
    expanded_sys: {},       // { sys_id: bool }
    expanded_ip: {},        // { ip_id: bool }
    customColumns: [],      // 自定义列定义列表
    showColumnManager: false, // 是否显示列管理面板
    stats: { total: 0, pass_count: 0, fail_count: 0, not_run_count: 0, blocked_count: 0, skip_count: 0, pass_rate: 0 },
    statusConfig: APP_CONFIG.statuses,
    priorityConfig: APP_CONFIG.priorities,
    statusTransitions: {},
    loading: false,
    modal: { open: false, title: '', body: '', onConfirm: null },
});
