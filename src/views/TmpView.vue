<template>
    <div class="tmp">
        <h3 class="center">Ad majorem Dei gloriam</h3>
        <p><i class="material-icons">crop_rotate</i>crop_rotate</p>
        <p><i class="material-icons">dashboard</i>dashboard</p>
        <p><i class="material-icons">data_usage</i>data_usage</p>
        <p><i class="material-icons">developer_board</i>developer_board</p>
        <p><i class="material-icons">details</i>details</p>
        <p><i class="material-icons">equalizer</i>equalizer</p>
        <p><i class="material-icons">error</i>error</p>
        <p><i class="material-icons">error_outline</i>error_outline</p>
        <p><i class="material-icons">insert_chart</i>insert_chart</p>
        <p><i class="material-icons">memory</i>memory</p>
        <p><i class="material-icons">loop</i>loop</p>
        <p><i class="material-icons">school</i>school</p>
        <p><i class="material-icons">schedule</i>schedule</p>
        <p><i class="material-icons">settings</i>settings</p>
        <p><i class="material-icons">show_chart</i>show_chart</p>
        <p><i class="material-icons">storage</i>storage</p>
        <p><i class="material-icons">subject</i>subject</p>
        <p><i class="material-icons">swap_calls</i>swap_calls</p>
        <p><i class="material-icons">transform</i>transform</p>
        <p><i class="material-icons">trending_down</i>trending_down</p>
        <p><i class="material-icons">trending_flat</i>trending_flat</p>
        <p><i class="material-icons">trending_up</i>trending_up</p>
        <p><i class="material-icons">3d_rotation</i>3d_rotation</p>
    </div>
</template>

<script>
export default {
    name: "Tmp",
    beforeRouteEnter(to, from, next) {
        next(vm => vm.$emit('close-preloader'))
    },
    beforeRouteUpdate(to, from, next) {
        this.$emit('close-preloader')
        next()
    },
}
</script>

<style lang="scss">
.tmp {

}
</style>
