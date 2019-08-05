<template>
    <div id="classes-summary-view" class="summary-view row" v-if="data">
        <div class="col s12 m10 push-m1 l8 push-l2">
            <div class="row">
                <h5 class="center">Сводка по классам</h5>
            </div>
            <div class="row" v-for="level of classes_by_level">
                <ClassesSummaryChart :data="level.data" :level_name="level.name"/>
            </div>
        </div>
    </div>
</template>

<script>
import BaseViewMixin from "@/mixins/BaseViewMixin"
import {zip} from "@/utils"
import ClassesSummaryChart from "@/views/summary/classes/ClassesSummaryChart"


export default {
    name: "ClassesSummaryView",
    components: {
        ClassesSummaryChart
    },
    mixins: [BaseViewMixin],
    data() {
        return {}
    },
    computed: {
        classes_by_level() {
            function class_level(class_) {
                let num = parseInt(class_.name.slice(0, -1))
                for (let [index, max] of [4, 9, 11].entries())
                    if (num <= max)
                        return index
            }

            let res = [[], [], []]
            for (let class_marks of this.data) {
                res[class_level(class_marks.class)].push(class_marks)
            }
            res = zip(['Начальная', 'Основная', 'Среднаяя'], res).map(
                x => ({name: x[0], data: x[1]})
            )
            return res
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
#classes-summary-view {
    > .col > .row {
        margin-bottom: 0;
    }
}
</style>
