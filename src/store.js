import Vue from 'vue'
import Vuex from 'vuex'
import {expand_path} from "@/utils"

Vue.use(Vuex)


const state = {
    user: null,
    sidenav: null,
}

const actions = {}

const mutations = {
    SET_USER: 'Set user',
    SET_USER_LOGGED_IN: 'Set user is logged in',
    LOGOUT: 'Log out user',
    SET_SIDENAV_DATA: 'Set sidenav data'
}

const getters = {}

const modules = {}

export const store = expand_path(null, {
    actions,
    mutations,
    getters,
    state: Object.keys(state),

    ...modules
})

export default new Vuex.Store({
    modules: modules,
    state: state,
    mutations: {
        [mutations.SET_USER](state, user) {
            state.user = user
            localStorage.setItem('user', '1')
        },
        [mutations.SET_USER_LOGGED_IN](state) {
            state.user = true
            localStorage.setItem('user', '1')
        },
        [mutations.LOGOUT](state) {
            state.user = null
            localStorage.removeItem('user')
        },
        [mutations.SET_SIDENAV_DATA](state, data) {
            state.sidenav = data
        }
    },
});
