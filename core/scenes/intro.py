import pyray as rl
from scenes.menu import MenuScene

WAIT_DURATION = 2.0
FADE_IN_DURATION = 0.5
HOLD_DURATION = 1.0
FADE_OUT_DURATION = 1.0

STATE_WAITING = 0
STATE_FADE_IN = 1
STATE_HOLD = 2
STATE_FADE_OUT = 3
STATE_DONE = 4


class IntroScene:
    def __init__(self):
        self.state = STATE_WAITING
        self.timer = 0.0
        self.alpha = 0.0
        self.next_scene = None

    def update(self):
        dt = rl.get_frame_time()
        self.timer += dt

        if self.state == STATE_WAITING:
            if self.timer >= WAIT_DURATION:
                self.state = STATE_FADE_IN
                self.timer = 0.0

        elif self.state == STATE_FADE_IN:
            progress = min(self.timer / FADE_IN_DURATION, 1.0)
            self.alpha = progress
            if progress >= 1.0:
                self.state = STATE_HOLD
                self.timer = 0.0

        elif self.state == STATE_HOLD:
            if self.timer >= HOLD_DURATION:
                self.state = STATE_FADE_OUT
                self.timer = 0.0

        elif self.state == STATE_FADE_OUT:
            progress = min(self.timer / FADE_OUT_DURATION, 1.0)
            self.alpha = 1.0 - progress
            if progress >= 1.0:
                self.state = STATE_DONE
                self.next_scene = MenuScene()

    def draw(self):
        if self.state == STATE_WAITING or self.alpha <= 0.0:
            return

        text = "Hestie presents"
        font_size = 40
        text_width = rl.measure_text(text, font_size)
        screen_width = rl.get_screen_width()
        screen_height = rl.get_screen_height()

        x = (screen_width - text_width) // 2
        y = screen_height // 2 - font_size // 2

        color = rl.fade(rl.WHITE, self.alpha)
        rl.draw_text(text, x, y, font_size, color)

    def is_done(self):
        return self.state == STATE_DONE
