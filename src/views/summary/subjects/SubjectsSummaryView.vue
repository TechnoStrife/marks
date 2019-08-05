<template>
    <div id="subjects-summary-view" class="summary-view row" v-if="data">
        <div class="col s12 m10 push-m1 l8 push-l2">
            <div class="row">
                <h5 class="center">Сводка по предметам</h5>
            </div>
            <div class="row" v-for="group of grouped_data">
                <SubjectsSummaryChart :data="group.data" :group_name="group.name"/>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import {group_by, key_sorter} from "@/utils"
import SubjectsSummaryChart from "@/views/summary/subjects/SubjectsSummaryChart"
import {sorter_with_others_group} from "@/utils/marks"


export default {
    name: "SubjectsSummaryView",
    components: {
        SubjectsSummaryChart
    },
    mixins: [BaseViewMixin],
    data() {
        return {}
    },
    computed: {
        grouped_data() {
            let subjects = group_by(this.data, subject_marks => subject_marks.subject.type)
            subjects = Object.entries(subjects)
            subjects.sort(
                ([type1], [type2]) => sorter_with_others_group(type1, type2)
            )
            return subjects.map(([type, subjects]) => ({
                name: type,
                data: subjects.sort(key_sorter(subject => subject.name))
            }))
        }
    },
    methods: {
        transform_response(data) {
            return data.results
        }
    },
}
</script>

<style lang="scss">
#subjects-summary-view {
    > .col > .row {
        margin-bottom: 0;
    }
}
</style>
