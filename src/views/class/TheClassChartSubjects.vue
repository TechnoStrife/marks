<template>
    <div id="class-chart-subjects">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="selected_student"
                @chart-click="console.log(arguments)"
            >
                <h6>Средняя оценка по ученику</h6>
                <katex-element :expression="'\\langle X \\rangle = ' + total_avg"/>
                <template v-slot:filters>
                    <div class="chart-filter left">
                        <div class="filter-title">Ученик:</div>
                        <RangeSelect
                            v-model="selected_student_index"
                            :range="all_students"
                            width="250px"
                        />
                    </div>
                </template>
            </ChartCardMulti>
        </div>
    </div>
</template>

<script>
import ChartCardMulti from "@/charts/ChartCardMulti"
import RangeSelect from "@/components/RangeSelect"
import {avg, deep_copy, short_name} from "@/utils"
import {avg_marks_by_groups, default_options, round2} from "@/utils/marks"

export default {
    name: "TheClassChartSubjects",
    components: {
        ChartCardMulti,
        RangeSelect,
    },
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            options: deep_copy(default_options),
            selected_student_index: 0,
            console,
        }
    },
    computed: {
        all_students() {
            return [
                'Общая',
                ...[...this.data.students].map(student => short_name(student.full_name)).sort()
            ]
        },
        selected_student() {
            return this.all_students[this.selected_student_index]
        },
        filtered_marks() {
            if (this.selected_student_index === 0)
                return this.data.marks
            else
                return this.data.marks.filter(
                    mark => short_name(mark.student.full_name) === this.selected_student
                )
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.subject.id,
                this.data.subjects.map(subject => subject.id)
            )
            return Object.entries(marks_grouped).map(([subject_id, mark]) => ({
                key: subject_id,
                label: this.data.subjects_map[subject_id].name,
                datasets: [round2(mark)],
            }))
        },
        total_avg() {
            return round2(avg(this.avg_marks.map(x => x.datasets[0]).filter(x => x > 0)))
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#class-chart-students {

}
</style>
