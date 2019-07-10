<template>
    <person-link type="student" :person="student"/>
</template>

<script>
import PersonLink from "@/components/PersonLink"

export default {
    name: "StudentLink",
    components: {PersonLink},
    props: {
        student: Object
    },
}
</script>
