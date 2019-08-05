<template>
    <div id="teachers-summary-view" class="summary-view row" v-if="data">
        <div class="col s12 m10 push-m1 l8 push-l2">
            <div class="row">
                <h5 class="center">Сводка по предметам</h5>
            </div>
            <div class="row" v-for="group of grouped_data">
                <TeachersSummaryChart :data="group.data" :group_name="group.name"/>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import {key_sorter} from "@/utils"
import {sorter_with_others_group} from "@/utils/marks"
import {mapState} from "vuex"
import TeachersSummaryChart from "@/views/summary/teachers/TeachersSummaryChart"


export default {
    name: "TeachersSummaryView",
    components: {
        TeachersSummaryChart
    },
    mixins: [BaseViewMixin],
    data() {
        return {}
    },
    computed: {
        ...mapState(['sidenav']),
        grouped_data() {
            let teachers = {'Остальные': []}
            for (let teacher_marks of this.data) {
                if (teacher_marks.teacher.types.length === 0) {
                    teachers['Остальные'].push(teacher_marks)
                    continue
                }
                for (let type of teacher_marks.teacher.types) {
                    if (!(type in teachers))
                        teachers[type] = []
                    teachers[type].push(teacher_marks)
                }
            }
            teachers = Object.entries(teachers)
            teachers.sort(
                ([type1], [type2]) => sorter_with_others_group(type1, type2)
            )
            return teachers.map(([type, teachers]) => ({
                name: type,
                data: teachers.sort(key_sorter(teacher_marks => teacher_marks.teacher.full_name))
            }))
        }
    },
    methods: {
        transform_response(data) {
            let res = data.results
            let lesson_types = Object.fromEntries(this.sidenav.teachers.map(
                teacher => [teacher.id, teacher.lesson_types]
            ))
            for (let teacher_marks of res) {
                teacher_marks.teacher.types = lesson_types[teacher_marks.teacher.id]
            }
            return res
        }
    },
}
</script>

<style lang="scss">
#teachers-summary-view {
    > .col > .row {
        margin-bottom: 0;
    }
}
</style>
