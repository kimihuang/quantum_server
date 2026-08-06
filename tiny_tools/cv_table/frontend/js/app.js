/**
 * App — 树形视图入口
 */
(function () {
    'use strict';

    let treeView;
    let modal;

    async function init() {
        // 创建组件
        treeView = new TreeView('#tree-container');
        modal = new Modal('#modal-container');

        // 加载初始数据
        await treeView.refreshAll();

        // 导入处理
        document.getElementById('import-file-input')?.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                const result = await API.importCSV(file);
                showToast(`导入完成: 成功 ${result.created} 条，跳过 ${result.skipped} 条`, 'success');
                await treeView.refreshAll();
            } catch (e) {
                showToast('导入失败: ' + e.message, 'error');
            } finally {
                e.target.value = '';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();
