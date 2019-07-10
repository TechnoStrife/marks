<template>
    <PersonDescription :person="teacher" class="teacher-desc col s12">
        <dt>dnevnik.ru:</dt>
        <dd v-if="teacher.dnevnik_id">
            <a :href="user_link" target="_blank">Пользователь</a>
        </dd>
        <dd>
            <a :href="person_link" target="_blank">Учитель</a>
        </dd>

        <template v-slot:after>
            <hr>
            <div class="head-in-classes" v-if="teacher.head_in_classes.length > 0">
                <p class="ul-title">Классное руководство:</p>
                <ul class="head-teacher-classes dashed">
                    <li v-for="class_ of teacher.head_in_classes">
                        <ClassLink :class_="class_" year/>
                    </li>
                </ul>
            </div>
            <div class="teacher-in-classes">
                <p class="ul-title">Преподаёт в:</p>
                <ul class="dashed">
                    <li v-for="class_ of teacher.classes">
                        <ClassLink :class_="class_" text="? классе" year/>
                    </li>
                </ul>
            </div>
            <hr>
            <div class="teacher-subjects">
                <p class="ul-title">Преподаёт:</p>
                <ul class="browser-default">
                    <li v-for="subjects_group of subjects">
                        <span class="ui-title">{{ subjects_group.type }}</span>
                        <ul class="browser-default">
                            <li v-for="subject of subjects_group.subjects">
                                <router-link :to="`/subject/${subject.id}/`">
                                    {{ subject.name }}
                                </router-link>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </template>
    </PersonDescription>
</template>

<script>
import StudentLink from "@/components/StudentLink"
import OptionalText from "@/components/OptionalText"
import ClassLink from "@/components/ClassLink"
import TeacherLink from "@/components/TeacherLink"
import {SCHOOL_ID} from "@/const"
import PersonDescription from "@/components/PersonDescription"
import {sorter_with_others_group} from "@/utils/marks"
import {key_sorter} from "@/utils"

export default {
    name: "TheTeacherDescription",
    components: {
        OptionalText,
        StudentLink,
        ClassLink,
        TeacherLink,
        PersonDescription,
    },
    props: {
        teacher: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {}
    },
    computed: {
        user_link() {
            return `https://dnevnik.ru/user/user.aspx?user=${this.teacher.dnevnik_id}`
        },
        person_link() {
            return `https://schools.dnevnik.ru/admin/persons/person.aspx`
                + `?person=${this.teacher.dnevnik_person_id}&school=${SCHOOL_ID}`
        },
        subjects() {
            let subjects = {}
            for (let subject of this.teacher.subjects) {
                if (!(subject.type in subjects))
                    subjects[subject.type] = []
                subjects[subject.type].push(subject)
            }
            subjects = Object.entries(subjects)
            subjects.sort(
                ([type1], [type2]) => sorter_with_others_group(type1, type2)
            )
            subjects = subjects.map(([type, subjects]) => ({
                type,
                subjects: subjects.sort(key_sorter(subject => subject.name))
            }))
            return subjects
        },
    },
    methods: {},
}
</script>

<style lang="scss">
.teacher-view {

}
</style>
