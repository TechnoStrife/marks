<template>
    <transition name="preloader" @after-enter="$emit('preloader-ready')">
        <div id="preloader" v-if="active"/>
    </transition>
</template>

<script>
export default {
    name: "ThePreloader",
    props: {
        active: Boolean,
    },
    data() {
        return {}
    },
}
</script>

<style lang="scss">
@import "~src/variables.scss";

#preloader {
    height: 100vh;
    position: fixed;
    z-index: $preloader-zindex;
    top: 0;
    left: 0;
    right: 0;
    /*opacity: 1;*/
    /*transition: opacity 0.5s;*/
    pointer-events: none;
    background: #eee;

    @media #{$large-and-up} {
        & {
            left: $sidenav-width;
        }
    }

    &::before {
        position: absolute;
        content: "";
        z-index: $preloader-zindex - 1;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("~src/assets/preloader.svg") center center no-repeat;
    }
}

.preloader-enter-active, .preloader-leave-active {
    transition: opacity .5s;
}

.preloader-enter, .preloader-leave-to {
    opacity: 0;
}

</style>
