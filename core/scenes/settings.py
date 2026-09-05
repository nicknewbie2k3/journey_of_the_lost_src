import pyray as rl

from core.assist.controls import (
    ACTION_LABELS,
    load_controls,
    save_controls,
    default_controls,
    default_das,
    key_name,
)
from core.assist.scaling import scale_f, scale_i, scale_rect

ROW_W = 420
ROW_H = 40
ROW_SPACING = 8
TAB_W = 120
TAB_H = 36
TITLE_Y = 15
TAB_Y = 80
ROWS_TOP = 140


class SettingsScene:
    def __init__(self):
        self.done = False
        self.next_scene = None

        self.controls, self.das = load_controls()
        self.actions = list(ACTION_LABELS.keys())

        self.remapping = None
        self.selected = 0

    def _actions(self):
        return list(ACTION_LABELS.keys())

    def _row_rect(self, index):
        sw = rl.get_screen_width()
        rw = scale_i(ROW_W)
        x = (sw - rw) // 2
        y = scale_i(ROWS_TOP) + index * scale_i(ROW_H + ROW_SPACING)
        return rl.Rectangle(x, y, rw, scale_i(ROW_H))

    def _tab_rect(self, index):
        sw = rl.get_screen_width()
        tw = scale_i(TAB_W)
        x = (sw - 2 * tw) // 2 + index * tw
        return rl.Rectangle(x, scale_i(TAB_Y), tw, scale_i(TAB_H))

    def update(self):
        mouse = rl.get_mouse_position()
        actions = self._actions()

        if self.remapping is not None:
            pressed = rl.get_key_pressed()
            if pressed != 0:
                if pressed == rl.KEY_ESCAPE:
                    self.remapping = None
                else:
                    self.controls[self.remapping] = pressed
                    save_controls(self.controls, self.das)
                    self.remapping = None
                return
            return

        if rl.is_key_pressed(rl.KEY_UP):
            self.selected = (self.selected - 1) % len(actions)
        elif rl.is_key_pressed(rl.KEY_DOWN):
            self.selected = (self.selected + 1) % len(actions)

        for i, action in enumerate(actions):
            if rl.check_collision_point_rec(mouse, self._row_rect(i)):
                self.selected = i

        if rl.is_key_pressed(rl.KEY_ENTER) or (
            rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
            and rl.check_collision_point_rec(mouse, self._row_rect(self.selected))
        ):
            self.remapping = actions[self.selected]

        if rl.is_key_pressed(rl.KEY_BACKSPACE) or rl.is_key_pressed(rl.KEY_ESCAPE):
            self._back_to_menu()

        if rl.is_key_pressed(rl.KEY_R) and (
            rl.is_key_down(rl.KEY_LEFT_CONTROL) or rl.is_key_down(rl.KEY_RIGHT_CONTROL)
        ):
            self.controls = default_controls()
            self.das = default_das()
            save_controls(self.controls, self.das)

    def _back_to_menu(self):
        from core.scenes.menu import MenuScene
        self.done = True
        self.next_scene = MenuScene()

    def draw(self):
        sw = rl.get_screen_width()
        sh = rl.get_screen_height()
        actions = self._actions()

        title_size = scale_i(50)
        title = "Settings"
        tw = rl.measure_text(title, title_size)
        rl.draw_text(title, (sw - tw) // 2, scale_i(TITLE_Y), title_size, rl.WHITE)

        tab = self._tab_rect(0)
        tab_label = "Control"
        tab_label_size = scale_i(22)
        tlw = rl.measure_text(tab_label, tab_label_size)
        rl.draw_text(tab_label, int(tab.x + (tab.width - tlw) // 2), int(tab.y + (tab.height - tab_label_size) // 2), tab_label_size, rl.YELLOW)

        row_h = scale_i(ROW_H)
        for i, action in enumerate(actions):
            rect = self._row_rect(i)
            hovered = rl.check_collision_point_rec(rl.get_mouse_position(), rect)
            selected = i == self.selected
            color = rl.SKYBLUE if selected else (rl.DARKBLUE if hovered else rl.GRAY)
            rl.draw_rectangle_rec(rect, color)
            rl.draw_rectangle_lines_ex(rect, 1, rl.WHITE)

            label = ACTION_LABELS[action]
            label_size = scale_i(20)
            rl.draw_text(label, int(rect.x + scale_f(15)), int(rect.y + (row_h - label_size) // 2), label_size, rl.WHITE)

            value = key_name(self.controls[action])
            value_size = scale_i(20)
            if self.remapping == action:
                value = "Press a key..."
                value_color = rl.YELLOW
            else:
                value_color = rl.LIGHTGRAY
            vw = rl.measure_text(value, value_size)
            rl.draw_text(value, int(rect.x + rect.width - vw - scale_f(15)), int(rect.y + (row_h - value_size) // 2), value_size, value_color)

        hint = "Enter/Click: remap    Esc/Backspace: back    Ctrl+R: reset"
        hint_size = scale_i(14)
        hw = rl.measure_text(hint, hint_size)
        rl.draw_text(hint, (sw - hw) // 2, sh - scale_i(30), hint_size, rl.GRAY)

    def is_done(self):
        return self.done

    def cleanup(self):
        pass
