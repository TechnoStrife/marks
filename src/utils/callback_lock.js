export class CallbackLock {
    constructor(locked = true) {
        this.locked = locked
        this._callback = null
    }

    lock() {
        this.locked = true
    }

    unlock() {
        if (typeof this._callback === "function") {
            this._callback()
            this._callback = null
        }
        this.locked = false
    }

    call(cb) {
        if (this.locked) {
            this._callback = cb
        } else {
            cb()
        }
    }
}
