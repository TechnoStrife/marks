<template>
    <div id="subject-chart-classes" class="row">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="labels"
                :draw_avg="false"
                :stacks="{2: 0, 3: 1}"
                @chart-click="console.log(arguments)"
                @export-chart="export_chart"
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
import {avg_marks_by_groups, default_options, distinct, round2, save_charts_to_excel_file} from "@/utils/marks"

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
            labels: [
                'Средняя оценка',
                'Средняя годовая оценка',
                'Завышение оценки',
                'Занижение оценки',
            ]
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
            let selected_year = this.selected_year
            return this.data.marks.filter(
                mark => mark.class.year === selected_year
            )
        },
        filtered_classes() {
            let selected_year = this.selected_year
            return this.data.classes.filter(
                class_ => class_.year === selected_year
                    && this.data.marks.find(mark => mark.class.id === class_.id) !== undefined
            )
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.class.id,
                this.filtered_classes.map(class_ => class_.id),
                [mark => mark.mark, mark => mark.terminal_mark, mark => mark.diff]
            )
            return Object.entries(marks_grouped).map(
                ([class_id, [mark, terminal_mark, diff]]) => ({
                    key: class_id,
                    label: this.data.classes_map[class_id].name,
                    datasets: [
                        round2(mark || 0),
                        round2(terminal_mark || 0),
                        Math.max(round2(diff || 0), 0),
                        -Math.min(round2(diff || 0), 0),
                    ],
                })
            )
        },
        total_avg() {
            let datasets = transpose_2d(this.avg_marks.map(x => x.datasets).map(
                x => [x[0], x[1], x[2] - x[3]]
            ))
            // datasets = datasets.filter(x => x !== 0)
            return datasets.map(x => round2(avg(x)))
        },
    },
    methods: {
        export_chart() {
            const selected_year_index = this.selected_year_index
            let charts_data = new Map()
            for (let [index, name] of this.all_years.entries()) {
                this.selected_year_index = index
                charts_data['' + name] = this.avg_marks
            }
            this.selected_year_index = selected_year_index
            save_charts_to_excel_file(
                `Успеваемость по ${this.data.name} по классам`,
                this.labels,
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
