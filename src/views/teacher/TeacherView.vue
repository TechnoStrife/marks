<template>
    <div class="teacher-view row" v-if="data">
        <div class="side-desc col s12 m5 l4">
            <h5>{{ data.full_name }}</h5>
            <NoteField :note="data.info"/>
            <div class="row">
                <TheTeacherDescription :teacher="data"/>
            </div>
        </div>
        <div id="charts" class="col s12 m7 l8">
            <h5>Успеваемость</h5>
            <div class="row">
                <div class="col s12">
                    <TheTeacherChartClasses :data="data"/>
                    <TheTeacherChartSubjects :data="data"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import TheTeacherDescription from "@/views/teacher/TheTeacherDescription"
import NoteField from "@/components/NoteField"
import {id_map} from "@/utils"
import TheTeacherChartClasses from "@/views/teacher/TheTeacherChartClasses"
import TheTeacherChartSubjects from "@/views/teacher/TheTeacherChartSubjects"

export default {
    name: "TeacherView",
    mixins: [BaseViewMixin],
    components: {
        TheTeacherChartSubjects,
        TheTeacherChartClasses,
        TheTeacherDescription,
        NoteField,
    },
    data() {
        return {}
    },
    computed: {},
    methods: {
        transform_response(data) {
            let {marks, classes, subjects} = data
            classes = id_map(classes)
            subjects = id_map(subjects)
            for (let mark of marks) {
                mark.subject = subjects[mark.subject]
                mark.class = classes[mark.class]
            }
            data.marks = marks
            // data.terminal_marks = terminal_marks
            data.classes_map = classes
            data.subjects_map = subjects
            return data
        }
    },
}
</script>

<style lang="scss">
.class-view {

}
</style>
