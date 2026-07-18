import pyray as rl
from assist.audioAssist import convert_all_progress
from scenes.intro import IntroScene


BAR_WIDTH = 400
BAR_HEIGHT = 30


class LoadingScene:
    def __init__(self):
        self.converter = convert_all_progress()
        self.current = 0
        self.total = 1
        self.status = "Starting..."
        self.converter_done = self.total == 0
        self.done = False
        self.next_scene = None

    def update(self):
        if self.converter_done:
            self.done = True
            self.next_scene = IntroScene()
            return

        try:
            self.current, self.total, self.status = next(self.converter)
        except StopIteration:
            self.converter_done = True

    def draw(self):
        screen_w = rl.get_screen_width()
        screen_h = rl.get_screen_height()

        bar_x = (screen_w - BAR_WIDTH) // 2
        bar_y = screen_h // 2 - BAR_HEIGHT // 2

        rl.draw_rectangle_lines_ex(
            rl.Rectangle(bar_x - 1, bar_y - 1, BAR_WIDTH + 2, BAR_HEIGHT + 2),
            1,
            rl.WHITE,
        )

        progress = self.current / max(self.total, 1)
        fill_w = int(BAR_WIDTH * progress)
        if fill_w > 0:
            rl.draw_rectangle(bar_x, bar_y, fill_w, BAR_HEIGHT, rl.SKYBLUE)

        if self.total > 0:
            pct = int(progress * 100)
            pct_text = f"{pct}%"
        else:
            pct_text = "100%"

        pct_size = 20
        pct_w = rl.measure_text(pct_text, pct_size)
        rl.draw_text(
            pct_text,
            (screen_w - pct_w) // 2,
            bar_y + BAR_HEIGHT + 10,
            pct_size,
            rl.WHITE,
        )

        status_size = 16
        status_w = rl.measure_text(self.status, status_size)
        rl.draw_text(
            self.status,
            (screen_w - status_w) // 2,
            bar_y - 30,
            status_size,
            rl.GRAY,
        )

    def is_done(self):
        return self.done
