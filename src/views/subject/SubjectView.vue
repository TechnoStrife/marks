<template>
    <div class="class-view row" v-if="data">
        <div class="side-desc col s12 m5 l4">
            <div class="row">
                <TheSubjectDescription :data="data"/>
            </div>
        </div>
        <div id="charts" class="col s12 m7 l8">
            <h5>Успеваемость</h5>
            <div class="row">
                <div class="col s12">
                    <TheSubjectChartClasses :data="data"/>
                    <TheSubjectChartTeachers :data="data" v-if="data.teachers.length > 1"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import TheSubjectDescription from "@/views/subject/TheSubjectDescription"
import {id_map} from "@/utils"
import TheSubjectChartClasses from "@/views/subject/TheSubjectChartClasses"
import TheSubjectChartTeachers from "@/views/subject/TheSubjectChartTeachers"

export default {
    name: "SubjectView",
    mixins: [BaseViewMixin],
    components: {
        TheSubjectChartClasses,
        TheSubjectDescription,
        TheSubjectChartTeachers,
    },
    data() {
        return {}
    },
    computed: {},
    methods: {
        transform_response(data) {
            let {marks, classes, teachers} = data
            classes = id_map(classes)
            teachers = id_map(teachers)
            for (let mark of marks) {
                mark.teacher = teachers[mark.teacher]
                mark.class = classes[mark.class]
            }
            data.marks = marks
            // data.terminal_marks = terminal_marks
            data.classes_map = classes
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
