from typing import Optional, List, Dict


def where_in(ids):
    if isinstance(ids, list):
        _str = ''
        for _id in ids:
            if isinstance(_id, (int, float)):
                _str += "{},".format(_id)
            else:
                _str += "'{}',".format(_id)
        return _str[:-1]
    return ids


def where_simple(condition):
    if isinstance(condition, str):
        return condition

    if isinstance(condition, list):
        return where_complex(condition)

    if isinstance(condition, dict):
        _arr = []
        for k, v in condition.items():
            if type(v) is list:
                _arr.append(f"{k} IN ({where_in(v)})")
            else:
                if isinstance(v, (int, float)):
                    _arr.append(f"{k} = {v}")
                else:
                    _arr.append(f"{k} = '{v}'")
        return ' AND '.join(_arr)


def where_complex(condition):
    """
    [
        'OR',
        [
            'AND',
            {'is_open': 1},
            'is_safe >= 10',
            ['>=', 'id', 100]
        ],
        ['IN', 'device_id', [1, 2, 3]]
    ]
    :return:
    """
    if not isinstance(condition, list):
        return '({})'.format(where_simple(condition))

    operator = condition[0].upper()
    _ = {
        'OR': 1,
        'AND': 1,
        'IN': 1,
        'NOT IN': 1,
        'BETWEEN': 1,
        '=': 1,
        '>': 1,
        '<': 1,
        '>=': 1,
        '<=': 1,
    }[operator]

    if operator in ['=', '>', '<', '>=', '<=']:
        return '({} {} {})'.format(condition[1], operator, condition[2])
    if operator in ['BETWEEN']:
        return '({} {} {} AND {})'.format(condition[1], operator, condition[2], condition[3])
    if operator in ['IN', 'NOT IN']:
        return '({} {} ({}))'.format(condition[1], operator, where_in(condition[2]))

    return '({})'.format(f" {operator} ".join([where_complex(_) for _ in condition[1:]]))


if '__main__' == __name__:
    print(where_simple('id > 0'))
    print(where_simple(dict(a=1, b=2, c=[1, 2, 3])))
    print(where_simple(['BETWEEN', 'id', 1, 100]))
    print(where_simple(['IN', 'id', [1, 100]]))
    print(where_simple(['IN', 'id', ['1', '100']]))
    print(where_simple(['in', 'id', '1,2,3']))

    print(where_simple(
        [
            'OR',
            [
                'AND',
                {'is_open': 1},
                'is_safe >= 10',
                ['>=', 'id', 100]
            ],
            ['IN', 'device_id', [1, 2, 3]]
        ]
    ))

    print(where_simple(
        [
            'AND',
            {'is_open': 1},
            'is_safe >= 10'
        ]
    ))
