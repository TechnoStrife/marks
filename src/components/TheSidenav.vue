<template>
    <header v-click-outside="close_all">
        <ul id="sidenav" class="sidenav sidenav-fixed">
            <the-sidenav-profile/>
            <li>
                <router-link to="/" class="waves-effect waves-teal">
                    <i class="material-icons">home</i>
                    <span>Главная</span>
                </router-link>
            </li>
            <SidenavFlyout v-for="(flyout, index) in flyouts"
                           :key="index"
                           :title="flyout.title"
                           :icon="flyout.icon"
                           :contents="flyout.contents"
                           :active="flyout.active"
                           @open="open_flyout(index)"/>
            <li>
                <router-link to="/tmp" class="waves-effect waves-teal">
                    <i class="material-icons">headset</i>
                    <span>Test</span>
                </router-link>
            </li>
        </ul>
    </header>
</template>

<script>
import TheSidenavProfile from "@/components/TheSidenavProfile"
import SidenavFlyout from "@/components/SidenavFlyout"
import {key_sorter, now} from '@/utils'
import ClickOutside from 'vue-click-outside'
import router from '@/router'
import {sorter_with_others_group} from "@/utils/marks"


function flyouts(data) {
    // let year = Math.max(...distinct(data.classes.map(class_ => class_.year)))
    // data.classes.filter(class_ => class_.year === year)
    let classes = {}
    for (let class_ of data.classes) {
        let num = parseInt(class_.name.slice(0, -1))
        if (!(num in classes))
            classes[num] = []
        classes[num].push(class_)
    }
    classes = Object.entries(classes).map(([num, classes]) => ({
        title: `${num}-е классы`,
        links: classes.map(class_ => ({
            text: `${class_.name} класс (${class_.year})`,
            href: `/class/${class_.id}/`,
        }))
    }))
    let subjects = {}
    for (let subject of data.subjects) {
        if (!(subject.type in subjects))
            subjects[subject.type] = []
        subjects[subject.type].push(subject)
    }
    subjects = Object.entries(subjects)
    subjects.sort(
        ([type1], [type2]) => sorter_with_others_group(type1, type2)
    )
    subjects = subjects.map(([type, subjects]) => ({
        title: type,
        links: subjects.sort(key_sorter(subject => subject.name)).map(subject => ({
            text: subject.name,
            href: `/subject/${subject.id}`
        }))
    }))
    let teachers = {'Остальные': []}
    for (let teacher of data.teachers) {
        teacher.lesson_types = teacher.lesson_types.split(',')
        if (teacher.lesson_types.includes('Прочее'))
            teacher.lesson_types.splice(teacher.lesson_types.indexOf('Прочее'), 1)
        if (teacher.lesson_types.length === 0)
            teachers['Остальные'].push(teacher)
        for (let lesson_type of teacher.lesson_types) {
            if (!(lesson_type in teachers))
                teachers[lesson_type] = []
            teachers[lesson_type].push(teacher)
        }
    }
    teachers = Object.entries(teachers).sort(([a], [b]) => sorter_with_others_group(a, b))
    teachers = teachers.map(([lesson_type, teachers]) => ({
        title: lesson_type,
        links: teachers.sort(key_sorter(teacher => teacher.full_name)).map(teacher => ({
            text: teacher.full_name,
            href: `/teacher/${teacher.id}/`,
        }))
    }))
    return [
        {
            title: 'Классы',
            icon: 'school',
            active: false,
            contents: classes
        },
        {
            title: 'Предметы',
            icon: 'subject',
            active: false,
            contents: subjects
        },
        {
            title: 'Учителя',
            icon: 'person',
            active: false,
            contents: teachers
        },
    ]
}

const open_time = 200

export default {
    name: "TheSidenav",
    data() {
        return {
            flyouts: flyouts(this.$store.state.sidenav),
            will_close_at: 0,
            will_open_at: 0,
            next_flyout_to_open: null,
        }
    },
    mounted() {
        router.beforeEach((to, from, next) => {
            this.close_all()
            next()
        })
        this.popupItem = this.$el
    },
    computed: {
        is_any_open() {
            return this.flyouts.some(flyout => flyout.active)
        },
        store_data() {
            return this.$store.state.sidenav
        },
    },
    methods: {
        is_opening_now() {
            return this.is_any_open
                && (this.will_open_at - open_time) < now() && now() < this.will_open_at
        },
        is_closing_now() {
            return !this.is_any_open
                && (this.will_close_at - open_time) < now() && now() < this.will_close_at
        },
        time_until_open() {
            return this.will_open_at - now()
        },
        time_to_reverse_opening() {
            return open_time - this.time_until_open()
        },
        activate_timeout(time) {
            setTimeout(this.after_close_func, time)
        },
        after_close_func() {
            if (this.next_flyout_to_open !== null) {
                this.flyouts[this.next_flyout_to_open].active = true
                this.next_flyout_to_open = null
                this.will_open_at = now() + open_time
            }
        },
        set_all_inactive() {
            for (let flyout of this.flyouts)
                if (flyout.active)
                    flyout.active = false
        },
        close_all() {
            if (this.is_opening_now()) {
                this.set_all_inactive()
                this.next_flyout_to_open = null
                this.will_close_at = this.time_to_reverse_opening()
            } else if (this.is_closing_now()) {
                // pass
            } else if (this.is_any_open) {
                this.set_all_inactive()
                this.next_flyout_to_open = null
                this.will_close_at = now() + open_time
                this.activate_timeout(open_time)
            } else {
                // pass
            }
        },
        open_flyout(flyout) {
            if (this.flyouts[flyout].active || this.next_flyout_to_open === flyout) {
                this.close_all()
                return
            }

            if (this.is_opening_now()) {
                this.set_all_inactive()
                this.next_flyout_to_open = flyout
                this.activate_timeout(this.time_to_reverse_opening())
            } else if (this.is_closing_now()) {
                this.next_flyout_to_open = flyout
            } else if (this.is_any_open) {
                this.close_all()
                this.next_flyout_to_open = flyout
            } else {
                this.flyouts[flyout].active = true
                this.next_flyout_to_open = null
                this.will_open_at = now() + this.open_time
            }
        }
    },
    components: {
        TheSidenavProfile,
        SidenavFlyout
    },
    directives: {
        ClickOutside
    }
}
</script>

<style lang="scss">
@import "~src/variables.scss";

#sidenav {
    color: $sidenav-text-color;
    overflow-y: visible;
    z-index: 500;

    li > a {
        padding: 0 16px;
    }

    > li:not(:first-child) {
        font-size: 14px;
        font-weight: 500;
    }

    > li.with-flyout {
        > a::after {
            font-family: 'Material Icons';
            content: "keyboard_arrow_left";
            color: $sidenav-text-color;
            font-size: 18px;
            position: absolute;
            right: 16px;
            transition: transform 200ms;
        }
    }

    > li.with-flyout.flyout-active {
        > a::after {
            transform: rotate(-180deg);
        }

        .sidenav-flyout {
            width: $sidenav-flyout-width;
        }
    }
}
</style>
