import os

import pyray as rl

from core.assist.paths import AUDIO_DIR
from core.assist.scaling import scale_f, scale_i

BUTTON_W = 250
BUTTON_H = 40
START_Y = 170
SPACING = 60
TITLE_SIZE = 60
TITLE_Y = 60
FONT_SIZE = 30


class MenuScene:
    def __init__(self):
        self.selected_index = 0
        self.done = False
        self.next_scene = None

        self.buttons = [
            {"label": "Story Mode", "enabled": True},
            {"label": "Online Mode", "enabled": False},
            {"label": "Settings", "enabled": True},
            {"label": "Quit", "enabled": True},
        ]

        self.music = rl.load_music_stream(os.path.join(AUDIO_DIR, "MenuBGM.wav"))
        rl.set_music_volume(self.music, 0.5)
        rl.play_music_stream(self.music)

        self._skip_to_enabled()

    def _skip_to_enabled(self):
        while not self.buttons[self.selected_index]["enabled"]:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)

    def _get_button_bounds(self, index):
        screen_width = rl.get_screen_width()
        button_width = scale_i(BUTTON_W)
        button_height = scale_i(BUTTON_H)
        x = (screen_width - button_width) // 2
        y = scale_i(START_Y) + index * scale_i(SPACING)
        return rl.Rectangle(x, y, button_width, button_height)

    def update(self):
        rl.update_music_stream(self.music)

        mouse_pos = rl.get_mouse_position()

        if rl.is_key_pressed(rl.KEY_UP):
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self._skip_to_enabled()
        elif rl.is_key_pressed(rl.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self._skip_to_enabled()

        for i, btn in enumerate(self.buttons):
            if btn["enabled"] and rl.check_collision_point_rec(mouse_pos, self._get_button_bounds(i)):
                self.selected_index = i

        if self.buttons[self.selected_index]["enabled"]:
            bounds = self._get_button_bounds(self.selected_index)
            clicked = (
                rl.is_key_pressed(rl.KEY_ENTER)
                or (
                    rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
                    and rl.check_collision_point_rec(mouse_pos, bounds)
                )
            )
            if clicked:
                self.done = True
                label = self.buttons[self.selected_index]["label"]
                if label == "Quit":
                    self.next_scene = None
                elif label == "Story Mode":
                    from core.scenes.storyMode import StoryModeScene
                    self.next_scene = StoryModeScene()
                elif label == "Settings":
                    from core.scenes.settings import SettingsScene
                    self.next_scene = SettingsScene()

    def draw(self):
        title = "HESTIE"
        title_size = scale_i(TITLE_SIZE)
        screen_width = rl.get_screen_width()
        title_w = rl.measure_text(title, title_size)
        rl.draw_text(title, (screen_width - title_w) // 2, scale_i(TITLE_Y), title_size, rl.WHITE)

        for i, btn in enumerate(self.buttons):
            bounds = self._get_button_bounds(i)
            font_size = scale_i(FONT_SIZE)

            if not btn["enabled"]:
                color = rl.DARKGRAY
            elif i == self.selected_index:
                color = rl.YELLOW
            else:
                color = rl.WHITE

            text_w = rl.measure_text(btn["label"], font_size)
            rx = int(bounds.x + (bounds.width - text_w) / 2)
            ry = int(bounds.y + (bounds.height - font_size) / 2)

            if i == self.selected_index and btn["enabled"]:
                rl.draw_text(">", int(rx - scale_f(20)), ry, font_size, rl.YELLOW)

            rl.draw_text(btn["label"], rx, ry, font_size, color)

    def is_done(self):
        return self.done

    def cleanup(self):
        rl.stop_music_stream(self.music)
        rl.unload_music_stream(self.music)
