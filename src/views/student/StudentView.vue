<template>
    <div class="student-view row" v-if="data">
        <div id="desc" class="col s12 m5 l4">
            <h5>{{ data.full_name }}</h5>
            <NoteField :note="data.info"/>
            <TheStudentDescription :student="data"/>
            <TheStudentAcademicPerformance :data="data"/>
        </div>
        <div id="charts" class="col s12 m7 l8">
            <h5>Успеваемость</h5>
            <TheStudentChartSubject :data="data"/>
            <TheStudentChartPeriod :data="data"/>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import NoteField from "@/components/NoteField"
import PersonDescription from "@/components/PersonDescription"
import {id_map} from "@/utils"
import ChartCard1bar from "@/charts/ChartCard1bar"
import TheStudentChartSubject from "@/views/student/TheStudentChartSubject"
import TheStudentChartPeriod from "@/views/student/TheStudentChartPeriod"
import TheStudentAcademicPerformance from "@/views/student/TheStudentAcademicPerformance"
import TheStudentDescription from "@/views/student/TheStudentDescription"


export default {
    name: "StudentView",
    components: {
        TheStudentAcademicPerformance,
        TheStudentChartPeriod,
        TheStudentChartSubject,
        ChartCard1bar,
        TheStudentDescription,
        PersonDescription,
        NoteField
    },
    mixins: [BaseViewMixin],
    data() {
        return {}
    },
    computed: {},
    methods: {
        transform_response(data) {
            let student = {...data}
            delete student.marks
            let {marks, semester_marks, terminal_marks, subjects, teachers, periods} = data.marks
            let all_classes = [data.class, ...data.previous_classes]
            for (let class_ of all_classes) {
                class_.num = parseInt(class_.name.slice(0, -1))
                class_.periods = [...Array(class_.periods_count).keys()].map(x => ({
                    num: x + 1,
                    year: class_.year,
                }))
            }
            let classes = id_map(all_classes)
            subjects = id_map(subjects)
            teachers = id_map(teachers)
            periods = id_map(periods)
            for (let mark of marks) {
                mark.student = student
                mark.class = classes[mark.lesson_info.class]
                mark.subject = subjects[mark.lesson_info.subject]
                mark.teacher = teachers[mark.lesson_info.teacher]
                mark.period = periods[mark.period]
                delete mark.lesson_info
            }
            for (let mark of semester_marks) {
                mark.student = student
                mark.class = classes[mark.lesson_info.class]
                mark.subject = subjects[mark.lesson_info.subject]
                mark.teacher = teachers[mark.lesson_info.teacher]
                mark.period = periods[mark.period]
                delete mark.lesson_info
            }
            for (let mark of terminal_marks) {
                mark.student = student
                mark.class = classes[mark.lesson_info.class]
                mark.subject = subjects[mark.lesson_info.subject]
                mark.teacher = teachers[mark.lesson_info.teacher]
                delete mark.lesson_info
            }
            data.marks = {marks, semester_marks, terminal_marks, subjects, teachers, periods}
            return data
        }
    },
}
</script>

<style lang="scss">
.student-view {

}
</style>
