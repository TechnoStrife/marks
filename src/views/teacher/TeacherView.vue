<template>
    <div class="teacher-view row" v-if="data">
        <div class="side-desc col s12 m5 l4">
            <h5>{{ data.full_name }}</h5>
            <NoteField :note="data.info"/>
            <div class="row">
                <TheTeacherDescription :teacher="data"/>
            </div>
        </div>
        <div class="col s12 m7 l8">
            <div class="row">
                <div class="col s12">
                    Charts here
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import TheTeacherDescription from "@/views/teacher/TheTeacherDescription"
import NoteField from "@/components/NoteField"

export default {
    name: "TeacherView",
    mixins: [BaseViewMixin],
    components: {
        TheTeacherDescription,
        NoteField,
    },
    data() {
        return {}
    },
    computed: {},
    methods: {},
}
</script>

<style lang="scss">
.class-view {

}
</style>
