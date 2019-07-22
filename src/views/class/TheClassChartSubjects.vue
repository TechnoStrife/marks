<template>
    <div id="class-chart-subjects">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="labels"
                @chart-click="console.log(arguments)"
                @export-chart="export_chart"
            >
                <h6>Средняя оценка по предмету</h6>
                <span>Средняя средняя оценка = {{ total_avg[0] }}</span><br>
                <span>Средняя средняя годовая оценка = {{ total_avg[1] }}</span><br>
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
import {avg, deep_copy, short_name, transpose_2d} from "@/utils"
import {avg_marks_by_groups, default_options, round2, save_charts_to_excel_file} from "@/utils/marks"

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
            labels: [
                'Средняя оценка',
                'Средняя годовая оценка',
            ]
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
            const selected_student = this.selected_student
            if (this.selected_student_index === 0)
                return this.data.marks
            else
                return this.data.marks.filter(
                    mark => short_name(mark.student.full_name) === selected_student
                )
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.subject.id,
                this.data.subjects.map(subject => subject.id),
                [mark => mark.mark, mark => mark.terminal_mark]
            )
            return Object.entries(marks_grouped).map(
                ([subject_id, [mark, terminal_mark]]) => ({
                    key: subject_id,
                    label: this.data.subjects_map[subject_id].name,
                    datasets: [
                        round2(mark || 0),
                        round2(terminal_mark || 0)
                    ],
                })
            )
        },
        total_avg() {
            let datasets = transpose_2d(this.avg_marks.map(x => x.datasets))
            // datasets = datasets.filter(x => x !== 0)
            return datasets.map(x => round2(avg(x)))
        },
    },
    methods: {
        export_chart() {
            const selected_student_index = this.selected_student_index
            let charts_data = new Map()
            for (let [index, name] of this.all_students.entries()) {
                this.selected_student_index = index
                charts_data['' + name] = this.avg_marks
            }
            this.selected_student_index = selected_student_index
            save_charts_to_excel_file(
                `Успеваемость ${this.data.name} по предметам`,
                [this.selected_student],
                charts_data
            )
        }
    },
}
</script>

<style lang="scss">
#class-chart-students {

}
</style>
