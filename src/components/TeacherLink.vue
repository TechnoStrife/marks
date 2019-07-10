<template>
    <person-link type="teacher" :person="teacher"/>
</template>

<script>
import PersonLink from "@/components/PersonLink"

export default {
    name: "TeacherLink",
    components: {PersonLink},
    props: {
        teacher: {
            type: Object,
            required: true,
        }
    },
}
</script>
