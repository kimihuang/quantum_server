/**
 * 组件基类 — 提供统一的组件生命周期管理。
 * 子类需要覆写: template() / afterRender() / destroy()
 */
class Component {
    /**
     * @param {HTMLElement|string} container - 容器元素或选择器
     * @param {Object} [props={}] - 组件属性
     */
    constructor(container, props = {}) {
        if (typeof container === 'string') {
            this.container = $(container);
        } else {
            this.container = container;
        }

        if (!this.container) {
            throw new Error(`Component: 容器不存在`);
        }

        this.props = props;
        this.state = {};
        this._subscriptions = [];
    }

    /**
     * 订阅 Store 变化
     */
    watch(key, callback) {
        const unsub = appStore.on(key, callback);
        this._subscriptions.push(unsub);
        return unsub;
    }

    /**
     * 订阅事件总线
     */
    listen(event, callback) {
        const unsub = bus.on(event, callback);
        this._subscriptions.push(unsub);
        return unsub;
    }

    /**
     * 触发事件
     */
    emit(event, data) {
        bus.emit(event, data);
    }

    /**
     * 设置组件状态并重新渲染
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    /**
     * 渲染组件
     */
    render() {
        this.container.innerHTML = this.template();
        this.afterRender();
    }

    /**
     * 返回 HTML 模板字符串（子类覆写）
     */
    template() {
        return '';
    }

    /**
     * 渲染后绑定事件（子类覆写）
     */
    afterRender() {
    }

    /**
     * 销毁组件，清理监听
     */
    destroy() {
        this._subscriptions.forEach(fn => fn());
        this._subscriptions = [];
        this.container.innerHTML = '';
    }
}
