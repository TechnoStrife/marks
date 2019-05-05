<template>
    <li class="with-flyout" :class="{'flyout-active': active}">
        <a class="waves-effect waves-teal" @click="$emit('open')">
            <i class="material-icons">{{ icon }}</i>
            <span>{{ title }}</span>
        </a>
        <div class="sidenav-flyout">
            <h5>{{ title }}</h5>
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
    export default {
        name: "SidenavFlyout",
        props: {
            icon: String,
            title: String,
            contents: Array,
            active: Boolean,
        },
        data() {
            return {
                collapsible: null
            }
        },
        mounted() {
            this.collapsible = M.Collapsible.init(this.$refs.collapsible, {
                accordion: true
            });
        },
        watch: {
            active(val) {
                if (val === false) {
                    this.collapsible.close()
                }
            }
        }
    }
</script>

<style lang="scss">
    @import "~src/variables.scss";

    .sidenav-flyout {
        color: $sidenav-flyout-text-color;
        position: fixed;
        overflow: hidden;
        left: $sidenav-width;
        top: 0;
        width: 0;
        transition: width 200ms ease-in-out;
        height: 100vh;
        background-color: $sidenav-flyout-bg-color;

        h5 {
            text-align: center;
        }

        > * {
            width: $sidenav-flyout-width;
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
