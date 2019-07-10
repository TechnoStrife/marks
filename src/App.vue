<template>
    <div id="app">
        <TheSidenav></TheSidenav>
        <main>
            <ThePreloader :active="preloader"
                          @preloader-ready="preloader_ready"/>
            <router-view @close-preloader="close_preloader"/>
        </main>
    </div>
</template>

<script>
import ThePreloader from "@/components/ThePreloader"
import TheSidenav from "@/components/TheSidenav"
import router from "@/router"
import {CallbackLock} from "@/utils/callback_lock"
import "materialize-css/sass/materialize.scss"
import "chart.js/dist/Chart.min.css"
import 'katex/dist/katex.css'
import "@/style.scss"

export default {
    name: 'app',
    data() {
        return {
            preloader: true,
            router_callback_lock: new CallbackLock(),
            preloader_close_lock: new CallbackLock(),
        }
    },
    mounted() {
        setTimeout(() => this.preloader_close_lock.unlock(), 250)
        router.beforeEach((to, from, next) => {
            this.preloader = true
            this.router_callback_lock.lock()
            this.preloader_close_lock.lock()
            next()
        })
        router.beforeResolve((to, from, next) => {
            this.router_callback_lock.call(next)
        })
    },
    methods: {
        preloader_ready() {
            this.router_callback_lock.unlock()
            this.preloader_close_lock.unlock()
        },
        close_preloader() {
            this.preloader_close_lock.call(() => this.preloader = false)
        },
    },
    components: {
        TheSidenav,
        ThePreloader
    }
}
</script>
