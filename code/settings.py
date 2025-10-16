# settings.py
# All relative paths in code/ expect assets folder at ../assets

from kivy.core.window import Window

# Default testing window size (mobile device will use native screen)
Window.size = Window.size or (1280, 720)

SCREEN_W, SCREEN_H = Window.size
MAP_W, MAP_H = 1920, 1080

ASSET_DIR = "../assets"   # keep assets at project root next to `code/`

# Speeds (pixels per second for Kivy movement style)
PLAYER_SPEED = 220.0
NPC_SPEED = 110.0
HUNTER_SPEED = 160.0

# Generator config
NUM_GENERATORS = 7
GEN_W, GEN_H = 64, 64
# Base repair seconds depending on alive players:
# We'll compute based on alive players: 1=>30, 2=>25, 3=>20, 4=>15, 5+=>10
REPAIR_TIMES = {1:30.0, 2:25.0, 3:20.0, 4:15.0, 5:10.0}

FPS = 60.0
