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
        <div class="subject-classes">
            <p class="ul-title">Изучается в:</p>
            <ul class="classes-groups browser-default">
                <li class="classes-group" v-for="classes of classes_grouped_by_year">
                    <p class="classes-year ul-title">{{ classes[0] }}/{{ classes[0] + 1 }}</p>
                    <ul class="classes dashed browser-default">
                        <li class="class" v-for="class_ of classes[1]">
                            <ClassLink :class_="class_" year/>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import TeacherLink from "@/components/TeacherLink"
import ClassLink from "@/components/ClassLink"
import {key_sorter} from "@/utils"
import {class_name_sorter} from "@/utils/marks"

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
    computed: {
        classes_grouped_by_year() {
            let classes = {}
            for (let class_ of this.data.classes) {
                if (!(class_.year in classes))
                    classes[class_.year] = []
                classes[class_.year].push(class_)
            }
            classes = Object.entries(classes)
            for (let classes_group of classes) {
                classes_group[0] = parseInt(classes_group[0])
                classes_group[1].sort((a, b) => class_name_sorter(a.name, b.name))
            }
            classes.sort(key_sorter(([year]) => -year))
            return classes
        },
    },
    methods: {},
}
</script>

<style lang="scss">
#the-subject-description {
    .subject-classes {
        .classes-group > .classes-year {
            margin: 0;
        }
    }
}
</style>
