import json
import os
import glob

from scenes.chapter.first.tutorial.tutorial import TutorialScene

CONFIG_PATH = os.path.join("core", "config", "config.json")
LEVEL_DIR = os.path.join("assets", "chapter", "level")

TYPE_TO_CLASS = {
    "tutorial": TutorialScene,
}


def _build_scene_map():
    scene_map = {}
    for path in glob.glob(os.path.join(LEVEL_DIR, "*.json")):
        with open(path, "r") as f:
            level = json.load(f)
        key = (str(level.get("chapter", 1)), level.get("name", ""))
        scene_cls = TYPE_TO_CLASS.get(level.get("type", ""))
        if key[1] and scene_cls:
            scene_map[key] = (scene_cls, level)
    return scene_map


class StoryModeScene:
    def __init__(self):
        self.done = True
        self.next_scene = None

        config = self._load_config()
        chapter = str(config.get("chapter", 1))
        current = config.get("current_scene", "")

        scene_map = _build_scene_map()
        entry = scene_map.get((chapter, current))
        if entry:
            scene_cls, level_data = entry
            self.next_scene = scene_cls(level_data)

    def _load_config(self):
        if not os.path.isfile(CONFIG_PATH):
            return {}
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def update(self):
        pass

    def draw(self):
        pass

    def is_done(self):
        return self.done
