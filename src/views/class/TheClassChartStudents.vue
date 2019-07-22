<template>
    <div id="class-chart-students">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="labels"
                @chart-click="console.log(arguments)"
                @export-chart="export_chart"
            >
                <h6>Средняя оценка по ученику</h6>
                <span>Средняя средняя оценка = {{ total_avg[0] }}</span><br>
                <span>Средняя средняя годовая оценка = {{ total_avg[1] }}</span><br>
                <template v-slot:filters>
                    <div class="chart-filter left">
                        <div class="filter-title">Предмет:</div>
                        <RangeSelect
                            v-model="selected_subject_index"
                            :range="all_subjects"
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
    name: "TheClassChartStudents",
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
            selected_subject_index: 0,
            console,
            labels: [
                'Средняя оценка',
                'Средняя годовая оценка',
            ]
        }
    },
    computed: {
        all_subjects() {
            return [
                'Общая',
                ...[...this.data.subjects].map(subject => subject.name).sort()
            ]
        },
        selected_subject() {
            return this.all_subjects[this.selected_subject_index]
        },
        filtered_marks() {
            const selected_subject = this.selected_subject
            if (this.selected_subject_index === 0)
                return this.data.marks
            else
                return this.data.marks.filter(
                    mark => mark.subject.name === selected_subject
                )
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.student.id,
                this.data.students.map(student => student.id),
                [mark => mark.mark, mark => mark.terminal_mark]
            )
            return Object.entries(marks_grouped).map(
                ([student_id, [mark, terminal_mark]]) => ({
                    key: student_id,
                    label: short_name(this.data.students_map[student_id].full_name),
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
            const selected_subject_index = this.selected_subject_index
            let charts_data = new Map()
            for (let [index, name] of this.all_subjects.entries()) {
                this.selected_subject_index = index
                charts_data['' + name] = this.avg_marks
            }
            this.selected_subject_index = selected_subject_index
            save_charts_to_excel_file(
                `Успеваемость ${this.data.name} по ученикам`,
                [this.selected_subject],
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
