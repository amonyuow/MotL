"""Title screen with Play, Mute, and volume sliders for title/boss themes. JS&B style."""

import pygame
from config import (
    SCREEN_W, SCREEN_H, ACCENT_WHITE, BOSS_IMAGE_PATH,
    TITLE_BUTTON_COLOR, TITLE_BUTTON_HOVER, TITLE_BUTTON_BORDER,
    DEFAULT_TITLE_VOLUME, DEFAULT_BOSS_VOLUME, DEFAULT_HIT_VOLUME,
    VOLUME_SLIDER_MAX,
    SLIDER_TRACK_IMAGE_PATH, SLIDER_THUMB_IMAGE_PATH,
    SETTINGS_GEAR_IMAGE_PATH,
)

# Button layout
PLAY_BUTTON_RECT = pygame.Rect(SCREEN_W // 2 - 100, 340, 200, 56)
SETTINGS_BUTTON_RECT = pygame.Rect(SCREEN_W - 60, 408, 44, 44)  # gear icon, toggles settings panel
# Settings panel: centered on screen, with consistent spacing between label and slider rows
TITLE_SETTINGS_PANEL_H = 206
TITLE_SETTINGS_PANEL_RECT = pygame.Rect(
    SCREEN_W // 2 - 160,
    SCREEN_H // 2 - TITLE_SETTINGS_PANEL_H // 2,
    320, TITLE_SETTINGS_PANEL_H
)

# Slider layout (track rects: x, y, width, height) — inside settings panel
SLIDER_W = 280
SLIDER_H = 22
LABEL_ABOVE_SLIDER = 18   # gap between label and its slider bar
ROW_GAP = 28              # gap between one slider bar and the next label
# Y positions (centered panel: top = SCREEN_H//2 - 103 = 197)
_settings_panel_top = SCREEN_H // 2 - TITLE_SETTINGS_PANEL_H // 2
SLIDER_Y_TITLE = _settings_panel_top + 36   # 197+36=233
SLIDER_Y_BOSS = SLIDER_Y_TITLE + SLIDER_H + ROW_GAP + LABEL_ABOVE_SLIDER   # 233+22+28+18=301
SLIDER_Y_HIT = SLIDER_Y_BOSS + SLIDER_H + ROW_GAP + LABEL_ABOVE_SLIDER    # 301+22+28+18=369
SLIDER_X = SCREEN_W // 2 - SLIDER_W // 2

TITLE_SLIDER_RECT = pygame.Rect(SLIDER_X, SLIDER_Y_TITLE, SLIDER_W, SLIDER_H)
BOSS_SLIDER_RECT = pygame.Rect(SLIDER_X, SLIDER_Y_BOSS, SLIDER_W, SLIDER_H)
HIT_SLIDER_RECT = pygame.Rect(SLIDER_X, SLIDER_Y_HIT, SLIDER_W, SLIDER_H)
# Mute button to the right of the settings panel (only visible when settings open)
TITLE_SETTINGS_MUTE_GAP = 12
TITLE_SETTINGS_MUTE_W = 100
TITLE_SETTINGS_MUTE_H = 44
TITLE_SETTINGS_MUTE_RECT = pygame.Rect(
    TITLE_SETTINGS_PANEL_RECT.right + TITLE_SETTINGS_MUTE_GAP,
    TITLE_SETTINGS_PANEL_RECT.centery - TITLE_SETTINGS_MUTE_H // 2,
    TITLE_SETTINGS_MUTE_W, TITLE_SETTINGS_MUTE_H,
)

# Pause menu (centered) + optional settings tab on the side. Heights snug to content.
PAUSE_PANEL_W = 280
PAUSE_PANEL_H = 248   # title + 3 buttons + padding (no excess)
PAUSE_SETTINGS_PANEL_GAP = 12
PAUSE_SETTINGS_PANEL_W = 248
PAUSE_SETTINGS_PANEL_H = 248   # same as pause panel for unified look
PAUSE_SLIDER_W = 220
PAUSE_SLIDER_H = 22
PAUSE_LABEL_ABOVE = 16
PAUSE_ROW_GAP = 22
# Rects depend on settings_open and are centered; use get_pause_menu_rects(settings_open).
# Default/legacy rects for handle_click when called without settings_open (main passes it).
PAUSE_PANEL_RECT = pygame.Rect(SCREEN_W // 2 - PAUSE_PANEL_W // 2, SCREEN_H // 2 - PAUSE_PANEL_H // 2, PAUSE_PANEL_W, PAUSE_PANEL_H)
PAUSE_RESUME_RECT = pygame.Rect(PAUSE_PANEL_RECT.centerx - 90, PAUSE_PANEL_RECT.top + 50, 180, 44)
PAUSE_TITLE_RECT  = pygame.Rect(PAUSE_PANEL_RECT.centerx - 90, PAUSE_PANEL_RECT.top + 105, 180, 44)
PAUSE_RESTART_RECT = pygame.Rect(PAUSE_PANEL_RECT.centerx - 90, PAUSE_PANEL_RECT.top + 160, 180, 44)
PAUSE_SETTINGS_BUTTON_RECT = pygame.Rect(PAUSE_PANEL_RECT.right - 50, PAUSE_PANEL_RECT.top + 12, 36, 36)
PAUSE_SETTINGS_PANEL_RECT = pygame.Rect(PAUSE_PANEL_RECT.right + PAUSE_SETTINGS_PANEL_GAP, PAUSE_PANEL_RECT.top, PAUSE_SETTINGS_PANEL_W, PAUSE_SETTINGS_PANEL_H)
PAUSE_TITLE_SLIDER_RECT = pygame.Rect(0, 0, PAUSE_SLIDER_W, PAUSE_SLIDER_H)  # filled by get_pause_menu_rects
PAUSE_BOSS_SLIDER_RECT = pygame.Rect(0, 0, PAUSE_SLIDER_W, PAUSE_SLIDER_H)
PAUSE_HIT_SLIDER_RECT = pygame.Rect(0, 0, PAUSE_SLIDER_W, PAUSE_SLIDER_H)

# Pause button (top-left, during game only)
PAUSE_BUTTON_RECT = pygame.Rect(12, 12, 44, 44)


PAUSE_MUTE_BTN_W, PAUSE_MUTE_BTN_H = 100, 44


def get_pause_menu_rects(settings_open):
    """Return (pause_rect, resume_rect, title_rect, restart_rect, settings_btn_rect,
    settings_panel_rect_or_None, title_slider_rect_or_None, boss_slider_rect_or_None, hit_slider_rect_or_None, pause_mute_rect_or_None).
    Combined block is centered; when settings_open, panels + mute button are centered together."""
    block_w = PAUSE_PANEL_W
    if settings_open:
        block_w += PAUSE_SETTINGS_PANEL_GAP + PAUSE_SETTINGS_PANEL_W + PAUSE_SETTINGS_PANEL_GAP + PAUSE_MUTE_BTN_W
    block_left = SCREEN_W // 2 - block_w // 2
    center_y = SCREEN_H // 2
    pause_rect = pygame.Rect(block_left, center_y - PAUSE_PANEL_H // 2, PAUSE_PANEL_W, PAUSE_PANEL_H)
    resume_rect = pygame.Rect(pause_rect.centerx - 90, pause_rect.top + 50, 180, 44)
    title_rect = pygame.Rect(pause_rect.centerx - 90, pause_rect.top + 105, 180, 44)
    restart_rect = pygame.Rect(pause_rect.centerx - 90, pause_rect.top + 160, 180, 44)
    settings_btn_rect = pygame.Rect(pause_rect.right - 50, pause_rect.top + 12, 36, 36)
    if not settings_open:
        return pause_rect, resume_rect, title_rect, restart_rect, settings_btn_rect, None, None, None, None, None
    settings_panel_rect = pygame.Rect(
        pause_rect.right + PAUSE_SETTINGS_PANEL_GAP,
        center_y - PAUSE_SETTINGS_PANEL_H // 2,
        PAUSE_SETTINGS_PANEL_W, PAUSE_SETTINGS_PANEL_H,
    )
    row_h = PAUSE_SLIDER_H + PAUSE_LABEL_ABOVE + PAUSE_ROW_GAP
    slider_x = settings_panel_rect.left + (PAUSE_SETTINGS_PANEL_W - PAUSE_SLIDER_W) // 2
    title_slider = pygame.Rect(slider_x, settings_panel_rect.top + 44, PAUSE_SLIDER_W, PAUSE_SLIDER_H)
    boss_slider = pygame.Rect(slider_x, settings_panel_rect.top + 44 + row_h, PAUSE_SLIDER_W, PAUSE_SLIDER_H)
    hit_slider = pygame.Rect(slider_x, settings_panel_rect.top + 44 + 2 * row_h, PAUSE_SLIDER_W, PAUSE_SLIDER_H)
    pause_mute_rect = pygame.Rect(
        settings_panel_rect.right + PAUSE_SETTINGS_PANEL_GAP,
        settings_panel_rect.centery - PAUSE_MUTE_BTN_H // 2,
        PAUSE_MUTE_BTN_W, PAUSE_MUTE_BTN_H,
    )
    return pause_rect, resume_rect, title_rect, restart_rect, settings_btn_rect, settings_panel_rect, title_slider, boss_slider, hit_slider, pause_mute_rect


def load_title_boss_image():
    """Load boss image for title screen (larger)."""
    if not BOSS_IMAGE_PATH:
        return None
    try:
        img = pygame.image.load(BOSS_IMAGE_PATH)
        img.set_colorkey((0, 0, 0))
        return pygame.transform.smoothscale(img, (220, 220))
    except (pygame.error, FileNotFoundError):
        return None


_settings_gear_img = None


def load_settings_gear_image():
    """Load settings gear icon for the settings button. Returns surface or None."""
    global _settings_gear_img
    if _settings_gear_img is not None:
        return _settings_gear_img
    if not SETTINGS_GEAR_IMAGE_PATH:
        return None
    try:
        img = pygame.image.load(SETTINGS_GEAR_IMAGE_PATH).convert_alpha()
        _settings_gear_img = pygame.transform.smoothscale(img, (44, 44))
        return _settings_gear_img
    except (pygame.error, FileNotFoundError):
        return None


# Slider track/thumb images (striped bar + face handle). Cached after first load.
_slider_track_img = None
_slider_thumb_img = None


def _load_slider_assets():
    """Load slider track and thumb from separate image files; return (track_surf, thumb_surf) or (None, None)."""
    global _slider_track_img, _slider_thumb_img
    if _slider_track_img is not None:
        return _slider_track_img, _slider_thumb_img
    if not SLIDER_TRACK_IMAGE_PATH or not SLIDER_THUMB_IMAGE_PATH:
        return None, None
    try:
        _slider_track_img = pygame.image.load(SLIDER_TRACK_IMAGE_PATH).convert_alpha()
        _slider_thumb_img = pygame.image.load(SLIDER_THUMB_IMAGE_PATH).convert_alpha()
        return _slider_track_img, _slider_thumb_img
    except (pygame.error, FileNotFoundError):
        return None, None


def _draw_slider(surface, rect, volume, thumb_height=42):
    """Draw one slider. volume is 0.0–VOLUME_SLIDER_MAX; thumb position = volume/MAX along track."""
    norm = max(0.0, min(VOLUME_SLIDER_MAX, volume)) / VOLUME_SLIDER_MAX  # 0–1 for position
    track_img, thumb_img = _load_slider_assets()
    if track_img is None or thumb_img is None:
        pygame.draw.rect(surface, TITLE_BUTTON_COLOR, rect)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, rect, 1)
        tw = 18
        th = min(thumb_height, rect.height + 5)
        tx = rect.left + int(norm * rect.width) - tw // 2
        tx = max(rect.left, min(rect.right - tw, tx))
        pygame.draw.rect(surface, ACCENT_WHITE, (tx, rect.centery - th // 2, tw, th))
        return
    scaled_track = pygame.transform.smoothscale(track_img, (rect.width, rect.height))
    surface.blit(scaled_track, rect)
    th = rect.height + 30
    thumb_h = max(1, thumb_img.get_height())
    tw = int(thumb_img.get_width() * th / thumb_h)
    scaled_thumb = pygame.transform.smoothscale(thumb_img, (tw, th))
    tx = rect.left + int(norm * rect.width) - tw // 2
    tx = max(rect.left, min(rect.right - tw, tx))
    surface.blit(scaled_thumb, (tx, rect.centery - th // 2))


def _slider_value_from_pos(rect, pos):
    """Return 0.0–VOLUME_SLIDER_MAX from mouse x within slider track."""
    if not rect.collidepoint(pos):
        return None
    x = max(rect.left, min(rect.right, pos[0]))
    norm = (x - rect.left) / max(1, rect.width)
    return max(0.0, min(VOLUME_SLIDER_MAX, norm * VOLUME_SLIDER_MAX))


def update_volumes(mouse_pos, mouse_pressed, title_volume, boss_volume, hit_volume):
    """
    If mouse is down and over a slider, return updated (title_volume, boss_volume, hit_volume).
    Otherwise return unchanged.
    """
    if not mouse_pressed:
        return title_volume, boss_volume, hit_volume
    v_title = _slider_value_from_pos(TITLE_SLIDER_RECT, mouse_pos)
    if v_title is not None:
        return v_title, boss_volume, hit_volume
    v_boss = _slider_value_from_pos(BOSS_SLIDER_RECT, mouse_pos)
    if v_boss is not None:
        return title_volume, v_boss, hit_volume
    v_hit = _slider_value_from_pos(HIT_SLIDER_RECT, mouse_pos)
    if v_hit is not None:
        return title_volume, boss_volume, v_hit
    return title_volume, boss_volume, hit_volume


def update_pause_volumes(mouse_pos, mouse_pressed, title_volume, boss_volume, hit_volume, settings_open):
    """Same as update_volumes but for pause menu slider rects (only active when settings tab is open)."""
    if not mouse_pressed or not settings_open:
        return title_volume, boss_volume, hit_volume
    _, _, _, _, _, _, title_slider, boss_slider, hit_slider, _ = get_pause_menu_rects(True)
    if title_slider is None:
        return title_volume, boss_volume, hit_volume
    v = _slider_value_from_pos(title_slider, mouse_pos)
    if v is not None:
        return v, boss_volume, hit_volume
    v = _slider_value_from_pos(boss_slider, mouse_pos)
    if v is not None:
        return title_volume, v, hit_volume
    v = _slider_value_from_pos(hit_slider, mouse_pos)
    if v is not None:
        return title_volume, boss_volume, v
    return title_volume, boss_volume, hit_volume


def draw_pause_menu(surface, mouse_pos, title_volume, boss_volume, hit_volume, settings_open=False, muted=False):
    """Draw pause overlay: panel with Resume, Return to title, Restart, settings gear; (when open) settings tab on the side + Mute. Centered."""
    font = pygame.font.Font(None, 28)
    font_btn = pygame.font.Font(None, 36)
    (pause_rect, resume_rect, title_rect, restart_rect, settings_btn_rect,
     settings_panel_rect, title_slider, boss_slider, hit_slider, pause_mute_rect) = get_pause_menu_rects(settings_open)
    # Dim overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    # Pause panel
    pygame.draw.rect(surface, TITLE_BUTTON_COLOR, pause_rect)
    pygame.draw.rect(surface, TITLE_BUTTON_BORDER, pause_rect, 3)
    title = font_btn.render("PAUSED", True, ACCENT_WHITE)
    surface.blit(title, title.get_rect(center=(pause_rect.centerx, pause_rect.top + 24)))
    for rect, label in [
        (resume_rect, "Resume"),
        (title_rect, "Return to title"),
        (restart_rect, "Restart"),
    ]:
        hover = rect.collidepoint(mouse_pos)
        color = TITLE_BUTTON_HOVER if hover else TITLE_BUTTON_COLOR
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, rect, 2)
        text = font.render(label, True, ACCENT_WHITE)
        surface.blit(text, text.get_rect(center=rect.center))
    # Settings (gear) button
    gear_img = load_settings_gear_image()
    settings_hover = settings_btn_rect.collidepoint(mouse_pos)
    if gear_img is not None:
        g = pygame.transform.smoothscale(gear_img, (36, 36))
        color = TITLE_BUTTON_HOVER if settings_hover else TITLE_BUTTON_COLOR
        pygame.draw.rect(surface, color, settings_btn_rect)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, settings_btn_rect, 2)
        surface.blit(g, settings_btn_rect)
    else:
        pygame.draw.rect(surface, TITLE_BUTTON_HOVER if settings_hover else TITLE_BUTTON_COLOR, settings_btn_rect)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, settings_btn_rect, 2)
        gear_text = font.render("⚙", True, ACCENT_WHITE)
        surface.blit(gear_text, gear_text.get_rect(center=settings_btn_rect.center))
    # Settings tab panel on the side when open
    if settings_open and settings_panel_rect is not None and title_slider is not None:
        pygame.draw.rect(surface, TITLE_BUTTON_COLOR, settings_panel_rect)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, settings_panel_rect, 3)
        settings_title = font_btn.render("Settings", True, ACCENT_WHITE)
        surface.blit(settings_title, settings_title.get_rect(center=(settings_panel_rect.centerx, settings_panel_rect.top + 22)))
        surface.blit(font.render("Title theme:", True, ACCENT_WHITE), (title_slider.left, title_slider.top - PAUSE_LABEL_ABOVE))
        _draw_slider(surface, title_slider, title_volume, thumb_height=28)
        surface.blit(font.render("Boss theme:", True, ACCENT_WHITE), (boss_slider.left, boss_slider.top - PAUSE_LABEL_ABOVE))
        _draw_slider(surface, boss_slider, boss_volume, thumb_height=24)
        surface.blit(font.render("Hit effect:", True, ACCENT_WHITE), (hit_slider.left, hit_slider.top - PAUSE_LABEL_ABOVE))
        _draw_slider(surface, hit_slider, hit_volume, thumb_height=24)
        # Mute button to the right of the settings panel
        if pause_mute_rect is not None:
            mute_hover = pause_mute_rect.collidepoint(mouse_pos)
            color_mute = TITLE_BUTTON_HOVER if mute_hover else TITLE_BUTTON_COLOR
            pygame.draw.rect(surface, color_mute, pause_mute_rect)
            pygame.draw.rect(surface, TITLE_BUTTON_BORDER, pause_mute_rect, 2)
            mute_label = "UNMUTE" if muted else "MUTE"
            mute_text = font.render(mute_label, True, ACCENT_WHITE)
            surface.blit(mute_text, mute_text.get_rect(center=pause_mute_rect.center))


def handle_pause_click(pos, settings_open=False):
    """Return 'resume', 'title', 'restart', 'settings', 'mute', or None. Use same settings_open as current state so rects match."""
    _, resume_rect, title_rect, restart_rect, settings_btn_rect, _, _, _, _, pause_mute_rect = get_pause_menu_rects(settings_open)
    if resume_rect.collidepoint(pos):
        return "resume"
    if title_rect.collidepoint(pos):
        return "title"
    if restart_rect.collidepoint(pos):
        return "restart"
    if settings_btn_rect.collidepoint(pos):
        return "settings"
    if settings_open and pause_mute_rect is not None and pause_mute_rect.collidepoint(pos):
        return "mute"
    return None


def draw(surface, mouse_pos, muted, title_volume, boss_volume, hit_volume, settings_open=False, highest_score=0, last_score=0):
    """Draw title screen. Use handle_click() for button actions. Background must be drawn by caller.
    When settings_open is True, the settings panel with audio sliders is visible.
    highest_score and last_score are shown below the Play button."""
    # Title text
    font_large = pygame.font.Font(None, 64)
    title = font_large.render("MotI", True, ACCENT_WHITE)
    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 50))
    font_sub = pygame.font.Font(None, 28)
    sub = font_sub.render("Red Soul Boss Fight", True, (160, 140, 200))
    surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 115))

    # Boss character
    img = load_title_boss_image()
    if img:
        r = img.get_rect(center=(SCREEN_W // 2, 240))
        surface.blit(img, r)
    else:
        pygame.draw.rect(surface, (180, 60, 80), (SCREEN_W // 2 - 60, 130, 120, 120), 3)

    # Play button
    play_hover = PLAY_BUTTON_RECT.collidepoint(mouse_pos)
    color_play = TITLE_BUTTON_HOVER if play_hover else TITLE_BUTTON_COLOR
    pygame.draw.rect(surface, color_play, PLAY_BUTTON_RECT)
    pygame.draw.rect(surface, TITLE_BUTTON_BORDER, PLAY_BUTTON_RECT, 3)
    font_btn = pygame.font.Font(None, 42)
    play_text = font_btn.render("PLAY", True, ACCENT_WHITE)
    surface.blit(play_text, play_text.get_rect(center=PLAY_BUTTON_RECT.center))

    # High score and last score below Play button
    below_play_y = PLAY_BUTTON_RECT.bottom + 14
    high_text = font_sub.render(f"Highest: {highest_score}", True, (200, 200, 220))
    surface.blit(high_text, (SCREEN_W // 2 - high_text.get_width() // 2, below_play_y))
    last_text = font_sub.render(f"Most recent: {last_score}", True, (200, 200, 220))
    surface.blit(last_text, (SCREEN_W // 2 - last_text.get_width() // 2, below_play_y + 24))

    # Settings (gear) button — toggles settings panel
    gear_img = load_settings_gear_image()
    settings_hover = SETTINGS_BUTTON_RECT.collidepoint(mouse_pos)
    if gear_img is not None:
        color = TITLE_BUTTON_HOVER if settings_hover else TITLE_BUTTON_COLOR
        pygame.draw.rect(surface, color, SETTINGS_BUTTON_RECT)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, SETTINGS_BUTTON_RECT, 2)
        surface.blit(gear_img, SETTINGS_BUTTON_RECT)
    else:
        pygame.draw.rect(surface, TITLE_BUTTON_HOVER if settings_hover else TITLE_BUTTON_COLOR, SETTINGS_BUTTON_RECT)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, SETTINGS_BUTTON_RECT, 2)
        gear_text = font_sub.render("⚙", True, ACCENT_WHITE)
        surface.blit(gear_text, gear_text.get_rect(center=SETTINGS_BUTTON_RECT.center))

    # Settings panel (audio sliders + Mute) — only when open
    if settings_open:
        pygame.draw.rect(surface, TITLE_BUTTON_COLOR, TITLE_SETTINGS_PANEL_RECT)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, TITLE_SETTINGS_PANEL_RECT, 3)
        label_title = font_sub.render("Title theme:", True, ACCENT_WHITE)
        surface.blit(label_title, (SLIDER_X, SLIDER_Y_TITLE - LABEL_ABOVE_SLIDER))
        _draw_slider(surface, TITLE_SLIDER_RECT, title_volume)
        label_boss = font_sub.render("Boss theme:", True, ACCENT_WHITE)
        surface.blit(label_boss, (SLIDER_X, SLIDER_Y_BOSS - LABEL_ABOVE_SLIDER))
        _draw_slider(surface, BOSS_SLIDER_RECT, boss_volume)
        label_hit = font_sub.render("Hit effect:", True, ACCENT_WHITE)
        surface.blit(label_hit, (SLIDER_X, SLIDER_Y_HIT - LABEL_ABOVE_SLIDER))
        _draw_slider(surface, HIT_SLIDER_RECT, hit_volume)
        # Mute button (to the right of the settings panel)
        mute_hover = TITLE_SETTINGS_MUTE_RECT.collidepoint(mouse_pos)
        color_mute = TITLE_BUTTON_HOVER if mute_hover else TITLE_BUTTON_COLOR
        pygame.draw.rect(surface, color_mute, TITLE_SETTINGS_MUTE_RECT)
        pygame.draw.rect(surface, TITLE_BUTTON_BORDER, TITLE_SETTINGS_MUTE_RECT, 2)
        mute_label = "UNMUTE" if muted else "MUTE"
        mute_text = font_sub.render(mute_label, True, ACCENT_WHITE)
        surface.blit(mute_text, mute_text.get_rect(center=TITLE_SETTINGS_MUTE_RECT.center))


def handle_click(pos, settings_open=False):
    """Return 'play', 'mute', 'settings', or None. Mute is only clickable when settings panel is open."""
    if PLAY_BUTTON_RECT.collidepoint(pos):
        return "play"
    if SETTINGS_BUTTON_RECT.collidepoint(pos):
        return "settings"
    if settings_open and TITLE_SETTINGS_MUTE_RECT.collidepoint(pos):
        return "mute"
    return None
