from typing import Any


def filter_dict(
    orginal_dict: dict[Any, Any],
    ignore_keys: set[Any] | None = None,
) -> dict[Any, Any]:
    """filter_dict.

    Args:
        orginal_dict (dict[Any, Any]): orginal_dict
        ignore_keys (set[Any] | None): ignore_keys
    """
    ignore_keys = ignore_keys or set()
    return {key: value for key, value in orginal_dict.items() if key not in ignore_keys}


def is_subdict(
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    ignore_keys: set[Any] | None = None,
) -> tuple[bool, Any]:
    """is_subdict.

    Args:
        dict_a (dict[Any, Any]): dict_a
        dict_b (dict[Any, Any]): dict_b
        ignore_keys (set[Any] | None): ignore_keys
    """
    ignore_keys = ignore_keys or set()
    dict_a = filter_dict(dict_a, ignore_keys)
    dict_b = filter_dict(dict_b, ignore_keys)

    for attr, value in dict_a.items():
        if attr not in dict_b:
            return False, attr
        if isinstance(value, dict):
            result, key = is_subdict(value, dict_b[attr])
            if not result:
                return False, key
            continue
        if value != dict_b[attr]:
            return False, attr

    return True, None


def is_equal(
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    ignore_keys: set[Any] | None = None,
) -> tuple[bool, Any]:
    """is_equal.

    Args:
        dict_a (dict[Any, Any]): dict_a
        dict_b (dict[Any, Any]): dict_b
        ignore_keys (set[Any] | None): ignore_keys
    """

    is_a_subdict = is_subdict(dict_a, dict_b, ignore_keys)
    is_b_subdict = is_subdict(dict_b, dict_a, ignore_keys)

    if not is_a_subdict[0]:
        return is_a_subdict

    if not is_b_subdict[0]:
        return is_b_subdict

    return True, None


def merge_dicts(
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    ignore_keys: set[Any] | None = None,
) -> dict[Any, Any]:
    """merge_dicts.

    Args:
        dict_a (dict[Any, Any]): dict_a
        dict_b (dict[Any, Any]): dict_b
        ignore_keys (set[Any] | None): ignore_keys
    """

    if ignore_keys is None:
        ignore_keys = set()

    result = dict_a.copy()
    for key, value in dict_b.items():
        if key in ignore_keys:
            continue
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = merge_dicts(result[key], dict_b[key])
        else:
            result[key] = value

    return result
