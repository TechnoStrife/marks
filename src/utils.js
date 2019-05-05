export function now() {
    return new Date().getTime();
}

export function chunk(arr, length) {
    let r = Array(Math.ceil(arr.length / length)).fill();
    return r.map((e, i) => arr.slice(i * length, i * length + length));
}

export function zip() {
    let arrays;
    if (arguments.length === 0)
        return [];

    if (arguments.length === 1)
        if (arguments[0].length === 1 || !Array.isArray(arguments[0]))
            throw "You must pass at least 2 arrays";
        else
            arrays = arguments[0];
    else
        arrays = [...arguments];

    return Array.apply(null, Array(arrays[0].length)).map(function (_, i) {
        return arrays.map(function (array) {
            return array[i]
        })
    });
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
