<template>
    <PersonDescription :person="student" class="student-desc">
        <dt>dnevnik.ru:</dt>
        <dd v-if="student.dnevnik_id">
            <a :href="user_link" target="_blank">Пользователь</a>
        </dd>
        <dd>
            <a :href="person_link" target="_blank" @click="dnevnik_link">Ученик</a>

            <Modal small
                   :opened="dnevnik_disabled_modal"
                   v-if="!student.dnevnik_person_id"
                   @close="dnevnik_disabled_modal=false">
                Ссылки на dnevnik.ru в демо-версии недоступны
                <div class="right-button">
                    <button class="btn waves-effect center"
                            @click="dnevnik_disabled_modal=false">
                        ОК
                    </button>
                </div>
            </Modal>
        </dd>
        <!--<div class="data-invalid" v-if="!student.dnevnik_person_id">
            <i class="material-icons">warning</i>
            Все данные недействительны
        </div>-->
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
import Modal from "@/components/Modal"

export default {
    name: "StudentDescription",
    components: {
        Modal,
        ClassLink,
        OptionalText,
        PersonDescription,

    },
    props: {
        student: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            dnevnik_disabled_modal: false,
        }
    },
    computed: {
        user_link() {
            return `https://dnevnik.ru/user/user.aspx?user=${this.student.dnevnik_id}`
        },
        person_link() {
            if (this.student.dnevnik_person_id)
                return 'https://schools.dnevnik.ru/admin/persons/person.aspx'
                    + `?person=${this.student.dnevnik_person_id}&school=${SCHOOL_ID}`
            else
                return 'https://schools.dnevnik.ru/admin/persons/person.aspx'
                    + '?person=1600397763924&school=1000001567119'
        },
    },
    methods: {
        format_date,
        dnevnik_link(event) {
            if (this.student.dnevnik_person_id)
                return
            event.preventDefault()
            this.dnevnik_disabled_modal = true
        }
    },
}
</script>

<style lang="scss">
.student-desc {

}
</style>
