def listify(my_object):
    """Ensures my_object is a list.
    If it's already a list, return as-is.
    If it's a string, nest it in a list.
    """
    if isinstance(my_object, list):
        return my_object
    else:
        return [my_object]


def dictify(to_convert, old_key, new_key):
    """converts a list of dicts into a dict with key=old_key &
    rename dict[old_key] to dict[new_key]
    """
    new_dict = {}
    for item in to_convert:
        name = item[old_key]
        if new_key:
            item[new_key] = item[old_key]
            del item[old_key]
        new_dict.update({name: item})
    return new_dict
