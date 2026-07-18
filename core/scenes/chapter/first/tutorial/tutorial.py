import json
import os

import pyray as rl

CONFIG_PATH = os.path.join("core", "config", "config.json")

BUTTON_W = 200
BUTTON_H = 40


class TutorialScene:
    def __init__(self, level_data=None):
        self.done = False
        self.next_scene = None
        self._level = level_data or {}

    def update(self):
        mouse = rl.get_mouse_position()
        bounds = self._skip_bounds()

        if rl.is_key_pressed(rl.KEY_ENTER) or rl.is_key_pressed(rl.KEY_SPACE):
            self._on_skip()
            return

        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT) and rl.check_collision_point_rec(mouse, bounds):
            self._on_skip()

    def _on_skip(self):
        next_name = self._level.get("next_scene", "")
        self._update_config(next_name)
        self.done = True
        if next_name:
            from scenes.storyMode import StoryModeScene
            self.next_scene = StoryModeScene()
        else:
            from scenes.menu import MenuScene
            self.next_scene = MenuScene()

    def _update_config(self, next_scene):
        config = {}
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)

        if next_scene:
            config["current_scene"] = next_scene

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

    def _skip_bounds(self):
        sw = rl.get_screen_width()
        sh = rl.get_screen_height()
        x = (sw - BUTTON_W) // 2
        y = sh // 2 + 40
        return rl.Rectangle(x, y, BUTTON_W, BUTTON_H)

    def draw(self):
        sw = rl.get_screen_width()
        sh = rl.get_screen_height()

        title = "This is a tutorial level"
        title_size = 30
        title_w = rl.measure_text(title, title_size)
        rl.draw_text(title, (sw - title_w) // 2, sh // 2 - 60, title_size, rl.WHITE)

        hint = "Press Enter or click Skip to skip the tutorial"
        hint_size = 18
        hint_w = rl.measure_text(hint, hint_size)
        rl.draw_text(hint, (sw - hint_w) // 2, sh // 2 - 20, hint_size, rl.GRAY)

        bounds = self._skip_bounds()
        mouse = rl.get_mouse_position()
        hovered = rl.check_collision_point_rec(mouse, bounds)

        color = rl.SKYBLUE if hovered else rl.DARKBLUE
        rl.draw_rectangle_rec(bounds, color)
        rl.draw_rectangle_lines_ex(bounds, 1, rl.WHITE)

        label = "Skip"
        label_size = 20
        label_w = rl.measure_text(label, label_size)
        rl.draw_text(
            label,
            int(bounds.x + (bounds.width - label_w) // 2),
            int(bounds.y + (bounds.height - label_size) // 2),
            label_size,
            rl.WHITE,
        )

    def is_done(self):
        return self.done
