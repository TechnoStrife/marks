<template>
    <div id="student-chart-subject" class="row">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="labels"
                @chart-click="console.log(arguments)"
            >
                <h6>Успеваемость по предметам</h6>

                <template v-slot:filters>
                    <div class="chart-filter left">
                        <div class="filter-title">Год:</div>
                        <RangeSelect v-model="selected_year_index" :range="all_years"/>
                    </div>
                    <div class="chart-filter left">
                        <div class="filter-title">Период:</div>
                        <RangeSelect v-model="selected_period_index" :range="select_period" width="250px"/>
                    </div>
                </template>
            </ChartCardMulti>
        </div>
    </div>
</template>

<script>
import ChartCardMulti from "@/charts/ChartCardMulti"
import RangeSelect from "@/components/RangeSelect"
import {avg_marks_by_groups, default_options, distinct, round2} from "@/utils/marks"
import {deep_copy} from "@/utils"

export default {
    name: "TheStudentChartSubject",
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
            selected_period_index: 0,
            console,
        }
    },
    watch: {
        selected_year_index() {
            this.selected_period_index = 0
        }
    },
    computed: {
        labels() {
            let additional = []
            if (this.selected_period === null) {
                if (this.include_terminal_marks)
                    additional = ['Годовая оценка']
            } else {
                if (this.include_semester_marks)
                    additional = ['Четвертная оценка']
            }
            return ['Средняя оценка', ...additional]
        },
        selected_year() {
            return this.all_years[this.selected_year_index]
        },
        all_years() {
            return distinct(this.data.marks.marks.map(mark => mark.period.year)).reverse()
        },
        all_periods() {
            let marks = this.data.marks.marks.filter(mark => mark.period.year === this.selected_year)
            return distinct(marks.map(mark => mark.period.num))
        },
        select_period() {
            let classes = [this.data.class, ...this.data.previous_classes]
            let period_count = classes[this.selected_year_index].periods_count
            let periods = this.all_periods
            let all_periods = [...Array(period_count).keys()].map(x => x + 1)
            let suffix = period_count === 2 ? ' семестр' : ' четверть'
            all_periods = all_periods.map(x => ({
                text: x + suffix,
                num: x,
                disabled: periods.indexOf(x) === -1
            }))
            return ['Год', ...all_periods]
        },
        selected_period() {
            if (this.selected_period_index === 0)
                return null
            return this.select_period[this.selected_period_index].num
        },
        filtered_marks() {
            let marks = this.data.marks.marks.filter(mark => mark.period.year === this.selected_year)
            if (this.selected_period > 0)
                marks = marks.filter(mark => mark.period.num === this.selected_period)
            return marks
        },
        filtered_semester_marks() {
            let marks = this.data.marks.semester_marks.filter(mark => mark.period.year === this.selected_year)
            if (this.selected_period > 0)
                marks = marks.filter(mark => mark.period.num === this.selected_period)
            return marks
        },
        include_semester_marks() {
            return this.filtered_semester_marks.length > 0
        },
        filtered_terminal_marks() {
            return this.data.marks.terminal_marks.filter(mark => mark.year === this.selected_year)
        },
        include_terminal_marks() {
            return this.filtered_terminal_marks.length > 0
        },
        filtered_subjects() {
            let subjects_map = {[true]: [], [false]: []}
            for (let subject of Object.values(this.data.marks.subjects)) {
                let found = this.data.marks.marks.find(mark => mark.subject.id === subject.id)
                subjects_map[found !== undefined].push(subject.id)
            }
            let has_marks = {}
            let no_marks = {}
            for (let subject_id of subjects_map[true])
                has_marks[subject_id] = this.data.marks.subjects[subject_id]
            for (let subject_id of subjects_map[false])
                no_marks[subject_id] = this.data.marks.subjects[subject_id]
            return {has_marks, no_marks,}
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.subject.id,
                Object.values(this.data.marks.subjects).map(subject => subject.id)
            )
            return Object.entries(marks_grouped).map(([subject_id, mark]) => {
                let subject = this.data.marks.subjects[subject_id]

                let terminal_mark = null
                if (this.selected_period === null) {
                    if (this.include_terminal_marks)
                        terminal_mark = this.filtered_terminal_marks.find(mark => mark.subject === subject)
                } else {
                    if (this.include_semester_marks)
                        terminal_mark = this.filtered_semester_marks.find(mark => mark.subject === subject)
                }
                if (terminal_mark === undefined)
                    terminal_mark = [NaN]
                else if (terminal_mark === null)
                    terminal_mark = []
                else
                    terminal_mark = [terminal_mark.mark]

                return {
                    key: subject,
                    label: subject.name,
                    after_label: subject.type,
                    group: subject.type,
                    datasets: [
                        round2(mark),
                        ...terminal_mark,
                    ],
                }
            })
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#student-chart-subject {

}
</style>
