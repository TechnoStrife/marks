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
                <a :href="class_page" target="_blank" @click="dnevnik_link">
                    Класс
                </a>
            </dd>
            <dd>
                <a :href="class_admin_page" target="_blank" @click="dnevnik_link">
                    Администрирование
                </a>
            </dd>
            <Modal small
                   :opened="dnevnik_disabled_modal"
                   v-if="!data.dnevnik_id"
                   @close="dnevnik_disabled_modal=false">
                Ссылки на dnevnik.ru в демо-версии недоступны
                <div class="right-button">
                    <button class="btn waves-effect center"
                            @click="dnevnik_disabled_modal=false">
                        ОК
                    </button>
                </div>
            </Modal>
            <!--<div class="data-invalid" v-if="!data.dnevnik_id">
                <i class="material-icons">warning</i>
                Все данные недействительны
            </div>-->
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
import Modal from "@/components/Modal"

export default {
    name: "TheClassDescription",
    components: {
        Modal,
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
        return {
            dnevnik_disabled_modal: false,
        }
    },
    computed: {
        class_admin_page() {
            if (this.data.dnevnik_id)
                return 'https://schools.dnevnik.ru/admin/class/class.aspx'
                    + `?class=${this.data.dnevnik_id}&school=${SCHOOL_ID}`
            else
                return 'https://schools.dnevnik.ru/admin/class/class.aspx'
                    + '?class=18456864&school=1000001567119'
        },
        class_page() {
            if (this.data.dnevnik_id)
                return `https://schools.dnevnik.ru/class.aspx?class=${this.data.dnevnik_id}`
            else
                return 'https://schools.dnevnik.ru/class.aspx?class=18456864'
        },
    },
    methods: {
        dnevnik_link(event) {
            if (this.data.dnevnik_id)
                return
            event.preventDefault()
            this.dnevnik_disabled_modal = true
        }
    },
}
</script>

<style lang="scss">
#the-class-description {

}
</style>
