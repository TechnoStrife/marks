<template>
    <component :is="tag" v-if="has_text">
        <slot/>
    </component>
    <component :is="tag" v-else class="hint-text">
        {{ hint_text }}
    </component>
</template>

<script>
import {slot_not_empty} from "@/utils"

export default {
    name: "OptionalText",
    props: {
        tag: {
            type: String,
            default: 'span'
        },
        hint_text: {
            type: String,
            default: '(..?)'
        }
    },
    computed: {
        has_text() {
            return slot_not_empty(this.$slots.default)
        }
    },
}
</script>

<style lang="scss">

</style>
