"""
Just Shapes and Beats style boss fight with Undertale red-soul mode.
Run this file to play. Customize attacks in attacks.py and ATTACK_CLASSES in boss.py.
Set BOSS_FIGHT_MUSIC_PATH and TITLE_MUSIC_PATH in config.py to use your MP3 files.
"""

import math
import random
import pygame
from config import (
    SCREEN_W, SCREEN_H, FPS, BG_COLOR,
    SOUL_BOX_X, SOUL_BOX_Y, SOUL_BOX_W, SOUL_BOX_H, PLAYER_RADIUS,
    SOUL_BOX_COLOR, SOUL_BOX_BORDER, SOUL_BOX_BORDER_THICKNESS,
    SHAKE_AMOUNT, SHAKE_DECAY, ACCENT_WHITE,
    TITLE_MUSIC_PATH, BOSS_FIGHT_MUSIC_PATH,
    DEFAULT_TITLE_VOLUME, DEFAULT_BOSS_VOLUME, DEFAULT_HIT_VOLUME,
    MUSIC_FADE_OUT_MS, MUSIC_FADE_IN_MS,
    TITLE_BUTTON_COLOR, TITLE_BUTTON_HOVER, TITLE_BUTTON_BORDER,
    BACKGROUND_IMAGE_PATH, HIT_SOUND_PATH,
    HEAL_SPAWN_INTERVAL_SEC, HEAL_MAX_PICKUPS, HEAL_PICKUP_RADIUS,
    HEAL_PICKUP_MARGIN, HEAL_PICKUP_COLOR,
    MINIGAME_INTERVAL_SEC, MINIGAME_CHANCE,     MINIGAME_CIRCLE_RADIUS,
    MINIGAME_CIRCLE_MARGIN, MINIGAME_TIME_BY_COUNT, MINIGAME_TIMER_ALPHA,
    MINIGAME_CIRCLE_IMAGE_PATH,
)
from player import Player
from boss import Boss
from title_screen import (
    draw as draw_title_screen,
    handle_click as handle_title_click,
    update_volumes as update_title_volumes,
    update_pause_volumes,
    draw_pause_menu,
    handle_pause_click,
    PAUSE_BUTTON_RECT,
)


def _minigame_generate_circles(count):
    """Return list of (x, y, radius) inside the soul box with margin. Radius = MINIGAME_CIRCLE_RADIUS."""
    r = MINIGAME_CIRCLE_RADIUS
    margin = MINIGAME_CIRCLE_MARGIN
    x_min = SOUL_BOX_X + margin + r
    x_max = SOUL_BOX_X + SOUL_BOX_W - margin - r
    y_min = SOUL_BOX_Y + margin + r
    y_max = SOUL_BOX_Y + SOUL_BOX_H - margin - r
    circles = []
    for _ in range(count):
        x = x_min + random.random() * (x_max - x_min)
        y = y_min + random.random() * (y_max - y_min)
        circles.append((x, y, r))
    return circles


def init_music(muted, title_volume):
    """Load and play title music at given volume (or 0 if muted)."""
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    vol = 0.0 if muted else min(1.0, title_volume)
    pygame.mixer.music.set_volume(vol)
    if TITLE_MUSIC_PATH and pygame.mixer.get_init():
        try:
            pygame.mixer.music.load(TITLE_MUSIC_PATH)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass


def start_fade_to_boss(muted, boss_volume):
    """Start fading out current track, then switch to boss theme and fade in."""
    if not pygame.mixer.get_init():
        return None
    pygame.mixer.music.fadeout(MUSIC_FADE_OUT_MS)
    return {
        "phase": "out",
        "start_ticks": pygame.time.get_ticks(),
        "target": "boss",
        "target_volume": 0.0 if muted else min(1.0, boss_volume),
    }


def start_fade_to_title(muted, title_volume):
    """Start fading out current track, then switch to title theme and fade in."""
    if not pygame.mixer.get_init():
        return None
    pygame.mixer.music.fadeout(MUSIC_FADE_OUT_MS)
    return {
        "phase": "out",
        "start_ticks": pygame.time.get_ticks(),
        "target": "title",
        "target_volume": 0.0 if muted else min(1.0, title_volume),
    }


def update_music_fade(music_fade, muted, title_volume, boss_volume):
    """
    Update fade state. Returns (new_fade_state, done).
    When done is True, fade is complete and caller should clear music_fade.
    """
    if music_fade is None:
        return None, True
    ticks = pygame.time.get_ticks()
    if music_fade["phase"] == "out":
        if ticks - music_fade["start_ticks"] >= MUSIC_FADE_OUT_MS:
            # Load and start new track at 0, then fade in
            try:
                if music_fade["target"] == "boss" and BOSS_FIGHT_MUSIC_PATH:
                    pygame.mixer.music.load(BOSS_FIGHT_MUSIC_PATH)
                elif music_fade["target"] == "title" and TITLE_MUSIC_PATH:
                    pygame.mixer.music.load(TITLE_MUSIC_PATH)
                else:
                    music_fade = None
                    return None, True
            except pygame.error:
                music_fade = None
                return None, True
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)
            music_fade["phase"] = "in"
            music_fade["start_ticks"] = ticks
        return music_fade, False
    else:
        # phase "in"
        elapsed = ticks - music_fade["start_ticks"]
        t = min(1.0, elapsed / MUSIC_FADE_IN_MS)
        vol = min(1.0, t * music_fade["target_volume"])
        pygame.mixer.music.set_volume(vol)
        if t >= 1.0:
            return None, True
        return music_fade, False


def apply_music_volume(muted, title_volume, boss_volume, state):
    """Set mixer volume from current mute and theme volumes (no fade). Capped at 1.0."""
    if not pygame.mixer.get_init():
        return
    raw = title_volume if state == "title" else boss_volume
    vol = 0.0 if muted else min(1.0, raw)
    pygame.mixer.music.set_volume(vol)


def load_background():
    """Load and scale background image to screen size. Returns None if missing/failed."""
    if not BACKGROUND_IMAGE_PATH:
        return None
    try:
        img = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
        return pygame.transform.smoothscale(img, (SCREEN_W, SCREEN_H))
    except (pygame.error, FileNotFoundError):
        return None


def draw_background(screen, background_surface):
    """Draw background: image if loaded, else solid BG_COLOR."""
    if background_surface is not None:
        screen.blit(background_surface, (0, 0))
    else:
        screen.fill(BG_COLOR)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    pygame.display.set_caption("MotI — Red Soul Boss Fight")
    clock = pygame.time.Clock()

    state = "title"
    muted = False
    title_volume = DEFAULT_TITLE_VOLUME
    boss_volume = DEFAULT_BOSS_VOLUME
    hit_volume = DEFAULT_HIT_VOLUME
    title_settings_open = False
    pause_settings_open = False
    music_fade = None
    init_music(muted, title_volume)

    player = Player()
    boss = Boss()
    shake = 0.0
    lives = 3
    game_timer = 0.0   # seconds alive this run; score = 1 point per second
    highest_score = 0
    last_score = 0
    minigame_state = None   # None or dict: circles, clicked, time_left, num_circles
    minigame_interval_timer = 0.0   # seconds until next 30s roll
    last_offset_x, last_offset_y = 0, 0   # for minigame click hit-test
    healing_pickups = []   # list of (x, y) in soul box
    heal_spawn_timer = 0.0  # seconds while lives < 3; spawn every HEAL_SPAWN_INTERVAL_SEC
    running = True
    soul_box_rect = pygame.Rect(SOUL_BOX_X, SOUL_BOX_Y, SOUL_BOX_W, SOUL_BOX_H)
    background_surface = load_background()
    hit_sound = None
    if HIT_SOUND_PATH and pygame.mixer.get_init():
        try:
            hit_sound = pygame.mixer.Sound(HIT_SOUND_PATH)
        except (pygame.error, FileNotFoundError):
            hit_sound = None

    minigame_circle_image = None
    if MINIGAME_CIRCLE_IMAGE_PATH:
        try:
            minigame_circle_image = pygame.image.load(MINIGAME_CIRCLE_IMAGE_PATH).convert_alpha()
        except (pygame.error, FileNotFoundError):
            minigame_circle_image = None

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Update music fade (runs in all states)
        if music_fade is not None:
            music_fade, fade_done = update_music_fade(music_fade, muted, title_volume, boss_volume)
            if fade_done and music_fade is None:
                pass  # fade finished

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "game":
                        state = "pause"
                    elif state == "pause":
                        state = "game"
                    elif state == "title":
                        running = False
                elif event.key == pygame.K_m:
                    # M = always go to title (from game or pause only; not on title)
                    if state == "game" or state == "pause":
                        state = "title"
                        music_fade = start_fade_to_title(muted, title_volume)
                        player = Player()
                        boss = Boss()
                        lives = 3
                        shake = 0.0
                        game_timer = 0.0
                        minigame_state = None
                        minigame_interval_timer = 0.0
                        healing_pickups = []
                        heal_spawn_timer = 0.0
                elif event.key == pygame.K_r:
                    if state == "pause":
                        state = "game"
                        lives = 3
                        player = Player()
                        boss = Boss()
                        shake = 0.0
                        game_timer = 0.0
                        minigame_state = None
                        minigame_interval_timer = 0.0
                        healing_pickups = []
                        heal_spawn_timer = 0.0
                    elif state == "game":
                        # Quick restart: R resets the boss fight (during play or on game over)
                        lives = 3
                        player = Player()
                        boss = Boss()
                        shake = 0.0
                        game_timer = 0.0
                        minigame_state = None
                        minigame_interval_timer = 0.0
                        healing_pickups = []
                        heal_spawn_timer = 0.0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "title":
                    result = handle_title_click(mouse_pos, title_settings_open)
                    if result == "settings":
                        title_settings_open = not title_settings_open
                    elif result == "mute":
                        muted = not muted
                        apply_music_volume(muted, title_volume, boss_volume, state)
                    elif not title_settings_open and result == "play":
                        state = "game"
                        music_fade = start_fade_to_boss(muted, boss_volume)
                        player = Player()
                        boss = Boss()
                        lives = 3
                        shake = 0.0
                        game_timer = 0.0
                        minigame_state = None
                        minigame_interval_timer = 0.0
                        healing_pickups = []
                        heal_spawn_timer = 0.0
                elif state == "game":
                    # Pause button (top-left)
                    if PAUSE_BUTTON_RECT.collidepoint(mouse_pos):
                        state = "pause"
                    elif minigame_state is not None:
                        # Click-circles minigame: hit-test circles (screen coords = world + last_offset)
                        for i, (cx, cy, cr) in enumerate(minigame_state["circles"]):
                            if i in minigame_state["clicked"]:
                                continue
                            sx, sy = cx + last_offset_x, cy + last_offset_y
                            if math.hypot(mouse_pos[0] - sx, mouse_pos[1] - sy) <= cr:
                                minigame_state["clicked"].add(i)
                                if len(minigame_state["clicked"]) == minigame_state["num_circles"]:
                                    minigame_state = None
                                    boss.reset_attacks_after_minigame()
                                    player.invuln_timer = 5 * FPS  # 5 s immunity after minigame
                                break
                elif state == "pause":
                    result = handle_pause_click(mouse_pos, pause_settings_open)
                    if result == "settings":
                        pause_settings_open = not pause_settings_open
                    elif result == "mute":
                        muted = not muted
                        apply_music_volume(muted, title_volume, boss_volume, "game")
                    elif not pause_settings_open:
                        # Only Resume/Title/Restart when settings tab is closed
                        if result == "resume":
                            state = "game"
                        elif result == "title":
                            state = "title"
                            music_fade = start_fade_to_title(muted, title_volume)
                            player = Player()
                            boss = Boss()
                            lives = 3
                            shake = 0.0
                            game_timer = 0.0
                            minigame_state = None
                            minigame_interval_timer = 0.0
                            healing_pickups = []
                            heal_spawn_timer = 0.0
                        elif result == "restart":
                            state = "game"
                            lives = 3
                            player = Player()
                            boss = Boss()
                            shake = 0.0
                            game_timer = 0.0
                            minigame_state = None
                            minigame_interval_timer = 0.0
                            healing_pickups = []
                            heal_spawn_timer = 0.0

        # ---------- Title screen ----------
        if state == "title":
            if title_settings_open and mouse_pressed:
                title_volume, boss_volume, hit_volume = update_title_volumes(
                    mouse_pos, mouse_pressed, title_volume, boss_volume, hit_volume
                )
            if music_fade is None:
                apply_music_volume(muted, title_volume, boss_volume, state)
            draw_background(screen, background_surface)
            draw_title_screen(screen, mouse_pos, muted, title_volume, boss_volume, hit_volume, title_settings_open, highest_score, last_score)
            pygame.display.flip()
            continue

        # ---------- Pause menu ----------
        if state == "pause":
            if pause_settings_open and mouse_pressed:
                title_volume, boss_volume, hit_volume = update_pause_volumes(
                    mouse_pos, mouse_pressed, title_volume, boss_volume, hit_volume, pause_settings_open
                )
            apply_music_volume(muted, title_volume, boss_volume, "game")
            # Draw game frame (frozen) then overlay
            offset_x = int((random.random() - 0.5) * shake) if shake else 0
            offset_y = int((random.random() - 0.5) * shake) if shake else 0
            draw_background(screen, background_surface)
            box_rect = soul_box_rect.move(offset_x, offset_y)
            pygame.draw.rect(screen, SOUL_BOX_COLOR, box_rect)
            for i in range(SOUL_BOX_BORDER_THICKNESS):
                pygame.draw.rect(screen, SOUL_BOX_BORDER, box_rect.inflate(i * 2, i * 2), 1)
            pygame.draw.rect(screen, ACCENT_WHITE, box_rect, 1)
            boss.draw_attacks(screen)
            for (hx, hy) in healing_pickups:
                pygame.draw.circle(screen, HEAL_PICKUP_COLOR, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS)
                pygame.draw.circle(screen, ACCENT_WHITE, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS, 1)
            player.draw(screen)
            boss.draw(screen)
            font = pygame.font.Font(None, 28)
            screen.blit(font.render(f"HP: {'♥' * lives}", True, (255, 80, 80)), (20 + offset_x, 20 + offset_y))
            score_text = font.render(f"Score: {int(game_timer)}", True, ACCENT_WHITE)
            score_x = SOUL_BOX_X + SOUL_BOX_W // 2 - score_text.get_width() // 2 + offset_x
            score_y = SOUL_BOX_Y - 28 + offset_y
            screen.blit(score_text, (score_x, score_y))
            draw_pause_menu(screen, mouse_pos, title_volume, boss_volume, hit_volume, pause_settings_open, muted)
            pygame.display.flip()
            continue

        # ---------- Game over ----------
        if lives <= 0:
            last_score = int(game_timer)
            highest_score = max(highest_score, last_score)
            draw_background(screen, background_surface)
            font = pygame.font.Font(None, 48)
            text = font.render("GAME OVER — Press R to restart", True, ACCENT_WHITE)
            screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, SCREEN_H // 2 - 24))
            score_text = font.render(f"Score: {int(game_timer)}", True, ACCENT_WHITE)
            screen.blit(score_text, (SCREEN_W // 2 - score_text.get_width() // 2, SCREEN_H // 2 + 20))
            pygame.display.flip()
            continue

        # ---------- Gameplay ----------
        if minigame_state is not None:
            # Click-circles minigame: freeze boss/player, no score tick
            minigame_state["time_left"] -= 1.0 / FPS
            if minigame_state["time_left"] <= 0:
                lives -= 1
                if hit_sound is not None and not muted:
                    hit_sound.set_volume(min(1.0, hit_volume))
                    hit_sound.play()
                shake = SHAKE_AMOUNT
                minigame_state = None  # will skip minigame draw below
                boss.reset_attacks_after_minigame()
                player.invuln_timer = 5 * FPS  # 5 s immunity after minigame (still took 1 life above)
            if shake > 0:
                shake *= SHAKE_DECAY
                if shake < 0.5:
                    shake = 0
            offset_x = int((random.random() - 0.5) * shake) if shake else 0
            offset_y = int((random.random() - 0.5) * shake) if shake else 0
            last_offset_x, last_offset_y = offset_x, offset_y
            draw_background(screen, background_surface)
            box_rect = soul_box_rect.move(offset_x, offset_y)
            pygame.draw.rect(screen, SOUL_BOX_COLOR, box_rect)
            for i in range(SOUL_BOX_BORDER_THICKNESS):
                pygame.draw.rect(screen, SOUL_BOX_BORDER, box_rect.inflate(i * 2, i * 2), 1)
            pygame.draw.rect(screen, ACCENT_WHITE, box_rect, 1)
            boss.draw_attacks(screen)
            for (hx, hy) in healing_pickups:
                pygame.draw.circle(screen, HEAL_PICKUP_COLOR, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS)
                pygame.draw.circle(screen, ACCENT_WHITE, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS, 1)
            player.draw(screen)
            boss.draw(screen)
            if minigame_state is not None:
                for i, (cx, cy, cr) in enumerate(minigame_state["circles"]):
                    if i in minigame_state["clicked"]:
                        continue
                    px, py = int(cx) + offset_x, int(cy) + offset_y
                    if minigame_circle_image is not None:
                        size = cr * 2
                        scaled = pygame.transform.smoothscale(minigame_circle_image, (size, size))
                        rect = scaled.get_rect(center=(px, py))
                        screen.blit(scaled, rect)
                    else:
                        pygame.draw.circle(screen, (255, 220, 100), (px, py), cr)
                        pygame.draw.circle(screen, ACCENT_WHITE, (px, py), cr, 2)
                timer_font = pygame.font.Font(None, 48)
                t = max(0.0, minigame_state["time_left"])
                timer_str = f"{t:.2f} s"
                timer_surf = timer_font.render(timer_str, True, ACCENT_WHITE)
                timer_surf.set_alpha(MINIGAME_TIMER_ALPHA)
                screen.blit(timer_surf, (SCREEN_W // 2 - timer_surf.get_width() // 2, SOUL_BOX_Y - 50 + offset_y))
            font = pygame.font.Font(None, 28)
            lives_text = font.render(f"HP: {'♥' * lives}", True, (255, 80, 80))
            screen.blit(lives_text, (20 + offset_x, 20 + offset_y))
            score_text = font.render(f"Score: {int(game_timer)}", True, ACCENT_WHITE)
            score_x = SOUL_BOX_X + SOUL_BOX_W // 2 - score_text.get_width() // 2 + offset_x
            score_y = SOUL_BOX_Y - 28 + offset_y
            screen.blit(score_text, (score_x, score_y))
            pygame.display.flip()
            continue

        minigame_interval_timer += 1.0 / FPS
        if minigame_interval_timer >= MINIGAME_INTERVAL_SEC:
            minigame_interval_timer = 0.0
            if random.random() < MINIGAME_CHANCE:
                num = random.randint(3, 10)
                duration = MINIGAME_TIME_BY_COUNT[num]
                circles = _minigame_generate_circles(num)
                minigame_state = {"circles": circles, "clicked": set(), "time_left": duration, "num_circles": num}

        game_timer += 1.0 / FPS   # 1 point per second while alive
        keys = pygame.key.get_pressed()
        player.update(keys)
        boss.update(*player.center())

        if not player.is_invulnerable():
            for bullet in boss.get_bullets():
                if player.get_rect().colliderect(bullet.get_rect()):
                    player.hit()
                    lives -= 1
                    if hit_sound is not None and not muted:
                        hit_sound.set_volume(min(1.0, hit_volume))
                        hit_sound.play()
                    shake = SHAKE_AMOUNT
                    break

        # Healing pickups: spawn every HEAL_SPAWN_INTERVAL_SEC while lives < 3, max HEAL_MAX_PICKUPS
        if lives < 3:
            heal_spawn_timer += 1.0 / FPS
            while heal_spawn_timer >= HEAL_SPAWN_INTERVAL_SEC and len(healing_pickups) < HEAL_MAX_PICKUPS:
                rx = SOUL_BOX_X + HEAL_PICKUP_MARGIN + random.random() * (SOUL_BOX_W - 2 * HEAL_PICKUP_MARGIN)
                ry = SOUL_BOX_Y + HEAL_PICKUP_MARGIN + random.random() * (SOUL_BOX_H - 2 * HEAL_PICKUP_MARGIN)
                healing_pickups.append((rx, ry))
                heal_spawn_timer -= HEAL_SPAWN_INTERVAL_SEC
        else:
            heal_spawn_timer = 0.0
        # Collect healing pickups (circle collision with player)
        px, py = player.center()
        for i in range(len(healing_pickups) - 1, -1, -1):
            hx, hy = healing_pickups[i]
            if math.hypot(hx - px, hy - py) < PLAYER_RADIUS + HEAL_PICKUP_RADIUS:
                healing_pickups.pop(i)
                lives = min(3, lives + 1)
                break

        if shake > 0:
            shake *= SHAKE_DECAY
            if shake < 0.5:
                shake = 0

        offset_x = int((random.random() - 0.5) * shake) if shake else 0
        offset_y = int((random.random() - 0.5) * shake) if shake else 0
        last_offset_x, last_offset_y = offset_x, offset_y

        draw_background(screen, background_surface)
        box_rect = soul_box_rect.move(offset_x, offset_y)
        pygame.draw.rect(screen, SOUL_BOX_COLOR, box_rect)
        for i in range(SOUL_BOX_BORDER_THICKNESS):
            pygame.draw.rect(screen, SOUL_BOX_BORDER, box_rect.inflate(i * 2, i * 2), 1)
        pygame.draw.rect(screen, ACCENT_WHITE, box_rect, 1)

        boss.draw_attacks(screen)
        for (hx, hy) in healing_pickups:
            pygame.draw.circle(screen, HEAL_PICKUP_COLOR, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS)
            pygame.draw.circle(screen, ACCENT_WHITE, (int(hx) + offset_x, int(hy) + offset_y), HEAL_PICKUP_RADIUS, 1)
        player.draw(screen)
        boss.draw(screen)

        # Pause button (top-left)
        pause_hover = PAUSE_BUTTON_RECT.collidepoint(mouse_pos)
        pcolor = TITLE_BUTTON_HOVER if pause_hover else TITLE_BUTTON_COLOR
        pygame.draw.rect(screen, pcolor, PAUSE_BUTTON_RECT)
        pygame.draw.rect(screen, TITLE_BUTTON_BORDER, PAUSE_BUTTON_RECT, 2)
        font_small = pygame.font.Font(None, 32)
        pause_text = font_small.render("II", True, ACCENT_WHITE)
        screen.blit(pause_text, pause_text.get_rect(center=PAUSE_BUTTON_RECT.center))

        font = pygame.font.Font(None, 28)
        lives_text = font.render(f"HP: {'♥' * lives}", True, (255, 80, 80))
        screen.blit(lives_text, (20 + offset_x, 20 + offset_y))
        score_text = font.render(f"Score: {int(game_timer)}", True, ACCENT_WHITE)
        score_x = SOUL_BOX_X + SOUL_BOX_W // 2 - score_text.get_width() // 2 + offset_x
        score_y = SOUL_BOX_Y - 28 + offset_y
        screen.blit(score_text, (score_x, score_y))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
