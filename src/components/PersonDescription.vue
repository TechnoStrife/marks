<template>
    <div class="person-desc">
        <dl>
            <dt>Телефон:</dt>
            <dd>
                <OptionalText hint_text="(неизвестен)">
                    {{ person.tel }}
                </OptionalText>
            </dd>
            <dt>Email:</dt>
            <dd>
                <OptionalText hint_text="(неизвестен)">
                    {{ person.email }}
                </OptionalText>
            </dd>
            <dt>День рождения:</dt>
            <dd>{{ format_date_long(person.birthday) }}</dd>

            <slot/>
        </dl>
        <slot name="after"/>
    </div>
</template>

<script>
import {format_date_long} from "@/utils"
import OptionalText from "@/components/OptionalText"

export default {
    name: "PersonDescription",
    components: {OptionalText},
    props: {
        person: {
            type: Object,
            required: true
        }
    },
    data() {
        return {}
    },
    computed: {},
    methods: {
        format_date_long
    },
}
</script>

<style lang="scss">
.person-desc {

}
</style>
