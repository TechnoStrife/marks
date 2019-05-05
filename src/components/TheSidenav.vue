<template>
    <header tabindex="-1" @focusout="close_all">
        <ul id="sidenav" class="sidenav sidenav-fixed">
            <the-sidenav-profile/>
            <li>
                <router-link to="/" class="waves-effect waves-teal" tabindex="-1">
                    <i class="material-icons">home</i>
                    <span>Главная</span>
                </router-link>
            </li>
            <sidenav-flyout v-for="(flyout, index) in flyouts"
                            :key="index"
                            :title="flyout.title"
                            :icon="flyout.icon"
                            :contents="flyout.contents"
                            :active="flyout.active"
                            @open="open_flyout(index)"/>
            <!--<li class="with-flyout">
                <a class="waves-effect waves-teal">
                    <i class="material-icons">school</i>
                    <span>Классы</span>
                </a>
                <div class="sidenav-flyout">
                    <ul>
                        <li><h5>Классы</h5></li>
                        <li>
                            <ul class="collapsible">
                                <li>
                                    <div class="collapsible-header waves-effect waves-light">2-е классы</div>
                                    <div class="collapsible-body">
                                        <ul>
                                            <li class="waves-effect waves-light">2А класс</li>
                                            <li class="waves-effect waves-light">2Б класс</li>
                                            <li class="waves-effect waves-light">2В класс</li>
                                        </ul>
                                    </div>
                                </li>
                                <li>
                                    <div class="collapsible-header waves-effect waves-light">3-е классы</div>
                                    <div class="collapsible-body">
                                        <ul>
                                            <li class="waves-effect waves-light">3А класс</li>
                                            <li class="waves-effect waves-light">3Б класс</li>
                                            <li class="waves-effect waves-light">3В класс</li>
                                        </ul>
                                    </div>
                                </li>
                                <li>
                                    <div class="collapsible-header waves-effect waves-light">4-е классы</div>
                                    <div class="collapsible-body">
                                        <ul>
                                            <li class="waves-effect waves-light">4А класс</li>
                                            <li class="waves-effect waves-light">4Б класс</li>
                                            <li class="waves-effect waves-light">4В класс</li>
                                        </ul>
                                    </div>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </li>
            <li class="with-flyout">
                <a class="waves-effect waves-teal">
                    <i class="material-icons">subject</i>
                    <span>Предметы</span>
                </a>
                <div class="sidenav-flyout">
                    <ul>
                        <li><h5>Предметы</h5></li>
                        <li>Физика</li>
                        <li>Русский</li>
                        <li>Математика</li>
                    </ul>
                </div>
            </li>
            <li class="with-flyout">
                <a class="waves-effect waves-teal">
                    <i class="material-icons">person</i>
                    <span>Учителя</span>
                </a>
                <div class="sidenav-flyout">
                    <ul>
                        <li><h5>Учителя</h5></li>
                        <li>Иванов</li>
                        <li>Петров</li>
                        <li>Сидоров</li>
                    </ul>
                </div>
            </li>-->
        </ul>
    </header>
</template>

<script>
    import TheSidenavProfile from "@/components/TheSidenavProfile"
    import SidenavFlyout from "@/components/SidenavFlyout"
    import {now} from '@/utils'

    let flyouts = [
        {
            title: 'Классы',
            icon: 'school',
            active: false,
            contents: [
                {
                    title: '2-е классы',
                    links: [
                        {text: '2А класс', href: '#'},
                        {text: '2Б класс', href: '#'},
                        {text: '2В класс', href: '#'},
                    ]
                },
                {
                    title: '3-е классы',
                    links: [
                        {text: '3А класс', href: '#'},
                        {text: '3Б класс', href: '#'},
                        {text: '3В класс', href: '#'},
                    ]
                },
                {
                    title: '4-е классы',
                    links: [
                        {text: '4А класс', href: '#'},
                        {text: '4Б класс', href: '#'},
                        {text: '4В класс', href: '#'},
                    ]
                },
            ]
        },
        {
            title: 'Предметы',
            icon: 'subject',
            active: false,
            contents: [
                {
                    title: 'Естествознание',
                    links: [
                        {text: 'Физика', href: '#'},
                    ]
                }
            ]
        },
        {
            title: 'Учителя',
            icon: 'person',
            active: false,
            contents: [
                {
                    title: 'Естествознание',
                    links: [
                        {text: 'Арджанов А.С.', href: '#'},
                    ]
                }
            ]
        },
    ]
    const open_time = 200

    export default {
        name: "TheSidenav",
        data() {
            return {
                flyouts,
                will_close_at: 0,
                will_open_at: 0,
                next_flyout_to_open: null,
            }
        },
        computed: {
            is_any_open() {
                return this.flyouts.some(flyout => flyout.active)
            }
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
                return this.will_open_at - now();
            },
            time_to_reverse_opening() {
                return open_time - this.time_until_open();
            },
            activate_timeout(time) {
                setTimeout(this.after_close_func, time);
            },
            after_close_func() {
                if (this.next_flyout_to_open !== null) {
                    this.flyouts[this.next_flyout_to_open].active = true
                    this.next_flyout_to_open = null
                    this.will_open_at = now() + open_time
                }
            },
            set_all_inactive() {
                for (let flyout of flyouts)
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
