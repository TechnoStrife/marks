<template>
    <div id="student-chart-period" class="row">
        <div class="col s12">
            <ChartCardMulti
                :data="avg_marks"
                :options="options"
                :label="labels"
                :sort="false"
                @chart-click="console.log(arguments)"
                @export-chart="export_chart"
            >
                <h6>Успеваемость в течение года</h6>
                <template v-slot:filters>
                    <div class="chart-filter left">
                        <div class="filter-title">Год:</div>
                        <RangeSelect
                            v-model="selected_year_index"
                            :range="all_years"
                        />
                    </div>
                    <div class="chart-filter left">
                        <div class="filter-title">Предмет:</div>
                        <RangeSelect
                            v-model="selected_subject_index"
                            :range="select_subject"
                            width="300px"
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
import {
    avg_marks_by_groups,
    default_options,
    distinct,
    get_mark,
    round2,
    save_charts_to_excel_file
} from "@/utils/marks"
import {avg, deep_copy, short_name} from "@/utils"

export default {
    name: "TheStudentChartPeriod",
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
            selected_subject_index: 0,
            labels: ['Средняя оценка', 'Итоговая']
        }
    },
    watch: {
        selected_year_index() {
            this.selected_subject_index = 0
        }
    },
    computed: {
        all_years() {
            return distinct(this.data.marks.marks.map(mark => mark.period.year)).reverse()
        },
        selected_year() {
            return this.all_years[this.selected_year_index]
        },
        all_subjects() {
            let marks = this.data.marks.marks
            // .filter(mark => mark.period.year === this.selected_year)
            let subjects = this.data.marks.subjects
            marks = marks.map(mark => mark.subject.id)
            marks = distinct(marks, false)
            return marks.sort(
                (id1, id2) => subjects[id1].name.localeCompare(subjects[id2].name)
            )
        },
        select_subject() {
            let all_marks = [
                ...this.data.marks.semester_marks,
                ...this.data.marks.terminal_marks,
                ...this.data.marks.marks,
            ]
            return this.all_subjects.map(subject_id => ({
                text: this.data.marks.subjects[subject_id].name,
                id: subject_id,
                disabled: all_marks.find(
                    mark => mark.subject.id === subject_id
                ) === undefined
            }))
        },
        selected_subject() {
            let subject_id = this.select_subject[this.selected_subject_index].id
            return this.data.marks.subjects[subject_id]
        },
        filtered_marks() {
            let selected_year = this.selected_year
            let marks = this.data.marks.marks.filter(
                mark => mark.period.year === selected_year
                    && mark.mark
            )
            if (this.selected_subject !== null) {
                let subject_id = this.selected_subject.id
                marks = marks.filter(mark => mark.subject.id === subject_id)
            }
            return marks
        },
        filtered_semester_marks() {
            let marks = this.data.marks.semester_marks.filter(
                mark => mark.period.year === this.selected_year
            )
            if (this.selected_subject !== null) {
                let subject_id = this.selected_subject.id
                marks = marks.filter(mark => mark.subject.id === subject_id)
            }
            return marks
        },
        avg_marks() {
            const selected_year = this.selected_year
            const selected_subject_id = this.selected_subject.id
            let marks = this.filtered_marks
            let classes = [this.data.class, ...this.data.previous_classes]
            let class_ = classes[this.selected_year_index]
            let period_name = class_.periods.length === 2 ? 'семестр' : 'четверть'
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.period.num,
                class_.periods.map(period => period.num)
            )
            let data = Object.entries(marks_grouped).map(([period_num, mark]) => {
                let semester_mark = this.data.marks.semester_marks.find(
                    mark => mark.period.year === selected_year
                        && mark.period.num === parseInt(period_num)
                        && mark.subject.id === selected_subject_id
                )
                if (semester_mark === undefined)
                    semester_mark = 0
                else
                    semester_mark = semester_mark.mark
                return {
                    key: {num: period_num, year: class_.year},
                    label: `${period_num} ${period_name}`,
                    datasets: [
                        round2(mark),
                        semester_mark,
                    ],
                }
            })
            let terminal_mark = get_mark(this.data.marks.terminal_marks.find(
                mark => mark.year === selected_year
                    && mark.subject.id === selected_subject_id
                    && mark.type === 1
            ))
            data.push({
                key: {type: 1, year: class_.year},
                label: `Годовая оценка`,
                datasets: [
                    round2(avg(this.filtered_marks.map(mark => mark.mark))),
                    terminal_mark,
                ],
            })
            if ([9, 11].includes(class_.num)) {
                let exam_mark = get_mark(this.data.marks.terminal_marks.find(
                    mark => mark.year === selected_year
                        && mark.subject.id === selected_subject_id
                        && mark.type === 2
                ))
                data.push({
                    key: {type: 2, year: class_.year},
                    label: `Экзамен`,
                    datasets: [undefined, exam_mark,],
                })
                let final_mark = get_mark(this.data.marks.terminal_marks.find(
                    mark => mark.year === selected_year
                        && mark.subject.id === selected_subject_id
                        && mark.type === 3
                ))
                data.push({
                    key: {type: 3, year: class_.year},
                    label: `Итоговая`,
                    datasets: [undefined, final_mark],
                })
            }
            return data
        },
    },
    methods: {
        export_chart() {
            const selected_subject_index = this.selected_subject_index
            let charts_data = new Map()
            for (let [index, id] of this.all_subjects.entries()) {
                this.selected_subject_index = index
                charts_data[this.data.marks.subjects[id].name] = this.avg_marks
            }
            this.selected_subject_index = selected_subject_index
            save_charts_to_excel_file(
                `Успеваемость ${short_name(this.data.full_name)} в течение года`,
                this.labels,
                charts_data
            )
        }
    },
}
</script>

<style lang="scss">
#student-chart-period {

}
</style>
