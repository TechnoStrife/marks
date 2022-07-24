<template>
    <div class="subjects-summary-chart row" v-if="all_years.length > 0">
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
                <h6>{{ group_name }}</h6>
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
    name: "SubjectsSummaryChart",
    components: {
        ChartCardMulti,
        RangeSelect,
    },
    props: {
        data: {
            type: Array,
            required: true,
        },
        group_name: {
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
            return distinct(this.data.map(subject => subject.year)).reverse()
        },
        selected_year() {
            return this.all_years[this.selected_year_index]
        },
        filtered_subjects() {
            let selected_year = this.selected_year
            return this.data.filter(
                x => x.year === selected_year
            )
        },
        chart_data() {
            return this.filtered_subjects.map(
                subject_marks => ({
                    key: subject_marks.subject.id,
                    label: subject_marks.subject.name,
                    datasets: [
                        round2(subject_marks.mark || 0),
                        round2(subject_marks.terminal_mark || 0),
                        Math.max(round2(subject_marks.diff || 0), 0),
                        -Math.min(round2(subject_marks.diff || 0), 0),
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
                `Успеваемость по ${this.data.name} по классам`,
                this.labels,
                charts_data
            )
        }
    },
}
</script>

<style lang="scss">
.subjects-summary-chart {

}
</style>
