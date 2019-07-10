<template>
    <div id="student-chart-academic-performance">
        <ChartCardDoughnut
            :data="avg_marks"
            label="Успеваемость"
            :draw_avg="false"
        >
            <h6>Оценка профильной области</h6>
            <span>по {{ selected_year }} уч. году</span>
            <div class="select-mark-threshold">
                <p class="select-mark-threshold-title">
                    Порог учёта оценки по предмету
                </p>
                <div class="range-field">
                    <input type="range" min="2" max="4.5" step="0.25" v-model="mark_threshold"/>
                    <span class="select-mark-threshold-value">{{ mark_threshold }}</span>
                </div>
            </div>
            <katex-element :expression="'\\Sigma = ' + total"/>
            <!--<template v-slot:after>
                <div class="after">
                    <a class="waves-effect waves-light btn more"
                       @click="details_modal_opened = true">
                        Подробнее
                    </a>
                </div>
            </template>-->
        </ChartCardDoughnut>
        <!--<Modal v-model="details_modal_opened">
            <TheStudentAcademicPerformanceMore :data="data" :year="selected_year"/>
        </Modal>-->
    </div>
</template>

<script>
import {avg_marks_by_groups, distinct, round2} from "@/utils/marks"
import {avg, sum} from "@/utils"
import strtotime from "locutus/php/datetime/strtotime"
import ChartCardDoughnut from "@/charts/ChartCardDoughnut"


const max_mark = 5
const ignore_groups = ['Физическая культура', 'Технология', 'Прочее']

export default {
    name: "TheStudentChartAcademicPerformance",
    components: {
        // TheStudentAcademicPerformanceMore,
        ChartCardDoughnut,
        // Modal,
    },
    props: {
        data: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            mark_threshold: 3.5,
            // details_modal_opened: false,
        }
    },
    computed: {
        all_years() {
            return distinct(this.data.marks.marks.map(mark => mark.period.year)).reverse()
        },
        selected_year() {
            // 1st Jan - 1st Sep == 243 days
            let current_academic_year = strtotime('243 days ago')
            current_academic_year = new Date(current_academic_year * 1000)
            if (this.all_years[0] === current_academic_year.getFullYear()
                && current_academic_year.getMonth() >= 9
                || this.all_years.length === 1)
                return this.all_years[0]
            else
                return this.all_years[1]
        },
        filtered_marks() {
            return this.data.marks.marks.filter(mark => mark.period.year === this.selected_year)
        },
        avg_marks() {
            let marks = this.filtered_marks
            let marks_grouped = avg_marks_by_groups(
                marks,
                mark => mark.subject.id,
                Object.values(this.data.marks.subjects).map(subject => subject.id)
            )
            marks_grouped = Object.entries(marks_grouped).map(([subject_id, mark]) => ({
                group: this.data.marks.subjects[subject_id].type,
                mark: round2(mark),
            }))
            let academic_fields = {}
            for (let {group, mark} of marks_grouped) {
                if (ignore_groups.includes(group) || mark === 0)
                    continue
                if (!(group in academic_fields))
                    academic_fields[group] = []
                academic_fields[group].push(mark)
            }
            return Object.entries(academic_fields).map(([field, marks]) => ({
                key: field,
                label: field,
                datasets: [round2(this.process_rating(marks))]
            }))
        },
        total() {
            return round2(sum(this.avg_marks.map(x => x.datasets[0])))
        }
    },
    methods: {
        process_rating(group) {
            group = group.map(mark => mark - this.mark_threshold)
            let rating = avg(group) * max_mark / (max_mark - this.mark_threshold)
            return rating > 0 ? rating : 0
        }
    },
}
</script>

<style lang="scss">
@import "~src/variables.scss";

#student-chart-academic-performance {
    @media #{$small-and-down} {
        & {
            margin: 0 -0.75rem;
        }
    }

    .after {
        margin-top: 10px;
    }

    .select-mark-threshold-title {
        margin-top: 1.4em;
        margin-bottom: 0;
    }
    .select-mark-threshold > .range-field {
        display: flex;
        justify-content: space-between;
        flex-wrap: nowrap;
        .select-mark-threshold-value {
            flex: 0 0 auto;
            margin: auto 0 auto 10px;
            width: 25px;
        }
    }
}
</style>
