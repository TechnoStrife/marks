<template>
    <div id="subject-chart-classes">
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
                <h6>Средняя оценка по классу</h6>
                <span>Средняя средняя оценка = {{ total_avg[0] }}</span><br>
                <span>Средняя средняя годовая оценка = {{ total_avg[1] }}</span><br>
                <span>Среднее завышение оценки = {{ total_avg[2] }}</span><br>
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
import {avg, deep_copy, transpose_2d} from "@/utils"
import {avg_marks_by_groups, default_options, distinct, get_mark, round2} from "@/utils/marks"

export default {
    name: "TheSubjectChartClasses",
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
        filtered_classes() {
            return this.data.classes.filter(class_ => class_.year === this.selected_year)
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.class.id,
                this.filtered_classes.map(class_ => class_.id)
            )
            return Object.entries(marks_grouped).map(([class_id, mark]) => {
                let terminal_mark = this.data.terminal_marks.find(
                    mark => mark.class.id === parseInt(class_id)
                )
                terminal_mark = get_mark(terminal_mark)
                return {
                    key: class_id,
                    label: this.data.classes_map[class_id].name,
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
            let datasets = transpose_2d(this.avg_marks.map(
                x => [x.datasets[0], x.datasets[1], x.datasets[2] - x.datasets[3]]
            ))
            return datasets.map(x => round2(avg(x.filter(x => x !== 0))))
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#class-chart-students {

}
</style>
