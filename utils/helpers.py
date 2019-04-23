#
# HELPERS
#
def first(value):
    print(type(value))
    if isinstance(value,tuple) or isinstance(value,list):
        return value[0]
    else:
        return value