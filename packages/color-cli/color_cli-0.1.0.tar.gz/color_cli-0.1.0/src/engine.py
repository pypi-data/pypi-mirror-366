from termcolor import colored


def color_text(text:str,color: str = 'white', attrs: list = None):
    attrs = attrs or []
    return colored(text, color=color, attrs=attrs)
