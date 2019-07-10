<template>
    <div id="the-subject-description" class="col s12">
        <h5>{{ data.name }}</h5>
        <p>Раздел: {{ data.type }}</p>
        <div class="subject-teachers">
            <hr>
            <p class="ul-title">Учителя:</p>
            <ul class="dashed" v-if="data.teachers.length > 0">
                <li v-for="teacher of data.teachers">
                    <TeacherLink :teacher="teacher"/>
                </li>
            </ul>
            <p v-else>&mdash;<span class="hint-text">..?</span></p>
        </div>
        <hr>
        <p class="ul-title">Изучается в:</p>
        <ul class="subject-classes dashed">
            <li v-for="class_ of data.classes">
                <ClassLink :class_="class_" year/>
            </li>
        </ul>
    </div>
</template>

<script>
import TeacherLink from "@/components/TeacherLink"
import ClassLink from "@/components/ClassLink"

export default {
    name: "TheSubjectDescription",
    components: {
        TeacherLink,
        ClassLink
    },
    props: {
        data: {
            type: Object,
            required: true,
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
#the-subject-description {

}
</style>
