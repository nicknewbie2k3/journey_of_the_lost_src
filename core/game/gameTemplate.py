import json
import os

import pyray as rl

from core.assist.paths import CONFIG_PATH, AUDIO_DIR
from core.assist.controls import load_controls, default_das


class GameTemplate:
    BOARD_W = 10
    BOARD_H = 20
    CELL_SIZE = 28
    BOARD_OFFSET_X = 30
    BOARD_OFFSET_Y = 50

    PIECES = {
        "I": {
            "shapes": [
                [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
                [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],
                [[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]],
                [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
            ],
            "color": rl.SKYBLUE,
        },
        "O": {
            "shapes": [
                [[1,1],[1,1]],
                [[1,1],[1,1]],
                [[1,1],[1,1]],
                [[1,1],[1,1]],
            ],
            "color": rl.YELLOW,
        },
        "T": {
            "shapes": [
                [[0,1,0],[1,1,1],[0,0,0]],
                [[0,1,0],[0,1,1],[0,1,0]],
                [[0,0,0],[1,1,1],[0,1,0]],
                [[0,1,0],[1,1,0],[0,1,0]],
            ],
            "color": rl.PURPLE,
        },
        "S": {
            "shapes": [
                [[0,1,1],[1,1,0],[0,0,0]],
                [[0,1,0],[0,1,1],[0,0,1]],
                [[0,0,0],[0,1,1],[1,1,0]],
                [[1,0,0],[1,1,0],[0,1,0]],
            ],
            "color": rl.GREEN,
        },
        "Z": {
            "shapes": [
                [[1,1,0],[0,1,1],[0,0,0]],
                [[0,0,1],[0,1,1],[0,1,0]],
                [[0,0,0],[1,1,0],[0,1,1]],
                [[0,1,0],[1,1,0],[1,0,0]],
            ],
            "color": rl.RED,
        },
        "J": {
            "shapes": [
                [[1,0,0],[1,1,1],[0,0,0]],
                [[0,1,1],[0,1,0],[0,1,0]],
                [[0,0,0],[1,1,1],[0,0,1]],
                [[0,1,0],[0,1,0],[1,1,0]],
            ],
            "color": rl.BLUE,
        },
        "L": {
            "shapes": [
                [[0,0,1],[1,1,1],[0,0,0]],
                [[0,1,0],[0,1,0],[0,1,1]],
                [[0,0,0],[1,1,1],[1,0,0]],
                [[1,1,0],[0,1,0],[0,1,0]],
            ],
            "color": rl.ORANGE,
        },
    }

    WALL_KICKS_SRS = {
        "JLSTZ": {
            "0->1": [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
            "1->0": [[0,0],[1,0],[1,-1],[0,2],[1,2]],
            "1->2": [[0,0],[1,0],[1,-1],[0,2],[1,2]],
            "2->1": [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
            "2->3": [[0,0],[1,0],[1,1],[0,-2],[1,-2]],
            "3->2": [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
            "3->0": [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
            "0->3": [[0,0],[1,0],[1,1],[0,-2],[1,-2]],
        },
        "I": {
            "0->1": [[0,0],[-2,0],[1,0],[-2,-1],[1,2]],
            "1->0": [[0,0],[2,0],[-1,0],[2,1],[-1,-2]],
            "1->2": [[0,0],[-1,0],[2,0],[-1,2],[2,-1]],
            "2->1": [[0,0],[1,0],[-2,0],[1,-2],[-2,1]],
            "2->3": [[0,0],[2,0],[-1,0],[2,1],[-1,-2]],
            "3->2": [[0,0],[-2,0],[1,0],[-2,-1],[1,2]],
            "3->0": [[0,0],[1,0],[-2,0],[1,-2],[-2,1]],
            "0->3": [[0,0],[-1,0],[2,0],[-1,2],[2,-1]],
        },
    }

    def __init__(self, level_data=None):
        self.done = False
        self.next_scene = None
        self._level = level_data or {}

        self.board = [[None for _ in range(self.BOARD_W)] for _ in range(self.BOARD_H)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.game_won = False

        self.piece_types = list(self.PIECES.keys())
        self.bag = []
        self.current_piece = None
        self.current_pos = (0, 0)
        self.current_rot = 0
        self.next_piece = None

        self.drop_timer = 0.0
        self.drop_interval = 0.8
        self.soft_drop_interval = 0.05
        self.soft_dropping = False
        self.das_timer = 0.0
        self.das_delay = 0.17
        self.das_interval = 0.05
        self.das_teleport = True
        self.move_dir = 0
        self.last_move_time = 0.0

        self.lock_delay = 1.0
        self.lock_timer = 0.0
        self.is_locked = False

        self.clear_delay = 0.5
        self.clear_timer = 0.0
        self.clear_rows = []
        self.spawn_delay = 0.1
        self.spawn_timer = 0.0
        self.game_state = "play"
        self.last_clear_type = None
        self.last_clear_timer = 0.0
        self.last_clear_duration = 1.0
        self.back_to_back = False
        self.last_clear_b2b = False
        self.was_rotated = False
        self.last_kick_1x2 = False
        self.last_tspin = False
        self.clear_stats = {
            "single": 0,
            "double": 0,
            "triple": 0,
            "quad": 0,
            "tspin_single": 0,
            "tspin_double": 0,
            "tspin_triple": 0,
            "tspin_quad": 0,
            "tspin_mini_single": 0,
            "tspin_mini_double": 0,
            "tspin_mini_triple": 0,
            "tspin_mini_quad": 0,
        }

        self.hold_piece = None
        self.can_hold = True

        self.paused = False
        self.pause_selection = 0
        self.pause_options = ["Resume", "Settings", "Main Menu", "Quit"]

        self.controls, self.das = load_controls()
        self.das_delay = self.das.get("das_delay", default_das()["das_delay"])
        self.das_teleport = self.das.get("das_teleport", default_das()["das_teleport"])

        self.music = None
        self.music_duration = 0.0
        self.music_elapsed = 0.0
        self.start_time = None

        music_file = self._level.get("music", "HOANG - ARE YOU STILL THERE (OFFICIAL AUDIO).wav")
        music_path = os.path.join(AUDIO_DIR, music_file)
        if os.path.isfile(music_path):
            self.music = rl.load_music_stream(music_path)
            self.music_duration = rl.get_music_time_length(self.music)
            rl.set_music_volume(self.music, 0.8)
            rl.play_music_stream(self.music)

        self._refill_bag()
        self._spawn_next_piece()

    def _refill_bag(self):
        import random
        self.bag = self.piece_types[:]
        random.shuffle(self.bag)

    def _spawn_next_piece(self):
        if self.next_piece is None:
            self.next_piece = self._get_next_from_bag()
        self.current_piece = self.next_piece
        self.current_rot = 0
        shape = self.PIECES[self.current_piece]["shapes"][0]
        self.current_pos = (self.BOARD_W // 2 - len(shape[0]) // 2, 0)
        if not self._is_valid_pos(self.current_pos, self.current_rot):
            self.game_over = True
        self.next_piece = self._get_next_from_bag()
        self.lock_timer = 0.0
        self.is_locked = False
        self.can_hold = True
        self.was_rotated = False
        self.last_kick_1x2 = False

    def _get_next_from_bag(self):
        if not self.bag:
            self._refill_bag()
        return self.bag.pop() if self.bag else self.piece_types[0]

    def _is_valid_pos(self, pos, rot, piece=None):
        p = piece or self.current_piece
        shape = self.PIECES[p]["shapes"][rot]
        bx, by = pos
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    gx = bx + x
                    gy = by + y
                    if gx < 0 or gx >= self.BOARD_W or gy >= self.BOARD_H:
                        return False
                    if gy >= 0 and self.board[gy][gx] is not None:
                        return False
        return True

    def _get_shape(self, piece=None, rot=None):
        p = piece or self.current_piece
        r = rot if rot is not None else self.current_rot
        return self.PIECES[p]["shapes"][r]

    def _try_move(self, dx, dy):
        nx, ny = self.current_pos[0] + dx, self.current_pos[1] + dy
        if self._is_valid_pos((nx, ny), self.current_rot):
            self.current_pos = (nx, ny)
            return True
        return False

    def _rotate(self, direction):
        new_rot = (self.current_rot + direction) % 4
        key = f"{self.current_rot}->{new_rot}"
        kick_table = self.WALL_KICKS_SRS.get("I" if self.current_piece == "I" else "JLSTZ")
        kicks = kick_table.get(key, [[0, 0]]) if kick_table else [[0, 0]]
        for dx, dy in kicks:
            if self._is_valid_pos((self.current_pos[0] + dx, self.current_pos[1] - dy), new_rot):
                self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] - dy)
                self.current_rot = new_rot
                self.was_rotated = True
                self.last_kick_1x2 = abs(dx) == 1 and abs(dy) == 2
                return True
        return False

    def _hold(self):
        if not self.can_hold or self.current_piece is None:
            return
        if self.hold_piece is None:
            self.hold_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self._get_next_from_bag()
        else:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
        self.current_rot = 0
        shape = self.PIECES[self.current_piece]["shapes"][0]
        self.current_pos = (self.BOARD_W // 2 - len(shape[0]) // 2, 0)
        if not self._is_valid_pos(self.current_pos, self.current_rot):
            self.game_over = True
        self.lock_timer = 0.0
        self.is_locked = False
        self.can_hold = False

    def _find_ghost_pos(self):
        cx, cy = self.current_pos
        while self._is_valid_pos((cx, cy + 1), self.current_rot):
            cy += 1
        return (cx, cy)

    def _hard_drop(self):
        drop_distance = 0
        while self._try_move(0, 1):
            drop_distance += 1
        self._lock_piece()
        self.score += drop_distance * 2

    def _lock_piece(self):
        shape = self._get_shape()
        color = self.PIECES[self.current_piece]["color"]
        bx, by = self.current_pos
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    gy = by + y
                    gx = bx + x
                    if 0 <= gy < self.BOARD_H and 0 <= gx < self.BOARD_W:
                        self.board[gy][gx] = color
        tspin = self._is_tspin()
        self.last_tspin = tspin
        self.current_piece = None
        self.clear_rows = self._find_full_rows()
        if self.clear_rows:
            self.game_state = "clearing"
            self.clear_timer = 0.0
        else:
            self.game_state = "spawning"
            self.spawn_timer = 0.0

    def _is_tspin(self):
        if self.current_piece != "T" or not self.was_rotated:
            return False
        bx, by = self.current_pos
        corners = [
            (bx, by),
            (bx + 2, by),
            (bx, by + 2),
            (bx + 2, by + 2),
        ]
        front = {
            0: [(bx, by), (bx + 2, by)],
            1: [(bx + 2, by), (bx + 2, by + 2)],
            2: [(bx, by + 2), (bx + 2, by + 2)],
            3: [(bx, by), (bx, by + 2)],
        }[self.current_rot]
        back = [c for c in corners if c not in front]

        def occupied(pos):
            cx, cy = pos
            if cx < 0 or cx >= self.BOARD_W or cy < 0 or cy >= self.BOARD_H:
                return True
            return self.board[cy][cx] is not None

        front_occ = sum(1 for c in front if occupied(c))
        back_occ = sum(1 for c in back if occupied(c))
        total_occ = front_occ + back_occ
        if total_occ < 3:
            return False
        if front_occ == 2:
            return "full"
        if front_occ == 1 and back_occ == 2:
            if self.last_kick_1x2:
                return "full"
            return "mini"
        return False

    def _find_full_rows(self):
        return [y for y in range(self.BOARD_H) if all(cell is not None for cell in self.board[y])]

    def _finish_clear(self):
        cleared = len(self.clear_rows)
        self.lines_cleared += cleared
        empty_rows = [[None for _ in range(self.BOARD_W)] for _ in range(cleared)]
        self.board = empty_rows + [row for y, row in enumerate(self.board) if y not in self.clear_rows]
        clear_type = self._classify_clear(cleared)
        is_b2b_type = clear_type in (
            "tspin_single", "tspin_double", "tspin_triple", "tspin_quad",
            "tspin_mini_single", "tspin_mini_double", "tspin_mini_triple", "tspin_mini_quad",
            "quad",
        )
        b2b = self.back_to_back and is_b2b_type
        points = [0, 100, 300, 500, 800]
        base = points[min(cleared, 4)]
        if self.last_tspin == "full":
            base *= 2
        if b2b:
            base = int(base * 1.5)
        self.score += base * (self.lines_cleared // 10 + 1)
        self.back_to_back = is_b2b_type
        self.last_clear_type = clear_type
        self.last_clear_b2b = b2b
        if clear_type:
            self.clear_stats[clear_type] = self.clear_stats.get(clear_type, 0) + 1
            self.last_clear_timer = self.last_clear_duration
        self.clear_rows = []
        self.game_state = "spawning"
        self.spawn_timer = 0.0

    def _classify_clear(self, cleared):
        if cleared <= 0:
            return None
        if self.last_tspin == "full":
            mapping = {1: "tspin_single", 2: "tspin_double", 3: "tspin_triple", 4: "tspin_quad"}
        elif self.last_tspin == "mini":
            mapping = {1: "tspin_mini_single", 2: "tspin_mini_double", 3: "tspin_mini_triple", 4: "tspin_mini_quad"}
        else:
            mapping = {1: "single", 2: "double", 3: "triple", 4: "quad"}
        return mapping.get(cleared)

    def update(self):
        if self.game_over or self.game_won:
            return

        if self.paused:
            self._handle_pause_input()
            return

        if self.music:
            rl.update_music_stream(self.music)
            self.music_elapsed = rl.get_music_time_played(self.music)
            if self.music_elapsed >= self.music_duration - 0.1:
                self.game_won = True
                return

        mouse = rl.get_mouse_position()
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT) and rl.check_collision_point_rec(mouse, self._pause_button_rect()):
            self.paused = True
            return

        dt = rl.get_frame_time()

        if self.last_clear_timer > 0.0:
            self.last_clear_timer -= dt
            if self.last_clear_timer <= 0.0:
                self.last_clear_type = None

        if self.game_state == "clearing":
            self.clear_timer += dt
            if self.clear_timer >= self.clear_delay:
                self._finish_clear()
            return

        if self.game_state == "spawning":
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.game_state = "play"
                self._spawn_next_piece()
            return

        self._handle_input(dt)

        if self.game_state != "play" or self.current_piece is None:
            return

        interval = self.soft_drop_interval if self.soft_dropping else self.drop_interval
        self.drop_timer += dt
        if self.drop_timer >= interval:
            self.drop_timer = 0.0
            moved = self._try_move(0, 1)
            if moved:
                self.lock_timer = 0.0
                self.is_locked = False
            else:
                self._handle_lock_delay(dt)

    def _handle_lock_delay(self, dt):
        if self.is_locked:
            return
        self.lock_timer += dt
        if self.lock_timer >= self.lock_delay:
            self._lock_piece()

    def _handle_pause_input(self):
        mouse = rl.get_mouse_position()

        if rl.is_key_pressed(rl.KEY_ESCAPE) or (
            rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
            and rl.check_collision_point_rec(mouse, self._pause_button_rect())
        ):
            self.paused = False
            return

        if rl.is_key_pressed(rl.KEY_UP):
            self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)
        elif rl.is_key_pressed(rl.KEY_DOWN):
            self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)

        for i, option in enumerate(self.pause_options):
            if rl.check_collision_point_rec(mouse, self._pause_option_rect(i)):
                self.pause_selection = i

        selected = (
            rl.is_key_pressed(rl.KEY_ENTER)
            or (
                rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT)
                and rl.check_collision_point_rec(mouse, self._pause_option_rect(self.pause_selection))
            )
        )
        if selected:
            self._pause_select(self.pause_options[self.pause_selection])

    def _pause_select(self, option):
        if option == "Resume":
            self.paused = False
        elif option == "Settings":
            from core.scenes.settings import SettingsScene
            self.done = True
            self.next_scene = SettingsScene()
        elif option == "Main Menu":
            from core.scenes.menu import MenuScene
            self.done = True
            self.next_scene = MenuScene()
        elif option == "Quit":
            self.done = True
            self.next_scene = None

    def _pause_option_rect(self, index):
        sw = rl.get_screen_width()
        sh = rl.get_screen_height()
        w = int(sw * 0.4)
        h = int(sh * 0.09)
        total = len(self.pause_options) * h
        x = (sw - w) // 2
        y = (sh - total) // 2 + index * h
        return rl.Rectangle(x, y, w, h)

    def _pause_button_rect(self):
        sw = rl.get_screen_width()
        w = int(sw * 0.12)
        h = int(sw * 0.05)
        x = 15
        y = 15
        return rl.Rectangle(x, y, w, h)

    def _handle_input(self, dt):
        if rl.is_key_pressed(rl.KEY_ESCAPE):
            self.paused = True
            return

        c = self.controls
        self.soft_dropping = rl.is_key_down(c["soft_drop"])

        if rl.is_key_pressed(c["rotate_cw"]):
            if self._rotate(1):
                self.lock_timer = 0.0
                self.is_locked = False
        if rl.is_key_pressed(c["rotate_ccw"]):
            if self._rotate(-1):
                self.lock_timer = 0.0
                self.is_locked = False
        if rl.is_key_pressed(c["hard_drop"]):
            self._hard_drop()
            return
        if rl.is_key_pressed(c["hold"]):
            self._hold()

        left = rl.is_key_down(c["move_left"])
        right = rl.is_key_down(c["move_right"])
        new_dir = (1 if right else 0) - (1 if left else 0)

        if new_dir != self.move_dir:
            self.move_dir = new_dir
            self.das_timer = 0.0
            if self.move_dir != 0:
                if self._try_move(self.move_dir, 0):
                    self.lock_timer = 0.0
                    self.is_locked = False
        elif self.move_dir != 0:
            self.das_timer += dt
            if self.das_timer >= self.das_delay:
                if self.das_teleport:
                    while self._try_move(self.move_dir, 0):
                        self.lock_timer = 0.0
                        self.is_locked = False
                    self.das_timer = 0.0
                else:
                    elapsed = self.das_timer - self.das_delay
                    moves = int(elapsed / self.das_interval) + 1
                    for _ in range(moves):
                        if not self._try_move(self.move_dir, 0):
                            break
                        self.lock_timer = 0.0
                        self.is_locked = False
                    self.das_timer = self.das_delay + (elapsed % self.das_interval)

    def draw(self):
        sw = rl.get_screen_width()
        sh = rl.get_screen_height()

        header_h = 90
        avail_w = sw
        avail_h = sh - header_h

        cell_size = int(min(avail_w / self.BOARD_W, avail_h / self.BOARD_H) * 0.9)
        cell_size = max(cell_size, 12)

        board_w_px = self.BOARD_W * cell_size
        board_h_px = self.BOARD_H * cell_size
        bx = (sw - board_w_px) // 2
        by = header_h + (avail_h - board_h_px) // 2

        score_size = max(14, int(cell_size * 0.6))
        score_text = f"SCORE: {self.score}"
        rl.draw_text(score_text, bx + board_w_px - 220, 15, score_size, rl.YELLOW)
        lines_text = f"LINES: {self.lines_cleared}"
        rl.draw_text(lines_text, bx + board_w_px - 220, 15 + score_size + 4, max(12, score_size - 2), rl.LIGHTGRAY)

        if self.music and self.music_duration > 0:
            remaining = max(0, self.music_duration - self.music_elapsed)
            time_text = f"TIME: {int(remaining // 60)}:{int(remaining % 60):02d}"
            rl.draw_text(time_text, bx + board_w_px - 220, 15 + score_size * 2 + 10, max(12, score_size - 2), rl.LIGHTGRAY)

        if self.last_clear_type and self.last_clear_timer > 0.0:
            name_map = {
                "single": ("SINGLE", None),
                "double": ("DOUBLE", None),
                "triple": ("TRIPLE", None),
                "quad": ("QUAD", None),
                "tspin_single": ("Tspin", "single"),
                "tspin_double": ("Tspin", "double"),
                "tspin_triple": ("Tspin", "triple"),
                "tspin_quad": ("Tspin", "quad"),
                "tspin_mini_single": ("Tspin", "mini"),
                "tspin_mini_double": ("Tspin", "mini double"),
                "tspin_mini_triple": ("Tspin", "mini triple"),
                "tspin_mini_quad": ("Tspin", "mini quad"),
            }
            line1, line2 = name_map[self.last_clear_type]
            last_size = max(12, score_size - 2)
            x = bx + board_w_px - 220
            y = 15 + score_size * 2 + 10 + score_size
            rl.draw_text(line1, x, y, last_size, rl.MAGENTA)
            if line2:
                rl.draw_text(line2, x, y + last_size + 2, last_size, rl.MAGENTA)
            if self.last_clear_b2b:
                b2b_y = y + last_size + 2 + (last_size + 2 if line2 else 0)
                rl.draw_text("Back-to-Back", x, b2b_y, last_size, rl.GOLD)

        self._draw_pause_button()

        preview_label_size = max(12, int(cell_size * 0.5))
        preview_cell = max(10, cell_size - 6)
        panel_w = 4 * preview_cell + 8
        panel_h = 4 * preview_cell + 8

        hold_panel_x = bx
        hold_panel_y = by - panel_h
        rl.draw_rectangle_rec(rl.Rectangle(hold_panel_x, hold_panel_y, panel_w, panel_h), rl.fade(rl.DARKGRAY, 0.3))
        rl.draw_rectangle_lines_ex(rl.Rectangle(hold_panel_x, hold_panel_y, panel_w, panel_h), 1, rl.LIGHTGRAY)
        rl.draw_text("HOLD", int(hold_panel_x + 4), int(hold_panel_y + 4), preview_label_size, rl.LIGHTGRAY)
        if self.hold_piece:
            hold_shape = self.PIECES[self.hold_piece]["shapes"][0]
            hold_color = self.PIECES[self.hold_piece]["color"]
            hold_bx = hold_panel_x + 4
            hold_by = hold_panel_y + preview_label_size + 12
            offset_x = (4 - len(hold_shape[0])) * preview_cell // 2
            offset_y = (4 - len(hold_shape)) * preview_cell // 2
            for y in range(len(hold_shape)):
                for x in range(len(hold_shape[y])):
                    if hold_shape[y][x]:
                        px = hold_bx + offset_x + x * preview_cell
                        py = hold_by + offset_y + y * preview_cell
                        rect = rl.Rectangle(px, py, preview_cell - 1, preview_cell - 1)
                        rl.draw_rectangle_rec(rect, hold_color)

        next_panel_x = bx + board_w_px - panel_w
        next_panel_y = by - panel_h
        rl.draw_rectangle_rec(rl.Rectangle(next_panel_x, next_panel_y, panel_w, panel_h), rl.fade(rl.DARKGRAY, 0.3))
        rl.draw_rectangle_lines_ex(rl.Rectangle(next_panel_x, next_panel_y, panel_w, panel_h), 1, rl.LIGHTGRAY)
        rl.draw_text("NEXT", int(next_panel_x + 4), int(next_panel_y + 4), preview_label_size, rl.LIGHTGRAY)
        if self.next_piece:
            next_shape = self.PIECES[self.next_piece]["shapes"][0]
            next_color = self.PIECES[self.next_piece]["color"]
            preview_bx = next_panel_x + 4
            preview_by = next_panel_y + preview_label_size + 12
            offset_x = (4 - len(next_shape[0])) * preview_cell // 2
            offset_y = (4 - len(next_shape)) * preview_cell // 2
            for y in range(len(next_shape)):
                for x in range(len(next_shape[y])):
                    if next_shape[y][x]:
                        px = preview_bx + offset_x + x * preview_cell
                        py = preview_by + offset_y + y * preview_cell
                        rect = rl.Rectangle(px, py, preview_cell - 1, preview_cell - 1)
                        rl.draw_rectangle_rec(rect, next_color)

        gap = max(1, cell_size // 20)
        flash_on = self.game_state == "clearing" and (int(self.clear_timer * 20) % 2 == 0)
        for y in range(self.BOARD_H):
            for x in range(self.BOARD_W):
                cell = self.board[y][x]
                rect = rl.Rectangle(bx + x * cell_size, by + y * cell_size, cell_size - gap, cell_size - gap)
                if cell:
                    if y in self.clear_rows and flash_on:
                        rl.draw_rectangle_rec(rect, rl.WHITE)
                    else:
                        rl.draw_rectangle_rec(rect, cell)
                rl.draw_rectangle_lines_ex(rect, 1, rl.DARKGRAY)

        if self.current_piece and not self.game_over:
            ghost_pos = self._find_ghost_pos()
            shape = self._get_shape()
            color = self.PIECES[self.current_piece]["color"]
            ghost_color = rl.fade(color, 0.25)
            gpx, gpy = ghost_pos
            for y in range(len(shape)):
                for x in range(len(shape[y])):
                    if shape[y][x]:
                        gx = bx + (gpx + x) * cell_size
                        gy = by + (gpy + y) * cell_size
                        rect = rl.Rectangle(gx, gy, cell_size - gap, cell_size - gap)
                        rl.draw_rectangle_rec(rect, ghost_color)

            px, py = self.current_pos
            for y in range(len(shape)):
                for x in range(len(shape[y])):
                    if shape[y][x]:
                        gx = bx + (px + x) * cell_size
                        gy = by + (py + y) * cell_size
                        rect = rl.Rectangle(gx, gy, cell_size - gap, cell_size - gap)
                        rl.draw_rectangle_rec(rect, color)

        overlay_y = by + board_h_px // 2 - 40
        if self.game_over:
            msg = "GAME OVER"
            msg_size = max(20, cell_size * 2)
            mw = rl.measure_text(msg, msg_size)
            rl.draw_text(msg, (sw - mw) // 2, overlay_y, msg_size, rl.RED)
            sub = "Press ENTER to continue"
            sub_size = max(14, cell_size)
            sw2 = rl.measure_text(sub, sub_size)
            rl.draw_text(sub, (sw - sw2) // 2, overlay_y + msg_size + 10, sub_size, rl.WHITE)
            if rl.is_key_pressed(rl.KEY_ENTER):
                self._complete()
        elif self.game_won:
            msg = "TIME'S UP!"
            msg_size = max(20, cell_size * 2)
            mw = rl.measure_text(msg, msg_size)
            rl.draw_text(msg, (sw - mw) // 2, overlay_y, msg_size, rl.GREEN)
            final = f"Final Score: {self.score}  Lines: {self.lines_cleared}"
            sub_size = max(14, cell_size)
            tw = rl.measure_text(final, sub_size)
            rl.draw_text(final, (sw - tw) // 2, overlay_y + msg_size + 10, sub_size, rl.YELLOW)
            sub = "Press ENTER to continue"
            sw2 = rl.measure_text(sub, sub_size)
            rl.draw_text(sub, (sw - sw2) // 2, overlay_y + msg_size + 10 + sub_size + 8, sub_size, rl.WHITE)
            if rl.is_key_pressed(rl.KEY_ENTER):
                self._complete()

        if self.paused:
            self._draw_pause_menu(sw, sh)

    def _draw_pause_button(self):
        rect = self._pause_button_rect()
        hovered = rl.check_collision_point_rec(rl.get_mouse_position(), rect)
        color = rl.SKYBLUE if hovered else rl.DARKBLUE
        rl.draw_rectangle_rec(rect, color)
        rl.draw_rectangle_lines_ex(rect, 1, rl.WHITE)

        label = "II"
        label_size = int(rect.height * 0.6)
        lw = rl.measure_text(label, label_size)
        rl.draw_text(
            label,
            int(rect.x + (rect.width - lw) // 2),
            int(rect.y + (rect.height - label_size) // 2),
            label_size,
            rl.WHITE,
        )

    def _draw_pause_menu(self, sw, sh):
        rl.draw_rectangle(0, 0, sw, sh, rl.fade(rl.BLACK, 0.7))

        title = "PAUSED"
        title_size = max(28, int(sw * 0.07))
        tw = rl.measure_text(title, title_size)
        rl.draw_text(title, (sw - tw) // 2, int(sh * 0.08), title_size, rl.WHITE)

        for i, option in enumerate(self.pause_options):
            rect = self._pause_option_rect(i)
            hovered = rl.check_collision_point_rec(rl.get_mouse_position(), rect)
            selected = i == self.pause_selection
            color = rl.SKYBLUE if selected else (rl.DARKBLUE if hovered else rl.DARKGRAY)
            rl.draw_rectangle_rec(rect, color)
            rl.draw_rectangle_lines_ex(rect, 1, rl.WHITE)

            label = option
            label_size = int(rect.height * 0.5)
            lw = rl.measure_text(label, label_size)
            rl.draw_text(
                label,
                int(rect.x + (rect.width - lw) // 2),
                int(rect.y + (rect.height - label_size) // 2),
                label_size,
                rl.WHITE,
            )

        hint = "ESC: resume"
        hint_size = max(12, int(sw * 0.025))
        hw = rl.measure_text(hint, hint_size)
        rl.draw_text(hint, (sw - hw) // 2, sh - int(sh * 0.1), hint_size, rl.GRAY)

    def _save_progress(self, next_scene):
        config = {}
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)

        if next_scene:
            config["current_scene"] = next_scene

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

    def _complete(self):
        next_name = self._level.get("next_scene", "")
        self._save_progress(next_name)
        self.done = True

        if next_name:
            from core.scenes.storyMode import StoryModeScene

            self.next_scene = StoryModeScene()
        else:
            from core.scenes.menu import MenuScene

            self.next_scene = MenuScene()

    def is_done(self):
        return self.done

    def cleanup(self):
        if self.music:
            rl.stop_music_stream(self.music)
            rl.unload_music_stream(self.music)
