def listify(my_object):
    """Ensures my_object is a list.
    If it's already a list, return as-is.
    If it's a string, nest it in a list.
    """
    if isinstance(my_object, list):
        return my_object
    else:
        return [my_object]
