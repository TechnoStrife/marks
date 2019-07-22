<template>
    <div class="class-view row" v-if="data">
        <div class="side-desc col s12 m5 l4">
            <div class="row">
                <TheClassDescription :data="data"/>
            </div>
        </div>
        <div id="charts" class="col s12 m7 l8">
            <h5>Успеваемость</h5>
            <div class="row">
                <div class="col s12">
                    <TheClassChartStudents :data="data"/>
                    <TheClassChartSubjects :data="data"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import TheClassDescription from "@/views/class/TheClassDescription"
import {id_map} from "@/utils"
import TheClassChartStudents from "@/views/class/TheClassChartStudents"
import TheClassChartSubjects from "@/views/class/TheClassChartSubjects"

export default {
    name: "ClassView",
    mixins: [BaseViewMixin],
    components: {
        TheClassChartSubjects,
        TheClassChartStudents,
        TheClassDescription,
    },
    data() {
        return {}
    },
    computed: {},
    methods: {
        transform_response(data) {
            let {marks, subjects, students, teachers} = data
            subjects = id_map(subjects)
            students = id_map(students)
            teachers = id_map(teachers)
            for (let mark of marks) {
                mark.student = students[mark.student]
                mark.subject = subjects[mark.subject]
                mark.teacher = teachers[mark.teacher]
            }
            data.marks = marks
            data.subjects_map = subjects
            data.students_map = students
            data.teachers_map = teachers
            return data
        }
    },
}
</script>

<style lang="scss">
.class-view {

}
</style>
