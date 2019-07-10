<template>
    <div class="chart">
        <canvas ref="canvas"></canvas>
    </div>
</template>

<script>
import Chart from 'chart.js'
import {only_data_changed} from "@/utils/marks"
import {deep_compare, deep_copy, zip} from "@/utils"

export default {
    name: "BaseChart",
    props: {
        width: {
            type: Number,
            default: 400,
        },
        height: {
            type: Number,
            default: 400,
        },
        plugins: {
            type: Array,
            default: Array
        },
        options: {
            type: Object,
            default: Object
        },
        data: {
            type: Object,
            required: true,
        },
        type: {
            type: String,
            required: true
        },
    },
    computed: {
        options_with_defaults() {
            let options = Object.assign({}, this.options)
            options.hover = {...options.hover}
            options.hover.onHover = this.on_hover
            options.onClick = this.on_click
            return options
        },
    },
    data() {
        return {
            _chart: null,
        }
    },
    watch: {
        plugins: 'recreate_chart',
        options: {
            handler(new_val, old_val) {
                if (this._chart) {
                    this._chart.options = this.options_with_defaults
                    this._chart.update()
                }
            },
            deep: true
        },
        data: {
            handler(new_val, old_val) {
                if (!this._chart)
                    return
                if (new_val.datasets.length !== old_val.datasets.length
                    && deep_compare(new_val.labels, old_val.labels)) {
                    new_val = deep_copy(new_val)
                    zip(new_val.datasets, this._chart.data.datasets).forEach(
                        ([new_dataset, old_dataset]) => {
                            new_dataset._meta = old_dataset._meta
                        }
                    )
                    this._chart.data = new_val
                } else if (only_data_changed(new_val, old_val)) {
                    zip(new_val.datasets, this._chart.data.datasets).forEach(
                        ([new_dataset, old_dataset]) => {
                            old_dataset.data = new_dataset.data
                            old_dataset.label = new_dataset.label
                        }
                    )
                } else {
                    this._chart.data = deep_copy(this.data)
                }
                this._chart.update()
            },
            deep: true
        },
        type() {
            if (this._chart)
                this._chart.update()
        },
    },
    methods: {
        generate_legend() {
            if (this._chart)
                return this._chart.generateLegend()
        },
        recreate_chart() {
            if (this._chart)
                this._chart.destroy()
            this._chart = new Chart(
                this.$refs.canvas.getContext('2d'), {
                    type: this.type,
                    data: deep_copy(this.data),
                    options: this.options_with_defaults,
                    plugins: this._plugins,
                }
            )
        },
        on_hover(e, el) {
            this.$refs.canvas.style.cursor = el.length ? 'pointer' : ''
        },
        on_click(event, arr) {
            if (arr.length === 0)
                return
            let key = this.data.datasets[arr[0]._datasetIndex].key[arr[0]._index]
            this.$emit('chart-click', key)
        }
    },
    mounted() {
        this.recreate_chart()
    },
    beforeDestroy() {
        if (this._chart)
            this._chart.destroy()
    }
}
</script>

<style lang="scss">
.chart {
    position: relative;
}
</style>
