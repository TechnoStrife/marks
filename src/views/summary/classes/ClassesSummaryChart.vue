<template>
    <div class="classes-summary-chart row" v-if="all_years.length > 0">
        <div class="col s12">
            <ChartCardMulti
                :data="chart_data"
                :options="options"
                :label="labels"
                :draw_avg="false"
                :stacks="{2: 0, 3: 1}"
                @chart-click="console.log(arguments)"
                @export-chart="export_chart"
            >
                <h6>{{ level_name }} школа</h6>
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
import {default_options, distinct, round2, save_charts_to_excel_file} from "@/utils/marks"

export default {
    name: "ClassesSummaryChart",
    components: {
        ChartCardMulti,
        RangeSelect,
    },
    props: {
        data: {
            type: Array,
            required: true,
        },
        level_name: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            options: {
                aspectRatio: 2,
                ...deep_copy(default_options)
            },
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
            return distinct(this.data.map(class_ => class_.year)).reverse()
        },
        selected_year() {
            return this.all_years[this.selected_year_index]
        },
        filtered_classes() {
            let selected_year = this.selected_year
            return this.data.filter(
                class_ => class_.year === selected_year
            )
        },
        chart_data() {
            return this.filtered_classes.map(
                class_marks => ({
                    key: class_marks.class.id,
                    label: class_marks.class.name,
                    datasets: [
                        round2(class_marks.mark || 0),
                        round2(class_marks.terminal_mark || 0),
                        Math.max(round2(class_marks.diff || 0), 0),
                        -Math.min(round2(class_marks.diff || 0), 0),
                    ],
                })
            )
        },
        total_avg() {
            let datasets = transpose_2d(this.chart_data.map(x => x.datasets).map(
                x => [x[0], x[1], x[2] - x[3]]
            ))
            return datasets.map(x => round2(avg(x)))
        },
    },
    methods: {
        export_chart() {
            const selected_year_index = this.selected_year_index
            let charts_data = new Map()
            for (let [index, name] of this.all_years.entries()) {
                this.selected_year_index = index
                charts_data['' + name] = this.chart_data
            }
            this.selected_year_index = selected_year_index
            save_charts_to_excel_file(
                `Сводка по классам`,
                this.labels,
                charts_data
            )
        }
    },
}
</script>

<style lang="scss">
.classes-summary-chart {

}
</style>
