import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
LEVEL_DIR = os.path.join(ASSETS_DIR, "chapter", "level")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "core", "config", "config.json")
