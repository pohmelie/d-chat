def apply(fun, *iterables):
    for args in zip(*iterables):
        fun(*args)

def rev(x):
    if type(x) == str:
        return bytes().fromhex(x.replace(" ", ""))
    else:
        return " ".join(map("{:0>2x}".format, x))
