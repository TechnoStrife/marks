import axios from 'axios'
import * as LosslessJSON from 'lossless-json'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

if (process.env.NODE_ENV === 'development')
    axios.defaults.timeout = Infinity
else
    axios.defaults.timeout = 10 * 1000


export function transform_value(key, value) {
    const date_keys = ['birthday', 'date', 'entered', 'leaved']
    const preserve_keys = ['dnevnik_id', 'dnevnik_person_id']
    const lose_precision_keys = ['avg', 'avg_mark', 'mark', 'terminal_mark', 'diff']

    if (value && date_keys.includes(key))
        return new Date(value)

    if (!value || !value.isLosslessNumber)
        return value

    if (preserve_keys.includes(key))
        return value

    if (lose_precision_keys.includes(key) && /^[+-]?\d+\.\d+(e[+-]\d+)?$/.test(value.value))
        return parseFloat(value.value)

    return value.valueOf()
}

function transform_response(data, headers) {
    try {
        if (headers['content-type'].startsWith('application/json'))
            return LosslessJSON.parse(data, transform_value)
        else
            return data
    } catch (e) {
        console.error(e)
    }
}


export class Api {
    constructor(transform_response) {
        this.res = null
        this.wrong = false
        this.loading = false
        this.error = false
        this.transform_response = transform_response
    }

    async request(url, params = null, data = null) {
        this.loading = true
        this.error = false
        this.wrong = false
        if (url.length > 0 && url[url.length - 1] === '/')
            url = url.slice(0, -1)
        try {
            let res = await axios({
                method: data ? 'post' : 'get',
                url: '/marks/api' + url  + '.json',
                params,
                data,
                transformResponse: transform_response
            })
            if (typeof this.transform_response === 'function')
                res.data = this.transform_response(res.data)
            this.res = res
            this.loading = false
            if (!this.res.data.success)
                this.wrong = true
        } catch (e) {
            this.loading = false
            this.error = true
            console.error(e)
        }
    }
}
