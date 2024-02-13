def isk_formatter(x):
    if x > 999999999:
        return f"{str(x)[:-9]}kkk"
    elif x > 999999:
        return f"{str(x)[:-6]}kk"
    elif x > 999:
        return f"{str(x)[:-3]}k"
    else:
        return f"{x}"
