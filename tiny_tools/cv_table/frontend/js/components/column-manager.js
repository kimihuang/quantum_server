/**
 * ColumnManager — 自定义列管理组件，支持添加/编辑/删除列。
 */
class ColumnManager extends Component {
    constructor(container) {
        super(container);
        this._editingId = null;  // 正在编辑的列 ID
        this._showAddForm = false;

        // 容器级事件委托
        this.container.addEventListener('click', (e) => {
            try { this._handleClick(e); } catch (err) { console.error('[ColumnManager]', err); }
        });
    }

    _handleClick(e) {
        const btn = e.target.closest('button');
        if (!btn) return;
        const id = btn.id || '';

        if (id === 'btn-add-column') {
            this._editingId = null;
            this._showAddForm = true;
            this.render();
            return;
        }
        if (id === 'cancel-add-column') {
            this._showAddForm = false;
            this._editingId = null;
            this.render();
            return;
        }
        if (id === 'confirm-add-column') {
            this._confirmAdd();
            return;
        }

        if (id.startsWith('edit-col-')) {
            this._editingId = parseInt(id.replace('edit-col-', ''));
            this._showAddForm = false;
            this.render();
            return;
        }
        if (id.startsWith('delete-col-')) {
            this._deleteColumn(parseInt(id.replace('delete-col-', '')));
            return;
        }
        if (id === 'cancel-edit-col') {
            this._editingId = null;
            this.render();
            return;
        }
        if (id === 'confirm-edit-col') {
            this._confirmEdit();
            return;
        }
        if (id === 'close-column-manager') {
            appStore.state.showColumnManager = false;
            this.render();
            return;
        }
    }

    async _confirmAdd() {
        const name = document.getElementById('col-name')?.value?.trim();
        const fieldKey = document.getElementById('col-field-key')?.value?.trim();
        const colType = document.getElementById('col-type')?.value || 'text';
        const isRequired = document.getElementById('col-required')?.checked || false;
        const options = document.getElementById('col-options')?.value?.trim() || null;

        if (!name) { showToast('请输入列名称', 'warning'); return; }
        if (!fieldKey) { showToast('请输入字段标识', 'warning'); return; }
        if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(fieldKey)) {
            showToast('字段标识必须以字母开头，只允许字母、数字、下划线', 'warning'); return;
        }
        if (colType === 'select' && !options) {
            showToast('select 类型必须提供选项（逗号分隔）', 'warning'); return;
        }

        try {
            await API.createColumn({ name, field_key: fieldKey, column_type: colType, is_required: isRequired, options });
            this._showAddForm = false;
            showToast('添加成功', 'success');
            await this._refresh();
        } catch (e) { showToast(e.message || '添加失败', 'error'); }
    }

    async _confirmEdit() {
        const id = this._editingId;
        if (!id) return;

        const name = document.getElementById('edit-col-name')?.value?.trim();
        const colType = document.getElementById('edit-col-type')?.value || 'text';
        const isRequired = document.getElementById('edit-col-required')?.checked || false;
        const options = document.getElementById('edit-col-options')?.value?.trim() || null;

        if (!name) { showToast('请输入列名称', 'warning'); return; }
        if (colType === 'select' && !options) {
            showToast('select 类型必须提供选项', 'warning'); return;
        }

        try {
            await API.updateColumn(id, { name, column_type: colType, is_required: isRequired, options });
            this._editingId = null;
            showToast('更新成功', 'success');
            await this._refresh();
        } catch (e) { showToast(e.message || '更新失败', 'error'); }
    }

    async _deleteColumn(id) {
        Modal.confirm('确认删除', '<p>确定要删除此自定义列吗？<br><small>已有数据不会丢失，但该列将不再显示</small></p>', async () => {
            try {
                await API.deleteColumn(id);
                showToast('删除成功', 'success');
                await this._refresh();
            } catch (e) { showToast(e.message || '删除失败', 'error'); }
        }, { confirmText: '删除' });
    }

    async _refresh() {
        try {
            appStore.state.customColumns = await API.getColumns();
        } catch (e) { console.error('加载自定义列失败:', e); }
        this.render();
    }

    template() {
        if (!appStore.state.showColumnManager) return '';
        const columns = appStore.state.customColumns || [];
        const typeLabels = { text: '文本', number: '数字', select: '下拉选项' };

        return `
            <div class="column-manager">
                <div class="column-manager-header">
                    <h4>自定义列管理</h4>
                    <button class="btn btn-sm btn-secondary" id="close-column-manager">收起</button>
                </div>
                <div class="column-manager-body">
                    ${this._showAddForm ? this._renderAddForm() : ''}
                    ${columns.length === 0 && !this._showAddForm ? '<p class="text-muted" style="padding:8px">暂无自定义列，点击下方按钮添加</p>' : ''}
                    <table class="data-table column-table">
                        <thead><tr>
                            <th>列名称</th><th>字段标识</th><th>类型</th><th>必填</th><th style="width:120px">操作</th>
                        </tr></thead>
                        <tbody>
                            ${columns.map(col => this._renderRow(col, typeLabels)).join('')}
                        </tbody>
                    </table>
                    <div style="margin-top:10px">
                        <button class="btn btn-primary btn-sm" id="btn-add-column">+ 添加列</button>
                    </div>
                </div>
            </div>`;
    }

    _renderAddForm() {
        return `
            <div class="inline-form column-form" style="background:#f0f7ff;padding:12px;border-radius:6px;margin-bottom:10px">
                <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end">
                    <div class="form-field" style="margin-bottom:0"><label>列名称</label><input type="text" id="col-name" class="form-input" placeholder="如：测试版本" autofocus style="width:130px"></div>
                    <div class="form-field" style="margin-bottom:0"><label>字段标识</label><input type="text" id="col-field-key" class="form-input" placeholder="如：test_version" style="width:130px"></div>
                    <div class="form-field" style="margin-bottom:0"><label>类型</label>
                        <select id="col-type" class="form-select" style="width:100px">
                            <option value="text">文本</option>
                            <option value="number">数字</option>
                            <option value="select">下拉选项</option>
                        </select>
                    </div>
                    <div class="form-field" style="margin-bottom:0"><label>选项(逗号分隔)</label><input type="text" id="col-options" class="form-input" placeholder="仅 select 类型需要" style="width:150px"></div>
                    <div class="form-field" style="margin-bottom:0;display:flex;align-items:center;gap:4px;margin-top:18px">
                        <input type="checkbox" id="col-required"> <label for="col-required" style="margin:0;font-size:0.8rem">必填</label>
                    </div>
                    <div style="display:flex;gap:4px;padding-top:18px">
                        <button class="btn btn-primary btn-sm" id="confirm-add-column">添加</button>
                        <button class="btn btn-secondary btn-sm" id="cancel-add-column">取消</button>
                    </div>
                </div>
            </div>`;
    }

    _renderEditForm(col) {
        const optsStr = Array.isArray(col.options) ? col.options.join(', ') : (col.options || '');
        return `
            <tr class="editing-row">
                <td colspan="5">
                    <div class="inline-form column-form" style="background:#fffbe6;padding:10px;border-radius:4px">
                        <input type="hidden" id="edit-col-id" value="${col.id}">
                        <span style="font-weight:500">${escapeHtml(col.name)}</span>
                        <input type="text" id="edit-col-name" class="form-input" value="${escapeHtml(col.name)}" style="width:110px">
                        <select id="edit-col-type" class="form-select" style="width:90px">
                            <option value="text" ${col.column_type === 'text' ? 'selected' : ''}>文本</option>
                            <option value="number" ${col.column_type === 'number' ? 'selected' : ''}>数字</option>
                            <option value="select" ${col.column_type === 'select' ? 'selected' : ''}>下拉选项</option>
                        </select>
                        <input type="text" id="edit-col-options" class="form-input" value="${optsStr}" placeholder="选项" style="width:120px">
                        <label style="font-size:0.8rem"><input type="checkbox" id="edit-col-required" ${col.is_required ? 'checked' : ''}> 必填</label>
                        <button class="btn btn-primary btn-sm" id="confirm-edit-col">保存</button>
                        <button class="btn btn-secondary btn-sm" id="cancel-edit-col">取消</button>
                    </div>
                </td>
            </tr>`;
    }

    _renderRow(col, typeLabels) {
        if (this._editingId === col.id) return this._renderEditForm(col);
        const typeLabel = typeLabels[col.column_type] || col.column_type;
        return `
            <tr>
                <td><strong>${escapeHtml(col.name)}</strong></td>
                <td><code>${escapeHtml(col.field_key)}</code></td>
                <td><span class="type-badge type-${col.column_type}">${typeLabel}</span></td>
                <td>${col.is_required ? '<span style="color:#dc2626">是</span>' : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" id="edit-col-${col.id}">编辑</button>
                    <button class="btn btn-sm btn-danger" id="delete-col-${col.id}">删除</button>
                </td>
            </tr>`;
    }

    afterRender() {}
}
