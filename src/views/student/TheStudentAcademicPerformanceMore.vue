<template>
    <div id="student-academic-performance-more">
        <h6>Оценка профильной области</h6>
        <div class="select-mark-threshold row">
            <div class="range-field col s12 m8 l6">
                <input type="range" min="2" max="4.5" step="0.25" v-model="mark_threshold"/>
                <span class="select-mark-threshold-value">{{ mark_threshold }}</span>
            </div>
        </div>
        <div class="row">
            <ChartCardMulti/>
        </div>
    </div>
</template>

<script>
import ChartCardMulti from "@/charts/ChartCardMulti"
import {avg_marks_by_groups, round2} from "@/utils/marks"
import {zip} from "@/utils"
import {chart_color_sequence} from "@/const"

const max_mark = 5
const ignore_types = ['Физическая культура', 'Технология', 'Прочее']

export default {
    name: "TheStudentAcademicPerformanceMore",
    components: {
        ChartCardMulti

    },
    props: {
        data: {
            type: Object,
            required: true,
        },
        year: {
            type: Number,
            required: true,
        }
    },
    data() {
        return {
            mark_threshold: 3.5
        }
    },
    computed: {
        filtered_marks() {
            return this.data.marks.marks.filter(mark => mark.period.year === this.year)
        },
        all_types() {
            let types = new Set(this.filtered_marks.map(mark => mark.type))
            ignore_types.forEach(type => types.delete(type))
            return [...types].sort()
        },
        colored_types() {
            return Object.fromEntries(zip(this.all_types, chart_color_sequence))
        },
        filtered_subjects() {
            return Object.values(this.data.marks.subjects).filter(
                subject => this.all_types.includes(subject.type)
            ).sort((a, b) => a.type.localeCompare(b.type))
        },
        marks_grouped() {
            return avg_marks_by_groups(
                this.filtered_marks.filter(mark => this.all_types.includes(mark.subject.type)),
                mark => mark.subject.id,
                this.filtered_subjects.map(subject => subject.id)
            )
        },
        avg_marks() {
            let marks_grouped = Object.entries(this.marks_grouped).map(([subject_id, mark]) => ({
                group: this.data.marks.subjects[subject_id].type,
                name: this.data.marks.subjects[subject_id].name,
                mark: round2(mark),
            }))
            let academic_fields = {}
            for (let {group, mark, name} of marks_grouped) {
                if (ignore_types.includes(group) || mark === 0)
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
    },
    methods: {},
}
</script>

<style lang="scss">
#student-academic-performance-more {

}
</style>
