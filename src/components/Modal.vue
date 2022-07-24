<template>
    <transition name="modal">
        <div id="modal" class="scroll hide-scroll-on-s row" v-if="opened" @click="close">
            <div class="modal-content-wrapper col" :class="size">
                <div class="card-panel" @mousedown="prevent = true" @mouseup="prevent = true">
                    <slot></slot>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
// import ClickOutside from 'vue-click-outside'
// directives: {
//     ClickOutside
// },

export default {
    name: "Modal",
    model: {
        prop: 'opened',
        event: 'close'
    },
    components: {},
    props: {
        opened: {
            type: Boolean,
            required: false,
        },
        small: {
            type: Boolean,
            default: false,
        }
    },
    data() {
        return {
            prevent: false
        }
    },
    computed: {
        size() {
            const classes = classes => Object.fromEntries(
                classes.split(' ').map(x => [x, true])
            )
            if (this.small)
                return classes('s10 push-s1 m6 push-m3 l4 push-l4')
            else
                return classes('s12 m10 push-m1 l8 push-l2')
        }
    },
    methods: {
        close(event) {
            if (this.opened && !this.prevent)
                this.$emit('close')
            this.prevent = false
        },
    },
}
</script>

<style lang="scss">
@import "~src/variables.scss";

#modal {
    z-index: 1000;
    position: fixed;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;

    margin: 0;
    opacity: 1;
    background: #0005;
    transition: opacity 0.3s;
    overflow-x: hidden;
    overflow-y: scroll;

    .modal-content-wrapper {
        position: relative;
        padding: 100px 0;
        top: 0;
        transition: top 0.5s;
    }

    &.modal-enter, &.modal-leave-to {
        opacity: 0;

        .modal-content-wrapper {
            top: 50px;
        }
    }
}
</style>
