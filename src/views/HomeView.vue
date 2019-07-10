<template>
    <div>
        <h3 class="center">Ad majorem Dei gloriam</h3>

    </div>
</template>

<script>

export default {
    components: {},
    beforeRouteEnter(to, from, next) {
        next(vm => vm.$emit('close-preloader'))
    },
    beforeRouteUpdate(to, from, next) {
        this.$emit('close-preloader')
        next()
    },
}
</script>
