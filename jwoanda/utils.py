#generator to loop over dictionary
def get_items(dict_object):
    for key in dict_object:
        yield key, dict_object[key]
