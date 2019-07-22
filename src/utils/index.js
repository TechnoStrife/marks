if (typeof Object.fromEntries !== 'function') {
    Object.fromEntries = function (kv_pairs) {
        let res = {}
        for (let [key, value] of kv_pairs)
            res[key] = value
        return res
    }
}

export function now() {
    return new Date().getTime();
}

export function short_name(full_name) {
    let name = full_name.split(' ')
    name = name[0] + ' ' + name.slice(1).map(name => name[0] + '.').join('')
    return name
}

export function format_date(date) {
    return date && date.toLocaleDateString('ru-RU')
}

export function format_date_long(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }
    return date && date.toLocaleDateString('ru-RU', options)
}

export function slot_not_empty(slot) {
    return Array.isArray(slot) && slot.length > 0 && (typeof slot[0].text !== 'string' || !!slot[0].text.trim())
}

export function id_map(array) {
    return Object.fromEntries(array.map(x => [x.id, x]))
}

export function sum(array) {
    if (array.length === 0)
        return 0
    return array.reduce((sum, x) => sum + x)
}

export function avg(array) {
    array = array.filter(x => x)
    if (array.length === 0)
        return null
    return sum(array) / array.length
}

export function chunk(arr, length) {
    let r = Array(Math.ceil(arr.length / length)).fill();
    return r.map((e, i) => arr.slice(i * length, i * length + length));
}

export function transpose_2d(array) {
    return array[0].map((_, i) => array.map(row => row[i]))
}

export function transpose_array_of_objects(data) {
    return Object.assign(...Array.from(
        new Set(data.reduce((keys, o) => keys.concat(Object.keys(o)), [])),
        key => ({[key]: data.map(o => o[key])})
    ))
}

export function reemit(event, params) {
    this.$emit(event, ...params)
}

export function zip(...arrays) {
    if (arrays.length === 0)
        return

    let min_len = Math.min(...arrays.map(array => array.length))
    let empty_array = Array.apply(null, Array(min_len))
    return empty_array.map((_, i) => arrays.map(array => array[i]))
}

export function zip_longest(...arrays) {
    if (arrays.length === 0)
        return

    let min_len = Math.max(...arrays.map(array => array.length))
    let empty_array = Array.apply(null, Array(min_len))
    return empty_array.map((_, i) => arrays.map(array => array[i]))
}

export function* zip_gen(...arrays) {
    if (arrays.length === 0)
        return

    let len = Math.min(...arrays.map(array => array.length))
    for (let i = 0; i < len; i++) {
        yield arrays.map(array => array[i])
    }
}

export function expand_path(path, object, add_path = true) {
    function join(first, second) {
        const separator = '/';
        const replace = new RegExp(separator + '{1,}', 'g');
        let res = [first, second].join(separator).replace(replace, separator);
        if (res[0] === '/')
            res = res.slice(1);
        if (res[res.length - 1] === '/')
            res = res.slice(0, -1);
        return res;
    }

    if (path === null)
        path = '';

    if (typeof object == "string")
        return join(path, object);

    if (Array.isArray(object)) {
        let new_object = [];
        for (let z = 0; z < object.length; ++z) {
            new_object.push(expand_path(path, object[z]));
        }
        return new_object;
    }

    let new_object = {};
    if (object.types_help)
        object = object.types_help;

    if (add_path) {
        if (object.hasOwnProperty('__path')) {
            path = join(path, object.__path);
            delete object.__path;
        }
        if (path !== '')
            new_object.__path = path;
    }
    for (let key in object) {
        if (object.hasOwnProperty(key)) {
            if (key === 'state') {
                new_object[key] = object[key];
            } else {
                new_object[key] = expand_path(path, object[key], add_path = false);
            }
        }
    }
    return new_object
}

export function deep_copy(val) {
    if (val instanceof Array)
        return val.map(x => deep_copy(x))
    if (val instanceof Object)
        return Object.entries(val).reduce(function (acc, [key, value]) {
            acc[key] = deep_copy(value)
            return acc
        }, {})
    return val
}

export function deep_compare(val1, val2) {
    if (typeof val1 !== typeof val2)
        return false
    if (val1 instanceof Array)
        return val1.length === val2.length && val1.every((x, i) => deep_compare(x, val2[i]))
    if (val1 instanceof Object)
        return deep_compare([...Object.keys(val1)].sort(), [...Object.keys(val2)].sort())
            && Object.entries(val1).every(([key]) => deep_compare(val1[key], val2[key]))
    return val1 === val2
}

export function key_sorter(key) {
    return (a, b) => {
        a = key(a)
        b = key(b)
        if (typeof a === 'string' && typeof b === 'string')
            return a.localeCompare(b)
        return a - b
    }
}
