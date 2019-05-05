import Vue from 'vue'
import App from '@/App'
import router from './router'
import store from './store'
import TheSidenav from '@/components/TheSidenav'

Vue.config.productionTip = false

new Vue({
    el: '#app',
    router,
    store,
    // render: h => h(App),
    components: {
        App,
        TheSidenav
    }
})
