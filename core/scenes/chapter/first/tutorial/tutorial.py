import pyray as rl

from core.game.gameTemplate import GameTemplate
from core.assist.scaling import scale_f, scale_i


class TutorialScene(GameTemplate):
    def __init__(self, level_data=None):
        super().__init__(level_data)

    def update(self):
        super().update()

    def draw(self):
        super().draw()
        self._draw_pause_hint()

    def _draw_pause_hint(self):
        sw = rl.get_screen_width()
        hint = "ESC to pause"
        hint_size = scale_i(14)
        hint_w = rl.measure_text(hint, hint_size)
        rl.draw_text(hint, int(sw - hint_w - scale_f(10)), int(scale_f(10)), hint_size, rl.GRAY)
