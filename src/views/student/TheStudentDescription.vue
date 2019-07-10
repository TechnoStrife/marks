<template>
    <PersonDescription :person="student" class="student-desc">
        <dt>dnevnik.ru:</dt>
        <dd v-if="student.dnevnik_id">
            <a :href="user_link" target="_blank">Пользователь</a>
        </dd>
        <dd>
            <a :href="person_link" target="_blank">Ученик</a>
        </dd>

        <hr>

        <dt>{{ student.leaved ? 'Обучался:' : 'Обучается:' }}</dt>
        <dd>
            c
            <OptionalText>{{ format_date(student.entered) }}</OptionalText>
            до
            <OptionalText>{{ format_date(student.leaved) }}</OptionalText>
        </dd>
        <dd>
            <template v-if="student.class">
                в
                <ClassLink :class_="student.class" text="? классе"/>
            </template>
            <template v-else>
                в <span class="hint-text">(..?)</span> классе
            </template>
        </dd>
        <template v-if="student.previous_classes.length > 0">
            <dt>Ранее учился в:</dt>
            <dd v-for="class_ in student.previous_classes">
                в
                <ClassLink :class_="class_" text="? классе" year/>
            </dd>
        </template>

    </PersonDescription>
</template>

<script>
import {SCHOOL_ID} from "@/const"
import {format_date} from "@/utils"
import PersonDescription from "@/components/PersonDescription"
import OptionalText from "@/components/OptionalText"
import ClassLink from "@/components/ClassLink"

export default {
    name: "StudentDescription",
    components: {
        ClassLink,
        OptionalText,
        PersonDescription

    },
    props: {
        student: {
            type: Object,
            required: true
        }
    },
    data() {
        return {}
    },
    computed: {
        user_link() {
            return `https://dnevnik.ru/user/user.aspx?user=${this.student.dnevnik_id}`
        },
        person_link() {
            return `https://schools.dnevnik.ru/admin/persons/person.aspx`
                + `?person=${this.student.dnevnik_person_id}&school=${SCHOOL_ID}`
        },
    },
    methods: {
        format_date
    },
}
</script>

<style lang="scss">
.student-desc {

}
</style>
