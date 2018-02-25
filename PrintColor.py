class PrintColor(object):
    _red = '\033[91m'
    _yellow = '\033[93m'
    _green = '\033[92m'
    _blue = '\033[94m'
    _bold = '\033[1m'
    _underline = '\033[4m'
    _HEADER = '\033[95m'
    _end = '\033[0m'

    name = "PrintColor"

    def __init__(self):
        print("PrintColor __init__")

    @classmethod
    def generic(cls, type, string, end = "\n"):
        color_string = type + string + cls._end
        print(color_string, end=end, flush=True)

    @classmethod
    def red(cls, string, end = "\n"):
        cls.generic(cls._red, string, end)

    @classmethod
    def yellow(cls, string, end = "\n"):
        cls.generic(cls._yellow, string, end)

    @classmethod
    def green(cls, string, end = "\n"):
        cls.generic(cls._green, string, end)

    @classmethod
    def blue(cls, string, end = "\n"):
        cls.generic(cls._blue, string, end)

    @classmethod
    def bold(cls, string, end="\n"):
        cls.generic(cls._bold, string, end)