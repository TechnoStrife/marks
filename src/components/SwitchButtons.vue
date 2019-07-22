<template>
    <div class="switch-buttons">
        <button
            v-for="(option, index) in processed"
            :title="option.title"
            :class="{
                selected: index === selected,
                'waves-effect': waves
            }"
            class="hover-highlight"
            :style="{color: option.color}"
            @click="$emit('switch', index)"
            v-html="option.text"
        />
    </div>
</template>

<script>
export default {
    name: "SwitchButtons",
    model: {
        prop: 'selected',
        event: 'switch',
    },
    props: {
        selected: {
            type: Number,
            required: false,
        },
        options: {
            type: Array,
            required: true,
        },
        brackets: {
            type: String,
            default: '{}',
            validator: brackets => brackets.length === 2
        },
        waves: {
            type: Boolean,
            default: true,
        },
    },
    data() {
        return {}
    },
    computed: {
        processed() {
            return this.options.map(option => {
                option = {...option}
                option.text = option.text.replace(this.brackets[0], '<i class="material-icons">')
                    .replace(this.brackets[1], '</i>')
                return option
            })
        },
    },
    methods: {},
}
</script>

<style lang="scss">
.switch-buttons {
    display: inline-block;
    font-size: 0.7em;
    user-select: none;
    border-radius: 4px;
    border: 1px solid rgba(0, 0, 0, .12);
    background-color: #fff;

    button {
        padding: 3px 8px;
        position: relative;
        background-color: transparent;
        border: none;
        height: 100%;

        &:not(.waves-effect):active:after {
            background-color: rgba(0, 0, 0, 0.08);
        }

        &.selected, &:focus {
            background-color: rgba(0, 0, 0, 0.12);
        }

        &:not(:first-child) {
            margin-left: 1px;
            box-shadow: -1px 0 0 rgba(0, 0, 0, 0.12);
        }
    }
}
</style>
