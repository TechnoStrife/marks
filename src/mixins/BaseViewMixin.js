import {Api} from "@/api"
import {CallbackLock} from "@/utils/callback_lock"

export default {
    name: "BaseViewMixin",
    data() {
        return {
            api: new Api(this.transform_response),
            preloader_lock: new CallbackLock(),
        }
    },
    computed: {
        data() {
            return this.api.res && this.api.res.data
        },
    },
    methods: {
        get_initial_api_url(to) {
            if (to === undefined)
                return this.$route.fullPath
            else
                return to.fullPath
        },
        transform_response(data) {
            return data
        }
    },
    beforeRouteEnter(to, from, next) {
        let api = new Api()
        let preloader_lock = new CallbackLock()
        api.request(to.fullPath).then(
            () => preloader_lock.unlock()
        )
        next(vm => {
            api.transform_response = vm.api.transform_response
            if (api.res && api.res.data)
                api.res.data = api.transform_response(api.res.data)
            vm.api = api
            preloader_lock.call(
                () => vm.$emit('close-preloader')
            )
        })
    },
    beforeRouteUpdate(to, from, next) {
        this.api.request(this.get_initial_api_url(to)).then(
            () => this.$emit('close-preloader')
        )
        next()
    },
}
