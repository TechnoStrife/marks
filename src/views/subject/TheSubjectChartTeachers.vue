<template>
    <div id="class-chart-subjects">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="[
                    'Средняя оценка',
                    'Средняя годовая оценка',
                    'Завышение оценки',
                    'Занижение оценки',
                ]"
                :draw_avg="false"
                :stacks="{2: 0, 3: 1}"
                @chart-click="console.log(arguments)"
            >
                <h6>Средняя оценка по учителю</h6>
                <!--<span>{{ total_avg }}</span>-->
                <template v-slot:filters>
                    <div class="chart-filter left">
                        <div class="filter-title">Год:</div>
                        <RangeSelect
                            v-model="selected_year_index"
                            :range="all_years"
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
import {avg_marks_by_groups, default_options, distinct, get_mark, round2} from "@/utils/marks"

export default {
    name: "TheSubjectChartTeachers",
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
            selected_year_index: 0,
            console,
        }
    },
    computed: {
        all_years() {
            return distinct(this.data.classes.map(class_ => class_.year)).reverse()
        },
        selected_year() {
            return this.all_years[this.selected_year_index]
        },
        filtered_marks() {
            return this.data.marks.filter(
                mark => mark.class.year === this.selected_year
            )
        },
        filtered_teachers() {
            return this.data.teachers.filter(teacher => !!this.filtered_marks.find(
                mark => mark.teacher.id === teacher.id
            ))
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.teacher.id,
                this.filtered_teachers.map(teacher => teacher.id)
            )
            return Object.entries(marks_grouped).map(([teacher_id, mark]) => {
                let terminal_mark = get_mark(this.data.terminal_marks.find(
                    mark => mark.teacher.id === parseInt(teacher_id)
                ))
                return {
                    key: teacher_id,
                    label: short_name(this.data.teachers_map[teacher_id].full_name),
                    datasets: [
                        round2(mark),
                        round2(terminal_mark),
                        mark && terminal_mark ? Math.max(round2(terminal_mark - mark), 0) : 0,
                        mark && terminal_mark ? -Math.min(round2(terminal_mark - mark), 0) : 0,
                    ],
                }
            })
        },
        total_avg() {
            let datasets = transpose_2d(this.avg_marks.map(x => x.datasets).map(
                x => [x[0], x[1], x[2] - x[3]]
            ))
            datasets = datasets.filter(x => x !== 0)
            return datasets.map(x => round2(avg(x)))
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#class-chart-students {

}
</style>
