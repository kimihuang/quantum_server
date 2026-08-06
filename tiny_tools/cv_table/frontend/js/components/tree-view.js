/**
 * TreeView — 树形视图组件，SYS → IP → Case 三层展开/折叠。
 */

// 工具函数：提取到模块级，避免模板内定义出错导致整体崩溃
function hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') return `rgba(108,117,125,${alpha})`;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    if (isNaN(r) || isNaN(g) || isNaN(b)) return `rgba(108,117,125,${alpha})`;
    return `rgba(${r},${g},${b},${alpha})`;
}

class TreeView extends Component {
    constructor(container) {
        super(container);
        this._addingSys = false;
        this._addingIP = null;
        this._addingCase = null;

        // 单次注册容器级事件委托，不受 DOM 重建影响
        this._setupDelegation();
    }

    _setupDelegation() {
        // 使用捕获阶段确保优先于子元素处理
        this.container.addEventListener('click', (e) => {
            try {
                this._handleClick(e);
            } catch (err) {
                console.error('[TreeView] click handler error:', err);
                showToast('操作异常: ' + err.message, 'error');
            }
        });
    }

    _handleClick(e) {
        const target = e.target;
        const btn = target.closest('button');

        // ── 行点击：展开/折叠（仅当没点到按钮时）──
        if (!btn) {
            const sysRow = target.closest('.tree-row-sys');
            if (sysRow) {
                const sysId = parseInt(sysRow.dataset.sysId);
                appStore.state.expanded_sys = { ...appStore.state.expanded_sys, [sysId]: !appStore.state.expanded_sys[sysId] };
                this.render();
                return;
            }
            const ipRow = target.closest('.tree-row-ip');
            if (ipRow) {
                const ipId = parseInt(ipRow.dataset.ipId);
                const isNow = !appStore.state.expanded_ip[ipId];
                appStore.state.expanded_ip = { ...appStore.state.expanded_ip, [ipId]: isNow };
                if (isNow) { this._loadCasesForIP(ipId).then(() => this.render()); }
                else { this.render(); }
                return;
            }
            return; // 点到了非按钮、非行的区域，忽略
        }

        // ── 以下是所有按钮的处理 ──

        const id = btn.id || '';
        const cls = btn.className || '';
        const dataset = btn.dataset || {};

        // 添加 SYS
        if (id === 'btn-add-sys') {
            this._addingSys = true;
            this.render();
            return;
        }
        if (id === 'confirm-add-sys') {
            this._confirmAddSys();
            return;
        }
        if (id === 'cancel-add-sys') {
            this._addingSys = false;
            this.render();
            return;
        }

        // 添加 IP
        if (cls.includes && cls.includes('add-ip-btn')) {
            e.stopPropagation();
            const sysId = parseInt(dataset.sysId);
            if (isNaN(sysId)) return;
            this._addingIP = sysId;
            appStore.state.expanded_sys = { ...appStore.state.expanded_sys, [sysId]: true };
            this.render();
            return;
        }
        if (id.startsWith('confirm-add-ip-')) {
            this._confirmAddIP(btn);
            return;
        }
        if (id.startsWith('cancel-add-ip-')) {
            this._addingIP = null;
            this.render();
            return;
        }

        // 添加 Case
        if (cls.includes && cls.includes('add-case-btn')) {
            e.stopPropagation();
            const ipId = parseInt(dataset.ipId);
            if (isNaN(ipId)) return;
            this._addingCase = ipId;
            appStore.state.expanded_ip = { ...appStore.state.expanded_ip, [ipId]: true };
            this.render();
            return;
        }
        if (id.startsWith('confirm-add-case-')) {
            this._confirmAddCase(btn);
            return;
        }
        if (id.startsWith('cancel-add-case-')) {
            this._addingCase = null;
            this.render();
            return;
        }

        // Case 操作
        const action = dataset.action;
        const caseId = parseInt(dataset.caseId);
        if (action === 'exec' && caseId) { this._execCase(caseId); return; }
        if (action === 'edit-case' && caseId) { this._editCase(caseId); return; }
        if (action === 'delete-case' && caseId) { this._deleteCase(caseId); return; }

        // 导入/导出
        if (id === 'btn-manage-columns') {
            appStore.state.showColumnManager = !appStore.state.showColumnManager;
            this.render();
            // 初始化 ColumnManager 组件
            if (appStore.state.showColumnManager && !this._columnManager) {
                const container = document.getElementById('column-manager-container');
                if (container) {
                    this._columnManager = new ColumnManager(container);
                    container.innerHTML = this._columnManager.template();
                    this._columnManager.afterRender();
                }
            }
            return;
        }
        if (id === 'btn-import-tree') {
            document.getElementById('import-file-input')?.click();
            return;
        }
        if (id === 'btn-export-tree') {
            API.exportCSV();
            showToast('导出已开始', 'info');
            return;
        }
    }

    async _confirmAddSys() {
        const name = document.getElementById('add-sys-name')?.value?.trim();
        if (!name) { showToast('请输入SYS名称', 'warning'); return; }
        try {
            await API.createSys({ name });
            this._addingSys = false;
            showToast('添加成功', 'success');
            await this.refreshAll();
        } catch (e) {
            showToast(e.message || '添加失败', 'error');
        }
    }

    async _confirmAddIP(btn) {
        const sysId = parseInt(btn.id.replace('confirm-add-ip-', ''));
        if (isNaN(sysId)) return;
        const name = document.getElementById(`add-ip-name-${sysId}`)?.value?.trim();
        if (!name) { showToast('请输入IP名称', 'warning'); return; }
        try {
            await API.createIP({ name, sys_id: sysId });
            this._addingIP = null;
            showToast('添加成功', 'success');
            await this.refreshAll();
        } catch (e) {
            showToast(e.message || '添加失败', 'error');
        }
    }

    async _confirmAddCase(btn) {
        const ipId = parseInt(btn.id.replace('confirm-add-case-', ''));
        if (isNaN(ipId)) return;
        const name = document.getElementById(`add-case-name-${ipId}`)?.value?.trim();
        if (!name) { showToast('请输入Case名称', 'warning'); return; }

        // 收集自定义字段值
        const customFields = {};
        const cols = appStore.state.customColumns || [];
        for (const col of cols) {
            const el = document.getElementById(`add-case-cf-${col.field_key}-${ipId}`);
            if (el && el.value !== '' && el.value !== undefined) {
                customFields[col.field_key] = el.value;
            }
        }

        try {
            await API.createCase({
                name,
                ip_id: ipId,
                owner: document.getElementById(`add-case-owner-${ipId}`)?.value?.trim() || '',
                priority: document.getElementById(`add-case-pri-${ipId}`)?.value || 'P2',
                custom_fields: customFields,
            });
            this._addingCase = null;
            showToast('添加成功', 'success');
            await this.refreshAll();
        } catch (e) {
            showToast(e.message || '添加失败', 'error');
        }
    }

    afterRender() {
        // 事件委托已在 constructor 中注册，此处无需再绑定
    }

    template() {
        try {
            return this._buildTemplate();
        } catch (err) {
            console.error('[TreeView] template error:', err);
            return '<div class="empty-state"><p style="color:red">页面渲染错误，请刷新</p></div>';
        }
    }

    _buildTemplate() {
        const { systems, ips, expanded_sys, expanded_ip, cases_by_ip } = appStore.state;

        return `
            <div class="tree-view">
                <div class="tree-header">
                    <div class="tree-stats" id="tree-stats">${this._renderStats()}</div>
                    <div class="tree-actions">
                        <button class="btn btn-outline btn-sm" id="btn-manage-columns">列管理</button>
                        <button class="btn btn-outline btn-sm" id="btn-import-tree">导入CSV</button>
                        <button class="btn btn-outline btn-sm" id="btn-export-tree">导出CSV</button>
                        <button class="btn btn-primary btn-sm" id="btn-add-sys">+ 添加_SYS</button>
                    </div>
                </div>
                <div id="column-manager-container"></div>
                ${this._addingSys ? this._renderAddSysForm() : ''}
                <div class="tree-body" id="tree-body">
                    ${systems.map(sys => this._renderSysNode(sys, ips, expanded_sys, expanded_ip, cases_by_ip)).join('')}
                </div>
                ${systems.length === 0 && !this._addingSys ? '<div class="empty-state"><p>暂无数据，点击"+ 添加_SYS"开始</p></div>' : ''}
            </div>
        `;
    }

    _renderStats() {
        const s = appStore.state.stats;
        return `<span>总计: <strong>${s.total || 0}</strong></span>
                <span style="color:#16a34a">通过: <strong>${s.pass_count || 0}</strong></span>
                <span style="color:#dc2626">失败: <strong>${s.fail_count || 0}</strong></span>
                <span style="color:#f59e0b">阻塞: <strong>${s.blocked_count || 0}</strong></span>
                <span>通过率: <strong>${s.pass_rate || 0}%</strong></span>`;
    }

    _renderAddSysForm() {
        return `
            <div class="inline-form">
                <input type="text" id="add-sys-name" class="form-input" placeholder="SYS名称，如 CPU_SYS" autofocus>
                <button class="btn btn-primary btn-sm" id="confirm-add-sys">添加</button>
                <button class="btn btn-secondary btn-sm" id="cancel-add-sys">取消</button>
            </div>`;
    }

    _renderAddIPForm(sysId) {
        return `
            <div class="inline-form" style="margin-left:40px">
                <input type="text" id="add-ip-name-${sysId}" class="form-input" placeholder="IP名称，如 A78" autofocus>
                <button class="btn btn-primary btn-sm" id="confirm-add-ip-${sysId}">添加</button>
                <button class="btn btn-secondary btn-sm" id="cancel-add-ip-${sysId}">取消</button>
            </div>`;
    }

    _renderAddCaseForm(ipId) {
        const priorities = (appStore.state.priorityConfig || {}).priorities || [];
        const priOpts = priorities.map(p => `<option value="${p.value}">${p.label}</option>`).join('');

        // 自定义列输入框
        const cols = appStore.state.customColumns || [];
        const cfInputs = cols.map(col => {
            const req = col.is_required ? ' required' : '';
            if (col.column_type === 'select') {
                const opts = (col.options || []).map(o => `<option value="${o}">${o}</option>`).join('');
                return `<select id="add-case-cf-${col.field_key}-${ipId}" class="form-select" style="width:100px"${req}><option value="">--</option>${opts}</select>`;
            }
            if (col.column_type === 'number') {
                return `<input type="number" id="add-case-cf-${col.field_key}-${ipId}" class="form-input" placeholder="${escapeHtml(col.name)}" style="width:90px"${req}>`;
            }
            return `<input type="text" id="add-case-cf-${col.field_key}-${ipId}" class="form-input" placeholder="${escapeHtml(col.name)}" style="width:120px"${req}>`;
        }).join('');

        return `
            <div class="inline-form" style="margin-left:20px; flex-wrap:wrap">
                <input type="text" id="add-case-name-${ipId}" class="form-input" placeholder="Case名称" autofocus style="width:200px">
                <input type="text" id="add-case-owner-${ipId}" class="form-input" placeholder="负责人" style="width:100px">
                <select id="add-case-pri-${ipId}" class="form-select" style="width:80px">${priOpts}</select>
                ${cfInputs}
                <button class="btn btn-primary btn-sm" id="confirm-add-case-${ipId}">添加</button>
                <button class="btn btn-secondary btn-sm" id="cancel-add-case-${ipId}">取消</button>
            </div>`;
    }

    _renderSysNode(sys, ips, expanded_sys, expanded_ip, cases_by_ip) {
        const isExpanded = !!expanded_sys[sys.id];
        const sysIps = ips.filter(ip => ip.sys_id === sys.id);
        const arrow = isExpanded ? '▼' : '▶';

        return `
            <div class="tree-node tree-sys">
                <div class="tree-row tree-row-sys" data-sys-id="${sys.id}">
                    <span class="tree-toggle">${arrow}</span>
                    <span class="tree-name sys-name">${escapeHtml(sys.name)}</span>
                    <button class="btn btn-sm btn-outline add-ip-btn" data-sys-id="${sys.id}" style="margin-left:6px">+ IP</button>
                    <span class="tree-count">${sys.ip_count || 0} IPs, ${sys.case_count || 0} Cases</span>
                </div>
                ${isExpanded ? `
                    <div class="tree-children">
                        ${this._addingIP === sys.id ? this._renderAddIPForm(sys.id) : ''}
                        ${sysIps.map(ip => this._renderIPNode(ip, expanded_ip, cases_by_ip)).join('')}
                        ${sysIps.length === 0 ? '<div class="tree-empty">暂无IP</div>' : ''}
                    </div>` : ''}
            </div>`;
    }

    _renderIPNode(ip, expanded_ip, cases_by_ip) {
        const isExpanded = !!expanded_ip[ip.id];
        const cases = cases_by_ip[ip.id] || [];
        const arrow = isExpanded ? '▼' : '▶';

        return `
            <div class="tree-node tree-ip">
                <div class="tree-row tree-row-ip" data-ip-id="${ip.id}">
                    <span class="tree-indent"></span>
                    <span class="tree-toggle">${arrow}</span>
                    <span class="tree-name ip-name">${escapeHtml(ip.name)}</span>
                    <button class="btn btn-sm btn-outline add-case-btn" data-ip-id="${ip.id}" style="margin-left:6px">+ Case</button>
                    <span class="tree-count">${ip.case_count || 0} Cases</span>
                </div>
                ${isExpanded ? `
                    <div class="tree-children">
                        ${this._addingCase === ip.id ? this._renderAddCaseForm(ip.id) : ''}
                        ${cases.length > 0 ? this._renderCaseTable(cases) : ''}
                        ${cases.length === 0 && this._addingCase !== ip.id ? '<div class="tree-empty">暂无Case</div>' : ''}
                    </div>` : ''}
            </div>`;
    }

    _renderCaseTable(cases) {
        const cols = appStore.state.customColumns || [];
        const customHeaders = cols.map(c => `<th>${escapeHtml(c.name)}</th>`).join('');
        return `
            <div class="case-table-wrapper">
                <table class="data-table">
                    <thead><tr>
                        <th>Case名称</th><th style="width:60px">优先级</th><th style="width:70px">状态</th>
                        <th style="width:70px">负责人</th>${customHeaders}<th style="width:130px">更新时间</th><th style="width:160px">操作</th>
                    </tr></thead>
                    <tbody>${cases.map(c => this._renderCaseRow(c)).join('')}</tbody>
                </table>
            </div>`;
    }

    _renderCaseRow(c) {
        const statusCfg = (APP_CONFIG.statuses || []).find(s => s.value === c.status) || {};
        const priCfg = (APP_CONFIG.priorities || []).find(p => p.value === c.priority) || {};
        const sc = statusCfg.color || '#9ca3af';
        const pc = priCfg.color || '#6b7280';

        // 自定义列单元格
        const cf = c.custom_fields || {};
        const cols = appStore.state.customColumns || [];
        const customCells = cols.map(col => {
            const val = cf[col.field_key];
            if (val === undefined || val === null) return '<td>-</td>';
            if (col.column_type === 'select') return `<td><span class="cf-select">${escapeHtml(String(val))}</span></td>`;
            if (col.column_type === 'number') return `<td style="text-align:right">${val}</td>`;
            return `<td>${escapeHtml(String(val))}</td>`;
        }).join('');

        return `
            <tr>
                <td><strong>${escapeHtml(c.name)}</strong></td>
                <td><span class="priority-badge" style="background:${hexToRgba(pc,0.15)};color:${pc};border:1px solid ${hexToRgba(pc,0.3)}">${priCfg.label || c.priority}</span></td>
                <td><span class="status-badge" style="background:${hexToRgba(sc,0.15)};color:${sc};border:1px solid ${hexToRgba(sc,0.3)}">${statusCfg.label || c.status}</span></td>
                <td>${escapeHtml(c.owner || '-')}</td>${customCells}
                <td><small>${formatDateTime(c.updated_at)}</small></td>
                <td class="action-cell">
                    <button class="btn btn-sm btn-outline" data-action="exec" data-case-id="${c.id}">执行</button>
                    <button class="btn btn-sm btn-outline" data-action="edit-case" data-case-id="${c.id}">编辑</button>
                    <button class="btn btn-sm btn-danger" data-action="delete-case" data-case-id="${c.id}">删除</button>
                </td>
            </tr>`;
    }

    // ── Data Helpers ──

    async _loadCasesForIP(ipId) {
        try {
            const result = await API.getCases({ ip_id: ipId, page: 1, page_size: 100 });
            const cases = { ...appStore.state.cases_by_ip };
            cases[ipId] = result.items || [];
            appStore.state.cases_by_ip = cases;
        } catch (e) {
            console.error('加载Cases失败:', e);
        }
    }

    async refreshAll() {
        try {
            const [systems, ips, config, stats, columns] = await Promise.all([
                API.getSystems(), API.getIPs(null), API.getConfig(), API.getStats(),
                API.getColumns().catch(() => []),  // 兼容旧版本
            ]);
            appStore.state.systems = systems || [];
            appStore.state.ips = ips || [];
            appStore.state.stats = stats || {};
            appStore.state.customColumns = columns || [];
            if (config) {
                if (config.statuses) appStore.state.statusConfig = config.statuses;
                if (config.priorities) appStore.state.priorityConfig = config.priorities;
                if (config.status_transitions) appStore.state.statusTransitions = config.status_transitions;
            }

            // 重新加载已展开IP的cases
            const expanded = { ...appStore.state.expanded_ip };
            const cases = { ...appStore.state.cases_by_ip };
            for (const [ipId, isExp] of Object.entries(expanded)) {
                if (isExp) {
                    const result = await API.getCases({ ip_id: parseInt(ipId), page: 1, page_size: 100 });
                    cases[ipId] = result.items || [];
                }
            }
            appStore.state.cases_by_ip = cases;
        } catch (e) {
            console.error('refreshAll error:', e);
            showToast('刷新数据失败: ' + e.message, 'error');
        }
        this.render();
    }

    async _execCase(caseId) {
        try {
            const item = await API.getCase(caseId);
            const statusTransitions = appStore.state.statusTransitions || {};
            const statusConfig = appStore.state.statusConfig || APP_CONFIG.statuses;
            const allowed = statusTransitions[item.status] || [];

            const body = `
                <p>Case: <strong>${escapeHtml(item.name)}</strong></p>
                <p>当前: ${this._statusBadge(item.status)}</p>
                <div class="form-field"><label>目标状态</label><select id="exec-status" class="form-select">
                    ${allowed.map(s => { const cfg = (statusConfig || []).find(c => c.value === s); return `<option value="${s}">${cfg ? cfg.label : s}</option>`; }).join('')}
                </select></div>
                <div class="form-field"><label>执行人</label><input type="text" id="exec-executor" class="form-input"></div>
                <div class="form-field"><label>日志</label><textarea id="exec-log" class="form-textarea" rows="2"></textarea></div>`;

            Modal.confirm('执行 Case', body, async () => {
                const status = document.getElementById('exec-status')?.value;
                const executor = document.getElementById('exec-executor')?.value?.trim() || '';
                const log = document.getElementById('exec-log')?.value?.trim() || '';
                await API.updateCaseStatus(caseId, { status, executor, log });
                showToast('状态更新成功', 'success');
                await this.refreshAll();
            });
        } catch (e) {
            showToast(e.message || '操作失败', 'error');
        }
    }

    async _editCase(caseId) {
        try {
            const item = await API.getCase(caseId);
            const priorityConfig = appStore.state.priorityConfig || APP_CONFIG.priorities;
            const priOpts = priorityConfig.map(p =>
                `<option value="${p.value}" ${p.value === item.priority ? 'selected' : ''}>${p.label}</option>`
            ).join('');

            // 自定义列编辑字段
            const cf = item.custom_fields || {};
            const cols = appStore.state.customColumns || [];
            const cfFields = cols.map(col => {
                const val = cf[col.field_key] !== undefined ? escapeHtml(String(cf[col.field_key])) : '';
                if (col.column_type === 'select') {
                    const opts = (col.options || []).map(o => `<option value="${o}" ${o == cf[col.field_key] ? 'selected' : ''}>${o}</option>`).join('');
                    return `<div class="form-field"><label>${escapeHtml(col.name)}</label><select id="edit-case-cf-${col.field_key}" class="form-select"><option value="">--</option>${opts}</select></div>`;
                }
                if (col.column_type === 'number') {
                    return `<div class="form-field"><label>${escapeHtml(col.name)}</label><input type="number" id="edit-case-cf-${col.field_key}" class="form-input" value="${val}"></div>`;
                }
                return `<div class="form-field"><label>${escapeHtml(col.name)}</label><input type="text" id="edit-case-cf-${col.field_key}" class="form-input" value="${val}"></div>`;
            }).join('');

            const body = `
                <div class="form-field"><label>Case名称</label><input type="text" id="edit-case-name" class="form-input" value="${escapeHtml(item.name)}"></div>
                <div class="form-field"><label>负责人</label><input type="text" id="edit-case-owner" class="form-input" value="${escapeHtml(item.owner || '')}"></div>
                <div class="form-field"><label>优先级</label><select id="edit-case-pri" class="form-select">${priOpts}</select></div>
                ${cfFields}
                <div class="form-field"><label>描述</label><textarea id="edit-case-desc" class="form-textarea" rows="2">${escapeHtml(item.description || '')}</textarea></div>`;

            Modal.confirm('编辑 Case', body, async () => {
                const name = document.getElementById('edit-case-name')?.value?.trim();
                if (!name) { showToast('请输入Case名称', 'warning'); return; }

                // 收集自定义字段值
                const customFields = {};
                for (const col of cols) {
                    const el = document.getElementById(`edit-case-cf-${col.field_key}`);
                    if (el && el.value !== '' && el.value !== undefined) {
                        customFields[col.field_key] = col.column_type === 'number' ? parseFloat(el.value) : el.value;
                    }
                }

                await API.updateCase(caseId, {
                    name,
                    owner: document.getElementById('edit-case-owner')?.value?.trim() || '',
                    priority: document.getElementById('edit-case-pri')?.value || 'P2',
                    description: document.getElementById('edit-case-desc')?.value?.trim() || '',
                    custom_fields: customFields,
                });
                showToast('更新成功', 'success');
                await this.refreshAll();
            });
        } catch (e) {
            showToast(e.message || '操作失败', 'error');
        }
    }

    _deleteCase(caseId) {
        Modal.confirm('确认删除', '<p>确定要删除此Case吗？</p>', async () => {
            try {
                await API.deleteCase(caseId);
                showToast('删除成功', 'success');
                await this.refreshAll();
            } catch (e) {
                showToast(e.message || '删除失败', 'error');
            }
        }, { confirmText: '删除' });
    }

    _statusBadge(status) {
        const cfg = (APP_CONFIG.statuses || []).find(s => s.value === status) || {};
        const color = cfg.color || '#9ca3af';
        return `<span class="status-badge" style="background:${hexToRgba(color,0.15)};color:${color};border:1px solid ${hexToRgba(color,0.3)}">${cfg.label || status}</span>`;
    }
}
