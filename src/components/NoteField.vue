<template>
    <div class="note-field">
        <p v-if="note == null" class="hint-text">
            (заметок нет)
        </p>
        <p v-else>
            {{ note }}
        </p>
    </div>
</template>

<script>
export default {
    name: "NoteField",
    props: {
        note: {
            type: String,
            required: false
        },
        tag: {
            type: String,
            default: 'p'
        },
        save_to: {
            type: String,
            required: false
        }
    },
    data() {
        return {}
    },
    computed: {},
    methods: {},
}
</script>

<style lang="scss">
.note-field {

}
</style>
