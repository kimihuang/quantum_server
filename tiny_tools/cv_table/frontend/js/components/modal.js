/**
 * Modal — 通用弹窗组件。
 */
class Modal extends Component {
    constructor(container) {
        super(container);
        this._onClose = null;

        // 点击遮罩关闭
        this.listen('modal:open', () => this.render());
        this.listen('modal:close', () => this.close());
    }

    template() {
        const { title, body } = appStore.state.modal;
        if (!appStore.state.modal.open) return '';

        return `
            <div class="modal-overlay" id="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${escapeHtml(title || '')}</h3>
                        <button class="modal-close" id="modal-close-btn">&times;</button>
                    </div>
                    <div class="modal-body">${body || ''}</div>
                    <div class="modal-footer" id="modal-footer"></div>
                </div>
            </div>
        `;
    }

    afterRender() {
        const overlay = document.getElementById('modal-overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) this.close();
            });
        }

        const closeBtn = document.getElementById('modal-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // 如果设置了确认回调，添加按钮（先清空防止重复）
        const footer = document.getElementById('modal-footer');
        const { onConfirm, confirmText, cancelText } = appStore.state.modal;

        if (footer) footer.innerHTML = '';

        if (onConfirm && footer) {
            const cancelBtn = createElement('button', {
                className: 'btn btn-secondary',
                onClick: () => this.close(),
            }, [cancelText || '取消']);
            const confirmBtn = createElement('button', {
                className: 'btn btn-primary',
                onClick: async () => {
                    try {
                        confirmBtn.disabled = true;
                        confirmBtn.textContent = '处理中...';
                        await onConfirm();
                        this.close();
                    } catch (e) {
                        confirmBtn.disabled = false;
                        confirmBtn.textContent = confirmText || '确认';
                        showToast(e.message || '操作失败', 'error');
                    }
                },
            }, [confirmText || '确认']);

            footer.appendChild(cancelBtn);
            footer.appendChild(confirmBtn);
        }
    }

    close() {
        appStore.state.modal = { open: false, title: '', body: '', onConfirm: null };
        bus.emit('modal:close');
        this.render();
    }

    /**
     * 打开确认弹窗
     */
    static confirm(title, body, onConfirm, options = {}) {
        appStore.state.modal = {
            open: true,
            title,
            body,
            onConfirm,
            confirmText: options.confirmText || '确认',
            cancelText: options.cancelText || '取消',
        };
        bus.emit('modal:open');
    }

    /**
     * 打开信息弹窗
     */
    static show(title, body) {
        appStore.state.modal = {
            open: true,
            title,
            body,
            onConfirm: null,
        };
        bus.emit('modal:open');
    }
}
