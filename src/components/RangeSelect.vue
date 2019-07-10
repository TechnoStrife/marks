<template>
    <div class="range-select" :style="{width: width}">
        <button class="waves-effect" :disabled="backward_disabled" @click="backward">
            <i class="material-icons">
                keyboard_arrow_left
            </i>
        </button>
        <div
            class="select-wrapper"
            tabindex="-1"
            @click="dropdown = true"
            v-click-outside="close_dropdown"
        >
            <transition :name="animation">
                <div :key="selected">
                    {{ range[selected].text ? range[selected].text : range[selected] }}
                </div>
            </transition>
            <ul class="dropdown-content select-dropdown" :class="{active: dropdown}">
                <li v-for="(option, index) in range"
                    :selected="index === selected"
                    :class="{selected: index === selected, disabled: option.disabled}"
                    @click.stop="select(index)">
                    <span>{{ option.text ? option.text : option }}</span>
                </li>
            </ul>
        </div>
        <button class="waves-effect" :disabled="forward_disabled" @click="forward">
            <i class="material-icons">
                keyboard_arrow_right
            </i>
        </button>
    </div>
</template>

<script>
import ClickOutside from 'vue-click-outside'


export default {
    name: "RangeSelect",
    model: {
        prop: 'selected',
        event: 'switch',
    },
    props: {
        range: {
            type: Array,
            required: true,
            validator(range) {
                return range.every(option =>
                    typeof option === 'string'
                    || typeof option === 'number'
                    || option instanceof Object && typeof option.text === 'string'
                )
            }
        },
        selected: {
            type: Number,
        },
        width: {
            type: String,
            required: false,
        }
    },
    data() {
        return {
            dropdown: false,
            animation: "slide-left"
        }
    },
    watch: {
        selected(old_val, new_val) {
            if (old_val < new_val)
                this.animation = "slide-right"
            else
                this.animation = "slide-left"
        }
    },
    computed: {
        forward_disabled() {
            return this.selected >= this.range.length - 1 ||
                this.range.slice(this.selected + 1).every(x => x.disabled)
        },
        backward_disabled() {
            return this.selected <= 0 ||
                this.range.slice(0, this.selected).every(x => x.disabled)
        },
    },
    methods: {
        forward() {
            if (this.forward_disabled)
                return
            let target = this.range.slice(this.selected + 1).findIndex(x => !x.disabled)
            target += this.selected + 1
            this.$emit('switch', target)
        },
        backward() {
            if (this.backward_disabled)
                return
            let target = this.range.slice(0, this.selected).reverse().findIndex(x => !x.disabled)
            target = this.selected - 1 - target
            this.$emit('switch', target)
        },
        select(value) {
            if (this.range[value].disabled)
                return
            this.dropdown = false
            this.$emit('switch', value)
        },
        close_dropdown() {
            this.dropdown = false
        },
    },
    directives: {
        ClickOutside
    }
}
</script>

<style lang="scss">
$height: 24px;
$animation-duration: 150ms;

.range-select {
    width: 200px;
    display: flex;
    flex-wrap: nowrap;
    align-items: stretch;
    align-content: stretch;
    font-size: 0.7em;
    user-select: none;
    border-radius: 4px;
    border: 1px solid rgba(0, 0, 0, .12);
    background-color: #fff;

    > * {
        flex: 0 0 40px;
        padding: 3px 8px;
        /*overflow: hidden;*/
        position: relative;
        background-color: transparent;
        border: none;

        &[disabled] {
            cursor: initial;
        }
        &:after {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
        }
        &:not([disabled]):hover:after {
            background-color: rgba(0, 0, 0, 0.04);
        }
        &:not(.select-wrapper):not([disabled]):not(.waves-effect):active:after {
            background-color: rgba(0, 0, 0, 0.08);
        }
        &:not(select).selected, &:not(select):focus {
            background-color: transparent;
        }
        &:not(:first-child) {
            margin-left: 1px;
            box-shadow: -1px 0 0 rgba(0, 0, 0, 0.12);
        }
    }

    > .select-wrapper {
        outline: none;
        flex: 1 1 100%;
        > div {
            margin: 0 auto;
            font-size: 16px;
            text-align: center;
            position: relative;
            width: 100%;
            left: 0;
            display: inline-block;
            &:not(:first-child) {
                position: absolute;
            }
        }
        .dropdown-content {
            top: 3px;
            left: 8px;
            right: 8px;
            transition: transform $animation-duration, opacity $animation-duration;
            transform: scaleX(0) scaleY(0);
            display: initial;
            &.active {
                transform: scaleX(1) scaleY(1);
                opacity: 1;
            }
        }
        input {
            height: $height !important;
            line-height: initial !important;
            margin-bottom: 0 !important;
            border: none !important;
        }
    }
}

$slide-amount: 40%;

.slide-left-enter-active, .slide-left-leave-active,
.slide-right-enter-active, .slide-right-leave-active {
    transition: all 0.3s;
}
.slide-left-enter, .slide-left-leave-active,
.slide-right-enter, .slide-right-leave-active {
    opacity: 0;
}
.slide-left-enter {
    transform: translateX($slide-amount);
}
.slide-left-leave-active {
    transform: translateX(-$slide-amount);
}
.slide-right-enter {
    transform: translateX(-$slide-amount);
}
.slide-right-leave-active {
    transform: translateX($slide-amount);
}
</style>
