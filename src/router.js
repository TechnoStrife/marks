import Vue from 'vue'
import Router from 'vue-router'
import HomeView from './views/HomeView.vue'
import ClassView from "@/views/class/ClassView"
import StudentView from "@/views/student/StudentView"
import SubjectView from "@/views/subject/SubjectView"
import TeacherView from "@/views/teacher/TeacherView"
import ClassesSummaryView from "@/views/summary/classes/ClassesSummaryView"
import SubjectsSummaryView from "@/views/summary/subjects/SubjectsSummaryView"
import TeachersSummaryView from "@/views/summary/teachers/TeachersSummaryView"

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
        {
            path: '/summary/classes',
            name: 'summary classes',
            component: ClassesSummaryView
        },
        {
            path: '/summary/subjects',
            name: 'summary subjects',
            component: SubjectsSummaryView
        },
        {
            path: '/summary/teachers',
            name: 'summary teachers',
            component: TeachersSummaryView
        },
    ]
})
// component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
