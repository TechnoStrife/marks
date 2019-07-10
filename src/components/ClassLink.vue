<template>
    <router-link :to="link" :disabled="disabled">
        {{ link_text }}
    </router-link>
</template>

<script>
export default {
    name: "ClassLink",
    props: {
        class_: {
            type: Object,
            required: true
        },
        text: {
            type: String,
            default: '? класс'
        },
        year: {
            type: Boolean,
            default: false
        },
        disabled: {
            type: Boolean,
            default: false,
        }
    },
    computed: {
        link() {
            return `/class/${this.class_.id}/`
        },
        link_text() {
            let class_text = this.text.replace('?', this.class_.name)
            if (this.year)
                class_text += ` (${this.class_.year}/${this.class_.year + 1})`
            return class_text
        }
    },
}
</script>

<style lang="scss">
.class-link {

}
</style>
