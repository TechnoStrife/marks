import Vue from 'vue'

import {library} from '@fortawesome/fontawesome-svg-core'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'

import {faDownload,} from '@fortawesome/free-solid-svg-icons'
import {faFileExcel,} from "@fortawesome/free-regular-svg-icons"

library.add(faFileExcel, faDownload)

Vue.component('font-awesome-icon', FontAwesomeIcon)
