import Vue from 'vue'
import VueKatex from 'vue-katex/dist/vue-katex.min'
import Chart from 'chart.js'
import * as LosslessJSON from 'lossless-json'
import router from './router'
import store, {store as store_scheme} from './store'
import App from '@/App'
import {transform_value} from "@/api"
// import 'global-components/MaterialSelect'

Chart.platform.disableCSSInjection = true
Chart.plugins.register(require('chartjs-plugin-annotation'))


Vue.use(VueKatex)
Vue.config.productionTip = false

new Vue({
    el: '#app',
    router,
    store,
    render: h => h(App),
    beforeMount() {
        let data = LosslessJSON.parse(this.$el.dataset.sidenav, transform_value)
        this.$store.commit(store_scheme.mutations.SET_SIDENAV_DATA, data)
    }
})
