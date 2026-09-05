import pyray as rl

REF_WIDTH = 800
REF_HEIGHT = 450


def screen_scale():
    sw = rl.get_screen_width()
    sh = rl.get_screen_height()
    return min(sw / REF_WIDTH, sh / REF_HEIGHT)


def scale_f(value):
    return value * screen_scale()


def scale_i(value):
    return int(value * screen_scale())


def scale_rect(x, y, w, h):
    s = screen_scale()
    return rl.Rectangle(int(x * s), int(y * s), int(w * s), int(h * s))
