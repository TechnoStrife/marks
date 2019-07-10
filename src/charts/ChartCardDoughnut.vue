<template>
    <div class="chart-card chart-card-doughnut card-panel">
        <slot></slot>
        <div class="row">
            <BaseChart
                :data="colored_datasets"
                type="doughnut"
                :options="processed_options"
                @chart-click="reemit('chart-click', arguments)"
            />
        </div>
        <slot name="after"></slot>
    </div>
</template>

<script>
import BaseChart from "@/charts/BaseChart"
import {doughnut_color_datasets} from "@/utils/marks"
import {deep_copy, reemit, transpose_2d, transpose_array_of_objects} from "@/utils"
import rearrange from "array-rearrange"


export default {
    name: "ChartCardDoughnut",
    components: {
        BaseChart
    },
    props: {
        data: {
            type: Array,
            required: true
        },
        options: {
            type: Object,
            required: false,
            default() {
                return {autoSkip: false, aspectRatio: 0.9}
            }
        },
    },
    data() {
        return {
            saved_sort_order: null,
        }
    },
    computed: {
        processed_data() {
            let data
            if (this.saved_sort_order === null) {
                let indexed_data = this.data.map((x, i) => [x, i])
                let sorted_data = indexed_data.sort(([a], [b]) => b.datasets[0] - a.datasets[0])
                data = sorted_data.map(([x]) => x)
                this.saved_sort_order = sorted_data.map(([_, id]) => id)
            } else {
                data = rearrange([...this.data], [...this.saved_sort_order])
            }
            let {label: labels, datasets, ...rest} = transpose_array_of_objects(data)
            datasets = transpose_2d(datasets)
            return {
                labels,
                datasets: [{
                    label: this.label,
                    data: datasets[0],
                    ...rest
                }]
            }
        },
        colored_datasets() {
            let data = this.processed_data
            data.datasets = doughnut_color_datasets(data.datasets)
            return data
        },
        processed_options() {
            let options = deep_copy(this.options)
            options.legend = {...options.legend}
            // options.legend.display = false
            options.tooltips = {...options.tooltips}
            options.tooltips.callbacks = {...options.tooltips.callbacks}
            options.tooltips.callbacks.afterLabel = (tooltip_item) => {
                let dataset = this.processed_data.datasets[tooltip_item.datasetIndex]
                return dataset.after_label && dataset.after_label[tooltip_item.index]
            }
            return options
        },
    },
    methods: {
        reemit
    },
}
</script>

<style lang="scss">
.chart-card-doughnut {

}
</style>
