#
# HELPERS
#
def first(value):
    if isinstance(value,tuple) or isinstance(value,list):
        return value[0]
    else:
        return value


def write(*args,**kwargs):
    pass