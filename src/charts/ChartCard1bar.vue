<template>
    <div class="chart-card card-panel">
        <slot></slot>
        <div class="chart-manager row">
            <div class="chart-sort left">
                <span class="filter-title">Сортировка:</span>
                <SwitchButtons v-model="sort" :options="sort_options"/>
            </div>
            <slot name="filters"></slot>
        </div>
        <div class="row">
            <BaseChart
                :data="processed_data"
                :type="type"
                :options="processed_options"
                @chart-click="reemit('chart-click', arguments)"
            />
        </div>
        <slot name="after"></slot>
    </div>
</template>

<script>
import BaseChart from "@/charts/BaseChart"
import SwitchButtons from "@/components/SwitchButtons"
import {deep_copy, reemit, sum, transpose_array_of_objects} from "@/utils"
import {color_datasets, default_sort_options, mark_color} from '@/utils/marks'
import RangeSelect from "@/components/RangeSelect"
import ChartManager from "@/charts/ChartManager"

export default {
    name: "ChartCard1bar",
    components: {
        ChartManager,
        RangeSelect,
        SwitchButtons,
        BaseChart
    },
    props: {
        type: {
            type: String,
            default: 'bar'
        },
        raw_data: {
            type: Array,
            required: true
        },
        filters: {
            type: Array,
            required: false,
        },
        options: {
            type: Object,
            required: false
        },
        label: {
            type: String,
            required: true,
        },
        draw_avg: {
            type: Boolean,
            default: true,
        },
    },
    data() {
        return {
            data: null,
        }
    },
    computed: {
        sort_options() {
            return [
                {
                    text: '{trending_up}',
                    title: 'Сортировка по возрастанию',
                    sorter: (a, b) => a.mark - b.mark,
                },
                ...default_sort_options(this.data)
            ]
        },
        processed_data() {
            let data = [...this.data].sort(this.sort_options[this.sort].sorter)
            let {label: labels, mark: marks, ...rest} = transpose_array_of_objects(data)
            return {
                labels,
                datasets: color_datasets([{
                    label: this.label,
                    data: marks,
                    ...rest
                }], true)
            }
        },
        processed_options() {
            let options = deep_copy(this.options)
            options.legend = {...options.legend}
            options.legend.display = false
            options.tooltips = {...options.tooltips}
            options.tooltips.callbacks = {...options.tooltips.callbacks}
            options.tooltips.callbacks.afterLabel = (tooltip_item) => {
                let dataset = this.processed_data.datasets[tooltip_item.datasetIndex]
                return dataset.after_label && dataset.after_label[tooltip_item.index]
            }
            if (this.draw_avg) {
                let dataset = this.processed_data.datasets[0]
                let avg = sum(dataset.data) / dataset.data.length
                options.annotation = {
                    annotations: [{
                        value: avg,
                        borderColor: mark_color(avg).border,
                        label: {
                            content: "Сред. " + dataset.label.toLowerCase(),
                            enabled: false,
                            position: 'left',
                        },
                        type: 'line',
                        mode: 'horizontal',
                        scaleID: 'y-axis-0',
                        borderWidth: 2,
                    }],
                }
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
.chart-card {

}
</style>
