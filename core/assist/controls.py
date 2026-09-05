import json
import os

import pyray as rl

from core.assist.paths import PROJECT_ROOT

CONTROLS_PATH = os.path.join(PROJECT_ROOT, "core", "config", "controls.json")

ACTION_LABELS = {
    "move_left": "Move Left",
    "move_right": "Move Right",
    "soft_drop": "Soft Drop",
    "hard_drop": "Hard Drop",
    "rotate_cw": "Rotate Clockwise",
    "rotate_ccw": "Rotate Counter-Clockwise",
    "hold": "Hold Piece",
}

DEFAULT_CONTROLS = {
    "move_left": rl.KEY_J,
    "move_right": rl.KEY_L,
    "soft_drop": rl.KEY_K,
    "hard_drop": rl.KEY_SPACE,
    "rotate_cw": rl.KEY_W,
    "rotate_ccw": rl.KEY_Q,
    "hold": rl.KEY_C,
}

DEFAULT_DAS = {
    "das_delay": 0.17,
    "das_teleport": True,
}

KEY_NAMES = {
    rl.KEY_SPACE: "Space",
    rl.KEY_ENTER: "Enter",
    rl.KEY_ESCAPE: "Esc",
    rl.KEY_LEFT: "Left",
    rl.KEY_RIGHT: "Right",
    rl.KEY_UP: "Up",
    rl.KEY_DOWN: "Down",
    rl.KEY_BACKSPACE: "Backspace",
    rl.KEY_TAB: "Tab",
    rl.KEY_DELETE: "Delete",
    rl.KEY_LEFT_SHIFT: "LShift",
    rl.KEY_RIGHT_SHIFT: "RShift",
    rl.KEY_LEFT_CONTROL: "LCtrl",
    rl.KEY_RIGHT_CONTROL: "RCtrl",
    rl.KEY_LEFT_ALT: "LAlt",
    rl.KEY_RIGHT_ALT: "RAlt",
}


def key_name(keycode):
    name = KEY_NAMES.get(keycode)
    if name:
        return name
    if 32 <= keycode <= 126:
        return chr(keycode)
    return f"Key{keycode}"


def default_controls():
    return dict(DEFAULT_CONTROLS)


def default_das():
    return dict(DEFAULT_DAS)


def load_controls():
    if not os.path.isfile(CONTROLS_PATH):
        return default_controls(), default_das()
    try:
        with open(CONTROLS_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return default_controls(), default_das()
    merged = default_controls()
    for action in merged:
        if action in data and isinstance(data[action], int):
            merged[action] = data[action]
    das = default_das()
    if isinstance(data.get("das_delay"), (int, float)):
        das["das_delay"] = float(data["das_delay"])
    if isinstance(data.get("das_teleport"), bool):
        das["das_teleport"] = data["das_teleport"]
    return merged, das


def save_controls(controls, das=None):
    data = dict(controls)
    if das:
        data["das_delay"] = das["das_delay"]
        data["das_teleport"] = das["das_teleport"]
    with open(CONTROLS_PATH, "w") as f:
        json.dump(data, f, indent=2)
