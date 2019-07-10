<template>
    <div class="chart-card card-panel" v-if="card">
        <slot></slot>
        <div class="row chart-filters">
            <slot name="filters"></slot>
            <div class="chart-sort left" v-if="sort === true">
                Сортировка:
                <SwitchButtons :options="sort_options" @switch="resort_data"/>
            </div>
        </div>
        <div class="row">
            <BaseChart
                :data="colored_datasets"
                :type="type"
                :options="processed_options"
                @chart-click="reemit('chart-click', arguments)"
            />
        </div>
        <slot name="after"></slot>
    </div>
    <div v-else>
        <BaseChart
            :data="colored_datasets"
            :type="type"
            :options="processed_options"
            @chart-click="reemit('chart-click', arguments)"
        />
    </div>
</template>

<script>
import BaseChart from "@/charts/BaseChart"
import SwitchButtons from "@/components/SwitchButtons"
import {deep_copy, reemit, sum, transpose_2d, transpose_array_of_objects, zip} from "@/utils"
import {color_datasets, default_sort_options} from "@/utils/marks"
import {chart_color_sequence} from "@/const"
import rearrange from "array-rearrange"


export default {
    name: "ChartCardMulti",
    components: {
        SwitchButtons,
        BaseChart
    },
    props: {
        type: {
            type: String,
            default: 'bar'
        },
        data: {
            type: Array,
            required: true
        },
        options: {
            type: Object,
            required: false,
        },
        stacks: {
            type: Object,
            required: false,
        },
        label: {
            type: [String, Array],
            required: true,
            validator: function (label) {
                if (Array.isArray(label))
                    return label.every(label => typeof label === 'string')
                return typeof label === 'string'
            }
        },
        draw_avg: {
            type: Boolean,
            default: true,
        },
        sort: {
            type: [Boolean, String],
            default: true,
        },
        card: {
            type: Boolean,
            default: true,
        }
    },
    data() {
        return {
            previous_sort: 0,
            data_changed: false,
            sort_ids: null,
            color_each_mark: false,
            sorted_data: null,
        }
    },
    computed: {
        sort_options() {
            let datasets_count = this.data[0].datasets.length
            let dataset_colors = chart_color_sequence.slice(0, datasets_count)
            let sort_options = dataset_colors.map((color, i) => ({
                key: `asc${i ? i : ''}`,
                text: '{trending_up}',
                title: `Сортировка по возрастанию (${this.labels[i]})`,
                sorter: (a, b) => a.datasets[i] - b.datasets[i],
                color: color.border
            }))
            return [...sort_options, ...default_sort_options(this.data)]
        },
        labels() {
            if (Array.isArray(this.label))
                return this.label
            else
                return [this.label]
        },
        processed_data() {
            let data = this.sort ? this.sorted_data : this.data
            let {label: labels, datasets, ...rest} = transpose_array_of_objects(data)
            datasets = transpose_2d(datasets)
            let stack = 0
            return {
                labels,
                datasets: zip(this.labels, datasets).map(([label, data], i) => ({
                    label,
                    data,
                    ...rest,
                    ...(this.stacks ? {
                        stack: '' + (i in this.stacks ? this.stacks[i] : stack++)
                    } : {})
                }))
            }
        },
        colored_datasets() {
            let data = this.processed_data
            data.datasets = color_datasets(data.datasets)
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
            if (this.stacks) {
                options.scales = {...options.scales}
                options.scales.xAxes = options.scales.xAxes ? [...options.scales.xAxes] : [{}]
                options.scales.xAxes[0] = {...options.scales.xAxes[0]}
                options.scales.xAxes[0].stacked = true
                options.scales.yAxes = options.scales.yAxes ? [...options.scales.yAxes] : [{}]
                options.scales.yAxes[0] = {...options.scales.yAxes[0]}
                options.scales.yAxes[0].stacked = true
            }
            if (this.draw_avg) {
                let datasets = this.colored_datasets.datasets
                options.annotation = {...options.annotation}
                options.annotation.annotations = datasets.map(function (dataset) {
                    let data = dataset.data.filter(x => !!x)
                    return {
                        type: 'line',
                        mode: 'horizontal',
                        scaleID: 'y-axis-0',
                        borderWidth: 2,
                        value: sum(data) / data.length,
                        borderColor: dataset.borderColor,
                        label: {
                            enabled: false,
                            position: 'left',
                            content: "Сред. " + dataset.label.toLowerCase(),
                        },
                    }
                })
            }
            return options
        },
    },
    watch: {
        data() {
            if (this.sort) {
                if (this.data.length === this.sort_ids.legnth) {
                    this.sorted_data = rearrange([...this.data], [...this.sort_ids])
                    this.data_changed = true
                } else {
                    this.sort_data()
                }
            }
        }
    },
    created() {
        if (this.sort)
            this.sort_data()
    },
    methods: {
        reemit,
        sort_data() {
            let sorter
            if (this.sort === true) {
                sorter = this.sort_options[this.previous_sort].sorter
            } else {
                sorter = this.sort_options.find(option => option.key === this.sort)
                if (!sorter)
                    throw `'${this.sort}' sort option not found\n`
                    + `available options: ${this.sort_options.map(x => x.key).join()}`
                sorter = sorter.sorter
            }
            let indexed_data = this.data.map((x, i) => [x, i])
            let sorted_data = indexed_data.sort(([a], [b]) => sorter(a, b))
            this.sorted_data = sorted_data.map(([x]) => x)
            this.sort_ids = sorted_data.map(([_, id]) => id)
        },
        resort_data(sort) {
            if (sort === this.previous_sort && !this.data_changed)
                return
            this.previous_sort = sort
            this.sort_data()
        }
    },
}
</script>
