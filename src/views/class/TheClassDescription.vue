<template>
    <div id="the-class-description" class="col s12">
        <h5>Класс {{ data.name }} ({{ data.year }}/{{ data.year + 1 }})</h5>
        <NoteField :note="data.info"/>
        <dl>
            <dt>Классный руководитель:</dt>
            <dd>
                <OptionalText hint_text="(не назначен)">
                    <TeacherLink :teacher="data.head_teacher" v-if="data.head_teacher"/>
                </OptionalText>
            </dd>
            <dt>dnevnik.ru:</dt>
            <dd>
                <a :href="class_page" target="_blank">Класс</a>
            </dd>
            <dd>
                <a :href="class_admin_page" target="_blank">Администрирование</a>
            </dd>
        </dl>
        <div class="related-classes">
            <hr>
            <p class="ul-title">Параллель:</p>
            <ul class="dashed">
                <li v-for="class_ of data.horizontal_classes">
                    <template v-if="class_.id === data.id">
                        этот класс
                    </template>
                    <template v-else>
                        <ClassLink :class_="class_" year/>
                    </template>
                </li>
            </ul>
            <div class="vertical-classes" v-if="data.vertical_classes.length > 1">
                <p class="ul-title">Вертикаль:</p>
                <ul class="dashed">
                    <li v-for="class_ of data.vertical_classes">
                        <template v-if="class_.id === data.id">
                            этот класс
                        </template>
                        <template v-else>
                            <ClassLink :class_="class_" year/>
                        </template>
                    </li>
                </ul>
            </div>
        </div>
        <hr>
        <p class="ul-title">Ученики ({{ data.students.length }}):</p>
        <ul class="class-students dashed">
            <li v-for="student of data.students">
                <StudentLink :student="student"/>
            </li>
        </ul>
    </div>
</template>

<script>
import StudentLink from "@/components/StudentLink"
import OptionalText from "@/components/OptionalText"
import ClassLink from "@/components/ClassLink"
import TeacherLink from "@/components/TeacherLink"
import {SCHOOL_ID} from "@/const"
import NoteField from "@/components/NoteField"

export default {
    name: "TheClassDescription",
    components: {
        NoteField,
        OptionalText,
        StudentLink,
        ClassLink,
        TeacherLink,
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
    computed: {
        class_admin_page() {
            return 'https://schools.dnevnik.ru/admin/class/class.aspx'
                + `?class=${this.data.dnevnik_id}&school=${SCHOOL_ID}`
        },
        class_page() {
            return `https://schools.dnevnik.ru/class.aspx?class=${this.data.dnevnik_id}`
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#the-class-description {

}
</style>
