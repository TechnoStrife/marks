<template>
    <li class="with-flyout" :class="{'flyout-active': active}">
        <a class="waves-effect waves-teal" @click="$emit('open')">
            <i class="material-icons">{{ icon }}</i>
            <span>{{ title }}</span>
        </a>
        <div class="sidenav-flyout">
            <!--<scrolly>
                <scrolly-viewport>
                </scrolly-viewport>
                <scrolly-bar axis="y"></scrolly-bar>
            </scrolly>-->
            <h5>{{ title }}</h5>
            <router-link :to="summary.link" v-if="summary">{{ summary.text }}</router-link>
            <ul class="collapsible" ref="collapsible">
                <li v-for="group in contents">
                    <div class="collapsible-header waves-effect waves-light">
                        {{ group.title }}
                    </div>
                    <div class="collapsible-body">
                        <ul>
                            <li class="waves-effect waves-light" v-for="link in group.links">
                                <router-link :to="link.href">
                                    {{ link.text }}
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
        </div>
    </li>
</template>

<script>
import {Collapsible} from "materialize-css"


export default {
    name: "SidenavFlyout",
    props: {
        icon: String,
        title: String,
        contents: Array,
        summary: {
            type: Object,
            required: false,
            validator: summary => typeof summary.text === 'string'
                && typeof summary.link === 'string'
        },
        active: Boolean,
    },
    data() {
        return {
            // collapsible: null
        }
    },
    mounted() {
        this.collapsible = Collapsible.init(this.$refs.collapsible, {
            accordion: true
        })
    },
    watch: {
        active(val) {
            if (val === false) {
                // this.collapsible.close(
                //     Array.from(this.collapsible.el.children).findIndex(
                //         x => x.classList.contains('active')
                //     ) // thanks materialize
                // )
            }
        }
    },
}
</script>

<style lang="scss">
@import "~src/variables.scss";

.sidenav-flyout {
    position: fixed;
    overflow-x: hidden;
    overflow-y: scroll;
    left: $sidenav-width;
    top: 0;
    width: 0;
    transition: width 200ms ease-in-out;
    height: 100vh;
    background-color: $sidenav-flyout-bg-color;

    color: $sidenav-flyout-text-color;
    a {
        color: $sidenav-flyout-text-color;
    }

    -ms-overflow-style: none; // IE 10+
    scrollbar-width: none; // Firefox
    &::-webkit-scrollbar { // webkit
        width: 0;
    }

    /*.scrolly {
        height: 100vh;
    }*/

    h5 {
        text-align: center;
    }

    > * {
        width: $sidenav-flyout-width;
    }

    > a {
        display: block;
        padding: 0 16px;
        &:hover {
            transition: background-color .3s ease-out;
            background-color: rgba(0, 0, 0, 0.05);
        }
    }

    li {
        display: list-item;

        .collapsible-header::after {
            //noinspection CssNoGenericFontName
            font-family: 'Material Icons';
            content: "keyboard_arrow_left";
            color: $sidenav-flyout-text-color;
            font-size: 18px;
            position: absolute;
            right: 16px;
            transition: transform 200ms;
        }

        &.active .collapsible-header::after {
            transform: rotate(-90deg);
        }

        .collapsible-body {
            background-color: $sidenav-flyout-collapsible-bg-color;

            li {
                padding-left: 32px;
                padding-right: 32px;

                &:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }

                a {
                    background-color: transparent;
                    color: $sidenav-flyout-text-color;
                    padding: 0 !important;
                }
            }
        }
    }
}
</style>
