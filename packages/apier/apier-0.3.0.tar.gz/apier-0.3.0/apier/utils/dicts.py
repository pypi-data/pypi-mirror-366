from functools import reduce


class _Default:
    """Unique class to signal that no default value has been provided."""

    pass


_default = _Default()


def get_multi_key(d: dict, key: str, separator: str = ".", default=_default):
    """
    Returns the value of the dictionary given by a key, which can define
    multiple levels (e.g. "info.version").

    :param d: The dictionary object.
    :param key: The key of the value that will be returned. It can define
                multiple levels by using a separator (which is '.' by default).
    :param separator: The separator of a multi-level key.
    :param default: The default value that will be returned if the key is not
                    found.
    :return: The value of the given key. It raises a KeyError if the value
             is not found and default is not set.
    """
    try:

        def get_item(a, b):
            if isinstance(a, list):
                b = int(b)
            return a[b]

        return reduce(get_item, key.split(separator), d)
    except KeyError:
        if default != _default:
            return default
        raise KeyError(f"Key '{key}' not found")
    except IndexError:
        if default != _default:
            return default
        raise IndexError(f"Index '{key}' out of range")
