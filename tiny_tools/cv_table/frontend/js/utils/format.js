/**
 * 格式化工具函数
 */

/**
 * 格式化日期时间
 */
function formatDateTime(isoStr) {
    if (!isoStr) return '-';
    const d = new Date(isoStr);
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/**
 * 获取状态标签（配置化）
 */
function getStatusLabel(status) {
    const config = appStore.state.statusConfig;
    const item = config.find(s => s.value === status);
    return item ? item.label : status;
}

/**
 * 获取状态颜色
 */
function getStatusColor(status) {
    const config = appStore.state.statusConfig;
    const item = config.find(s => s.value === status);
    return item ? item.color : '#9ca3af';
}

/**
 * 获取优先级标签
 */
function getPriorityLabel(priority) {
    const config = appStore.state.priorityConfig;
    const item = config.find(p => p.value === priority);
    return item ? item.label : priority;
}

/**
 * 获取优先级颜色
 */
function getPriorityColor(priority) {
    const config = appStore.state.priorityConfig;
    const item = config.find(p => p.value === priority);
    return item ? item.color : '#6b7280';
}
