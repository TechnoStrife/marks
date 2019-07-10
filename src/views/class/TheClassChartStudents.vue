<template>
    <div id="class-chart-students">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="selected_subject"
                @chart-click="console.log(arguments)"
            >
                <h6>Средняя оценка по предмету</h6>
                <katex-element :expression="'\\langle X \\rangle = ' + total_avg"/>
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
import {avg, deep_copy, short_name} from "@/utils"
import {avg_marks_by_groups, default_options, round2} from "@/utils/marks"

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
            if (this.selected_subject_index === 0)
                return this.data.marks
            else
                return this.data.marks.filter(
                    mark => mark.subject.name === this.selected_subject
                )
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.student.id,
                this.data.students.map(student => student.id)
            )
            return Object.entries(marks_grouped).map(([student_id, mark]) => ({
                key: student_id,
                label: short_name(this.data.students_map[student_id].full_name),
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
