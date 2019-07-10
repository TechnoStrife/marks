<template>
    <router-link :to="link" :title="person.full_name">
        {{ this.name }}
    </router-link>
</template>

<script>
import {short_name} from "@/utils"

export default {
    name: "PersonLink",
    props: {
        person: Object,
        type: String,
    },
    computed: {
        name() {
            return short_name(this.person.full_name)
        },
        link() {
            return '/' + this.type + '/' + this.person.id + '/'
        }
    },
}
</script>
