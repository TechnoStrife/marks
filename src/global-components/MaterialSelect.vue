<template>
    <select @change="$emit('input', value)">
        <slot></slot>
    </select>
</template>

<script>
import Vue from 'vue'
import {FormSelect} from "materialize-css"


"use strict"

export default Vue.component("material-select", {
    props: {
        value: String
    },
    watch: {
        value: function (value) {
            this.reload(value)
        }
    },
    methods: {
        reload: function (value) {
            this.$el.value = value || this.value
            FormSelect.getInstance(this.$el).destroy()
            FormSelect.init(this.$el)
        }
    },
    mounted: function () {
        this.$el.value = this.value
        FormSelect.init(this.$el)
    },
    updated: function () {
        this.reload()
    },
    destroyed: function () {
        FormSelect.getInstance(this.$el).destroy()
    }
})
</script>
