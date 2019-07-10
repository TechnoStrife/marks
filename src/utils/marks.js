import {chart_color_sequence, chart_colors} from "@/const"
import {deep_compare, deep_copy, sum} from "@/utils/index"


export const default_options = {
    autoSkip: false,
    tooltips: {
        intersect: false,
        mode: "index",
    },
    scales: {
        yAxes: [
            {
                ticks: {
                    min: 0,
                    max: 5
                }
            }
        ]
    }
}

export function round2(num) {
    return Math.round(num * 100) / 100
}

export function get_mark(mark) {
    return (mark && mark.mark) ? mark.mark : 0
}

export function mark_color(mark) {
    if (mark >= 4.5)
        return chart_colors.green
    else if (mark >= 3.5)
        return chart_colors.green_yellow
    else if (mark >= 2.5)
        return chart_colors.orange
    else
        return chart_colors.red
}

export function color_datasets(datasets, every = false) {
    let color_func
    if (every) {
        color_func = (dataset, i) => {
            let colors = dataset.data.map(mark_color)
            return {
                backgroundColor: colors.map(color => color.background),
                borderColor: colors.map(color => color.border),
            }
        }
    } else {
        color_func = (dataset, i) => ({
            backgroundColor: chart_color_sequence[i].background,
            borderColor: chart_color_sequence[i].border,
        })
    }
    return datasets.map((dataset, i) => ({
        ...dataset,
        ...color_func(dataset, i),
        borderWidth: 1,
    }))
}

export function doughnut_color_datasets(datasets) {
    return datasets.map(dataset => {
        let colors = chart_color_sequence.slice(0, dataset.data.length)
        return {
            ...dataset,
            backgroundColor: colors.map(color => color.background),
            borderColor: colors.map(color => color.border),
            borderWidth: 1,
        }
    })
}


export function default_sort_options(data) {
    let sort_options = [
        {
            key: 'abc',
            text: '{sort_by_alpha}',
            title: 'Сортировка по алфавиту',
            sorter: (a, b) => a.label.localeCompare(b.label),
        }
    ]
    if (data.every(x => /\d{1,2}[А-Я]/.test(x.label))) {
        sort_options[0].sorter = (a, b) => {
            a = a.label
            b = b.label
            let res = parseInt(a.slice(0, -1)) - parseInt(b.slice(0, -1))
            if (res !== 0)
                return res
            return a[a.length - 1].localeCompare(b[b.length - 1])
        }
    }

    if (data.every(x => !!x.group))
        sort_options.push({
            key: 'group',
            text: '{widgets}',
            title: 'По образовательной области предмета',
            sorter: (a, b) => sorter_with_others_group(a.key.type, b.key.type),
        })


    return sort_options
}

export function avg_marks_by_groups(marks, key, groups) {
    let marks_grouped = {}
    for (let group of groups)
        marks_grouped[group] = []
    for (let mark of marks)
        if (mark.mark)
            marks_grouped[key(mark)].push(mark)

    for (let [group_id, group] of Object.entries(marks_grouped)) {
        if (group.length === 0) {
            marks_grouped[group_id] = 0
        } else {
            group = group.map(mark => mark.mark)
            marks_grouped[group_id] = sum(group) / group.length
        }
    }
    return marks_grouped
}

/**
 *
 * @param array {array<T>}
 * @param sort {boolean}
 * @returns {array<T>}
 * @template T
 */
export function distinct(array, sort = true) {
    let res = [...new Set(array)]
    if (sort)
        res.sort((a, b) => a - b)
    return res
}

export function only_data_changed(new_val, old_val) {
    if (!deep_compare(new_val.labels, old_val.labels))
        return false
    if (new_val.datasets.length !== old_val.datasets.length)
        return false
    let new_datasets = deep_copy(new_val.datasets)
    let old_datasets = deep_copy(old_val.datasets)
    let delete_data = x => {
        delete x.data
        delete x.label
    }
    new_datasets.forEach(delete_data)
    old_datasets.forEach(delete_data)
    return deep_compare(new_datasets, old_datasets)
}

export function sorter_with_others_group(a, b) {
    if (a === 'Прочее')
        return 1
    if (b === 'Прочее')
        return -1
    if (a === 'Остальные')
        return 1
    if (b === 'Остальные')
        return -1
    return a.localeCompare(b)
}
