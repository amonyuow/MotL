"""Game configuration - colors, dimensions, tuning."""

import os

# Display
SCREEN_W = 800
SCREEN_H = 600
FPS = 60

# -----------------------------------------------------------------------------
# MUSIC — Insert your MP3 file paths here
# -----------------------------------------------------------------------------
# Folder containing this project (so paths work from any working directory).
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Title screen music (plays on menu). Use None for no title music.
TITLE_MUSIC_PATH = os.path.join(_PROJECT_DIR, "Studlands OST - Max's Inn.mp3")

# Boss fight music (plays during the fight).
BOSS_FIGHT_MUSIC_PATH = r"c:\Users\maxim\Downloads\audiomass-output.mp3"

# Default volume for each track. Sliders range 0%–200% (0.0–2.0); 100% = 1.0.
DEFAULT_TITLE_VOLUME = 1.0
DEFAULT_BOSS_VOLUME = 1.0
DEFAULT_HIT_VOLUME = 1.0
VOLUME_SLIDER_MAX = 2.0   # 200% max; mixer is capped at 1.0 when applying

# Music crossfade duration (ms) when switching between title and boss theme.
MUSIC_FADE_OUT_MS = 400
MUSIC_FADE_IN_MS = 500
# Sound effect when the player loses a heart (hit by bullet/hazard). None = no sound.
HIT_SOUND_PATH = os.path.join(_PROJECT_DIR, "assets", "hitHurt.wav")
# -----------------------------------------------------------------------------

# Just Shapes and Beats style palette
BG_COLOR = (148, 0, 0)
SOUL_BOX_COLOR = ((66, 2, 0))
SOUL_BOX_BORDER = (120, 80, 180)
PLAYER_COLOR = (255, 60, 80)      # Red soul
PLAYER_SAFE_COLOR = (255, 100, 120)
DANGER_COLOR = (255, 80, 120)     # Bullets / hazards
ACCENT_CYAN = (0, 255, 255)
ACCENT_MAGENTA = (87, 0, 4)
ACCENT_WHITE = (240, 248, 255)
BOSS_COLOR = (180, 100, 255)

# Soul box (Undertale red soul arena)
SOUL_BOX_X = 80
SOUL_BOX_Y = 120
SOUL_BOX_W = 320
SOUL_BOX_H = 280
SOUL_BOX_BORDER_THICKNESS = 4

# Player (soul)
PLAYER_RADIUS = 8
PLAYER_SPEED = 5

# Healing pickups (spawn when HP < 3, every 30 seconds, max 3 at a time, +1 HP each)
HEAL_SPAWN_INTERVAL_SEC = 30
HEAL_MAX_PICKUPS = 3
HEAL_PICKUP_RADIUS = 10
HEAL_PICKUP_MARGIN = 24   # min distance from soul box edge when spawning
HEAL_PICKUP_COLOR = (80, 255, 120)   # green

# Boss
BOSS_X = 520
BOSS_Y = 200
BOSS_SIZE = 80
# Path to boss image (JS&B style character). None = draw geometric fallback.
BOSS_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "boss.png")

# Background image (title + gameplay). None = use BG_COLOR only.
BACKGROUND_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "background.png")

# Bullets
BULLET_RADIUS = 6
BULLET_HITBOX_RADIUS = 5   # small hitbox at bullet center, along flight path
BULLET_SPEED = 6.5   # faster flight
BULLET_COLOR = (255, 80, 120)
BULLET_ROTATION_OFFSET = 8  # degrees to subtract to align tip with direction (0=no correction)

# Screen shake
SHAKE_AMOUNT = 8
SHAKE_DECAY = 0.9

# Slider assets: track (striped bar) and thumb (audio handle). None = use drawn rects.
SLIDER_TRACK_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "slider_track.png")
SLIDER_THUMB_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "slider_thumb.png")

# Title screen
TITLE_BUTTON_COLOR = (80, 40, 120)
TITLE_BUTTON_HOVER = (140, 80, 200)
TITLE_BUTTON_BORDER = (180, 120, 255)
# Settings (gear) button. None = draw a simple gear shape.
SETTINGS_GEAR_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "settings_gear.png")

# Click-circles minigame: 50% chance every 30 seconds; click 3–10 circles in time or lose 1 life.
MINIGAME_INTERVAL_SEC = 30
MINIGAME_CHANCE = 0.5
MINIGAME_CIRCLE_RADIUS = 22
MINIGAME_CIRCLE_MARGIN = 28   # min distance from soul box edge
# Time limit (seconds) by number of circles: 3→1, 4→1, 5→1.5, 6→2, 7→2, 8→2.5, 9→3, 10→3
MINIGAME_TIME_BY_COUNT = {3: 1.5, 4: 1.5, 5: 2.25, 6: 3.0, 7: 3.0, 8: 3.75, 9: 4.5, 10: 4.5}
MINIGAME_TIMER_ALPHA = 55   # heavily translucent text (0–255)
MINIGAME_CIRCLE_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "minigame_circle.png")  # red circle sprite; None = draw with pygame
