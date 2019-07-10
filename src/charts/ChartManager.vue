<template>
    <div class="chart-manager row">
        <div class="left">
            <span class="filter-title">Сортировка:</span>
            <SwitchButtons v-model="sort" :options="sort_options"/>
        </div>
        <template v-if="filters.length">
            <div class="left" v-for="filter in filters">
                <span class="filter-title" v-if="filter.title">{{ filter.title }}</span>
                <RangeSelect v-model="filter.selected" :range="filter.range"/>
            </div>
        </template>
    </div>
</template>

<script>
import RangeSelect from "@/components/RangeSelect"
import SwitchButtons from "@/components/SwitchButtons"
import {default_sort_options} from "@/utils/marks"

export default {
    name: "ChartManager",
    components: {
        SwitchButtons,
        RangeSelect
    },
    props: {
        filters: {
            type: Array,
            required: true,
            validator(filters) {
                return filters.every(filter =>
                    filter instanceof Object
                    && (!filter.title || filter.title instanceof String)
                    && filter.range instanceof Array
                    && filter.range.every(x => x instanceof String)
                    && filter.filter instanceof Function
                )
            }
        },
        data: {
            type: Array,
            required: true,
        }
    },
    data() {
        return {
            sort: null,
            filtered_data: null,
        }
    },
    computed: {
        sort_options() {
            let dataset_count = this.filtered_data[0].datasets.length
            let dataset_colors
            if (dataset_count === 1)
                dataset_colors = [undefined]
            else
                dataset_colors = chart_color_sequence.slice(0, dataset_count)
            let sort_options = dataset_colors.map((color, i) => ({
                text: '{trending_up}',
                title: `Сортировка по возрастанию (${this.labels[i]})`,
                sorter: (a, b) => a.datasets[i] - b.datasets[i],
                color: color && color.border
            }))
            return [...sort_options, ...default_sort_options(this.data)]
        },
        sorted_data() {
            return [...this.data].sort(this.sort_options[this.sort].sorter)
        },
    },
    watch: {
        data: "filter_data",
        sorted_data() {
            this.$emit('update', this.sorted_data)
        }
    },
    methods: {
        filter_data() {
            let data = this.data
            for (let filter of this.filters) {
                data = data.filter(filter.filter(filter.selected))
            }
            this.filtered_data = data
        }
    },
}
</script>

<style lang="scss">
.chart-manager {

}
</style>
