/**
 * 事件总线 — 组件间解耦通信。
 */
class EventBus {
    constructor() {
        this._events = new Map();
    }

    /**
     * 注册事件监听
     * @returns {Function} 取消订阅函数
     */
    on(event, callback) {
        if (!this._events.has(event)) {
            this._events.set(event, new Set());
        }
        this._events.get(event).add(callback);
        return () => this.off(event, callback);
    }

    /**
     * 移除事件监听
     */
    off(event, callback) {
        this._events.get(event)?.delete(callback);
    }

    /**
     * 触发事件
     */
    emit(event, data) {
        this._events.get(event)?.forEach(cb => {
            try {
                cb(data);
            } catch (e) {
                console.error(`[EventBus] Error in "${event}" handler:`, e);
            }
        });
    }

    /**
     * 只触发一次的事件监听
     */
    once(event, callback) {
        const wrapper = (data) => {
            this.off(event, wrapper);
            callback(data);
        };
        return this.on(event, wrapper);
    }
}

// 全局事件总线单例
const bus = new EventBus();
