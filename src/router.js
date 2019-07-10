import Vue from 'vue'
import Router from 'vue-router'
import HomeView from './views/HomeView.vue'
import TmpView from "@/views/TmpView"
import ClassView from "@/views/class/ClassView"
import StudentView from "@/views/student/StudentView"
import SubjectView from "@/views/subject/SubjectView"
import TeacherView from "@/views/teacher/TeacherView"

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/tmp',
            name: 'tmp',
            component: TmpView
        },
        {
            path: '/class/:id',
            name: 'class',
            component: ClassView
        },
        {
            path: '/student/:id',
            name: 'student',
            component: StudentView
        },
        {
            path: '/subject/:id',
            name: 'subject',
            component: SubjectView
        },
        {
            path: '/teacher/:id',
            name: 'teacher',
            component: TeacherView
        },
    ]
})
// component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
