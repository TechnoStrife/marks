<template>
    <router-view/>
</template>
<script>
    export default {
        name: 'app',
    }
</script>
<style lang="scss">
    @import "~src/variables.scss";

    main {
        background-color: $content-bg-color;
        padding-left: $sidenav-width;
    }

    .collapsible-header {
        outline: none
    }

    a[tabindex="-1"], a.waves-effect {
        outline: none;
    }

    /*.collapsible-body li a {
        padding-left: 48px !important
    }*/
</style>
