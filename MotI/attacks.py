"""
Customizable attack system for the boss.
Define new attacks by subclassing AttackPattern and spawning bullets.
"""

import math
import random
import pygame
import os
from config import (
    BOSS_X, BOSS_Y, BULLET_RADIUS, BULLET_HITBOX_RADIUS, BULLET_SPEED, BULLET_COLOR,
    BULLET_ROTATION_OFFSET,
    SOUL_BOX_X, SOUL_BOX_Y, SOUL_BOX_W, SOUL_BOX_H,
    SCREEN_W, SCREEN_H,
    DANGER_COLOR, ACCENT_CYAN, ACCENT_MAGENTA, PLAYER_RADIUS,
)

# Image paths
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SAW_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "saw.png")
EXCLAMATION_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "exclamation.png")
SPIKE_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "spike.png")
BULLET_IMAGE_PATH = os.path.join(_PROJECT_DIR, "assets", "bullet.png")


class Bullet:
    """Single projectile. Move with vx, vy; despawn when off-screen."""

    _image = None  # class-level, bullet sprite (points left by default)

    def __init__(self, x, y, vx, vy, radius=None, color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius or BULLET_RADIUS
        self.color = color or DANGER_COLOR
        if Bullet._image is None:
            try:
                img = pygame.image.load(BULLET_IMAGE_PATH).convert_alpha()
                # Scale to ~2x radius for visibility
                size = max(self.radius * 2, 16)
                Bullet._image = pygame.transform.smoothscale(img, (size * 2, size))
            except (pygame.error, FileNotFoundError):
                Bullet._image = False

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def is_off_screen(self, margin=60):
        """True when bullet has flown off-screen (despawn)."""
        return (
            self.x < -margin or self.x > SCREEN_W + margin
            or self.y < -margin or self.y > SCREEN_H + margin
        )

    def draw(self, surface):
        if Bullet._image and Bullet._image is not False:
            # Sprite tip faces direction of travel. Pygame rotates CCW; +x = 0°, +y = down.
            angle = math.atan2(self.vy, self.vx)
            if abs(self.vx) < 1e-6 and abs(self.vy) < 1e-6:
                angle = 0
            # Sprite points left (-x); rotate so tip faces velocity
            rotation_deg = math.degrees(angle) + 180 - BULLET_ROTATION_OFFSET
            rotated = pygame.transform.rotate(Bullet._image, rotation_deg)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated, rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        """Small circular hitbox centered on bullet (along its flight path)."""
        r = BULLET_HITBOX_RADIUS
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def is_inside_soul_box(self):
        """Rough check: bullet matters for collision when near the box."""
        return (
            SOUL_BOX_X - 50 < self.x < SOUL_BOX_X + SOUL_BOX_W + 50
            and SOUL_BOX_Y - 50 < self.y < SOUL_BOX_Y + SOUL_BOX_H + 50
        )


def _perimeter_position(t):
    """t in [0, 1) -> (x, y) on the soul box perimeter (clockwise from top-left)."""
    perim = 2 * SOUL_BOX_W + 2 * SOUL_BOX_H
    pos = (t % 1.0) * perim
    W, H = SOUL_BOX_W, SOUL_BOX_H
    if pos < W:
        return (SOUL_BOX_X + pos, SOUL_BOX_Y)
    if pos < W + H:
        return (SOUL_BOX_X + W, SOUL_BOX_Y + (pos - W))
    if pos < 2 * W + H:
        return (SOUL_BOX_X + (2 * W + H - pos), SOUL_BOX_Y + H)
    return (SOUL_BOX_X, SOUL_BOX_Y + (2 * W + 2 * H - pos))


class RevolvingSaw:
    """Saw that orbits the soul box edge and spins on its center like a sawblade. Always present (not an attack)."""
    radius = 14
    speed = 0.012  # fraction of perimeter per frame (orbit speed)
    spin_speed = 0.4  # radians per frame (spin on center, sawblade effect)
    _image = None

    def __init__(self, t_offset):
        self.t = t_offset
        self.x, self.y = _perimeter_position(self.t)
        self.spin = 0.0  # rotation angle for drawing
        if RevolvingSaw._image is None:
            try:
                img = pygame.image.load(SAW_IMAGE_PATH).convert_alpha()
                size = self.radius * 2 + 8  # Slightly larger for visibility
                RevolvingSaw._image = pygame.transform.smoothscale(img, (size, size))
                RevolvingSaw._image_radius = size // 2
            except (pygame.error, FileNotFoundError):
                RevolvingSaw._image = False  # Mark as failed
                RevolvingSaw._image_radius = self.radius

    def update(self):
        self.t = (self.t + RevolvingSaw.speed) % 1.0
        self.x, self.y = _perimeter_position(self.t)
        self.spin += RevolvingSaw.spin_speed

    def get_rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def is_inside_soul_box(self):
        return True

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = self.radius
        if RevolvingSaw._image and RevolvingSaw._image is not False:
            # Spin on center: rotate image around its center, then blit centered at (cx, cy)
            rotated = pygame.transform.rotate(RevolvingSaw._image, math.degrees(self.spin))
            rect = rotated.get_rect(center=(cx, cy))
            surface.blit(rotated, rect)
        else:
            # Fallback: draw circle
            pygame.draw.circle(surface, DANGER_COLOR, (cx, cy), r)
            pygame.draw.circle(surface, (200, 60, 90), (cx, cy), r, 2)


class SpikeHitbox:
    """Simple hitbox for ground spike; get_rect() returns current rect or empty."""
    def __init__(self):
        self.rect = None

    def get_rect(self):
        return self.rect if self.rect is not None else pygame.Rect(0, 0, 0, 0)


class AttackPattern:
    """Base class for one attack. Override start() to spawn bullets."""

    name = "Base"
    duration = 180  # frames this attack runs (then boss switches)
    cooldown = 30   # frames before next attack

    def __init__(self):
        self.timer = 0
        self.bullets = []
        self.finished = False

    def start(self, boss_x, boss_y):
        """Spawn initial bullets. Override in subclasses."""
        self.timer = 0
        self.bullets = []
        self.finished = False

    def update(self, boss_x, boss_y, player_x=None, player_y=None):
        self.timer += 1
        for b in self.bullets:
            b.update()
        # Despawn bullets when they fly off-screen; other hazards (e.g. SpikeHitbox) stay
        self.bullets = [b for b in self.bullets if not (hasattr(b, 'is_off_screen') and b.is_off_screen())]
        if self.timer >= self.duration:
            self.finished = True

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)

    def get_bullets(self):
        return self.bullets


# --------------- Basic attacks (customize or add more) ---------------

class AttackSpread(AttackPattern):
    """Fan of bullets toward the soul box. Flight path shown in transparent red for 1s before bullets fire."""
    name = "Spread"
    preview_frames = 60   # 1 second of path preview
    duration = 60 + 120   # preview + bullet phase
    cooldown = 45
    path_length = 380     # how far to draw the preview line
    path_alpha = 100      # transparency for path (0-255)

    def start(self, boss_x, boss_y):
        self.timer = 0
        self.finished = False
        self.bullets = []
        self._boss_x = boss_x
        self._boss_y = boss_y
        center_soul_x = SOUL_BOX_X + SOUL_BOX_W // 2
        center_soul_y = SOUL_BOX_Y + SOUL_BOX_H // 2
        num = 9
        base_angle = math.atan2(center_soul_y - boss_y, center_soul_x - boss_x)
        spread = math.radians(50)
        self._path_angles = []
        for i in range(num):
            angle = base_angle - spread / 2 + spread * i / max(1, num - 1)
            vx = math.cos(angle) * BULLET_SPEED
            vy = math.sin(angle) * BULLET_SPEED
            self._path_angles.append((vx, vy))

    def update(self, boss_x, boss_y, player_x=None, player_y=None):
        self.timer += 1
        if self.timer == self.preview_frames:
            for vx, vy in self._path_angles:
                self.bullets.append(Bullet(self._boss_x, self._boss_y, vx, vy))
        if self.bullets:
            for b in self.bullets:
                b.update()
            self.bullets = [b for b in self.bullets if not (hasattr(b, 'is_off_screen') and b.is_off_screen())]
        if self.timer >= self.duration:
            self.finished = True

    def draw(self, surface):
        if self.timer < self.preview_frames and hasattr(self, '_path_angles'):
            # Draw transparent red flight paths (1 second warning)
            path_surf = pygame.Surface((self.path_length * 2, self.path_length * 2), pygame.SRCALPHA)
            path_surf.fill((0, 0, 0, 0))
            cx, cy = self.path_length, self.path_length
            path_color = (255, 80, 120, self.path_alpha)
            for vx, vy in self._path_angles:
                d = math.sqrt(vx * vx + vy * vy) or 1
                ex = cx + (vx / d) * self.path_length
                ey = cy + (vy / d) * self.path_length
                pygame.draw.line(path_surf, path_color, (cx, cy), (ex, ey), 5)
            surface.blit(path_surf, (self._boss_x - self.path_length, self._boss_y - self.path_length))
        else:
            for b in self.bullets:
                b.draw(surface)


class AttackHorizontalLine(AttackPattern):
    """Horizontal line of bullets across the soul box."""
    name = "Horizontal Line"
    duration = 90
    cooldown = 60

    def start(self, boss_x, boss_y):
        super().start(boss_x, boss_y)
        y = SOUL_BOX_Y + SOUL_BOX_H // 2
        for x in range(SOUL_BOX_X, SOUL_BOX_X + SOUL_BOX_W + 1, 25):
            # From left to right
            self.bullets.append(Bullet(x, SOUL_BOX_Y - 20, 0, BULLET_SPEED, color=ACCENT_CYAN))
        for x in range(SOUL_BOX_X, SOUL_BOX_X + SOUL_BOX_W + 1, 25):
            # From top
            self.bullets.append(Bullet(x, SOUL_BOX_Y - 20, 0, BULLET_SPEED * 0.7, color=ACCENT_MAGENTA))


class AttackCircle(AttackPattern):
    """Circle of bullets expanding from boss."""
    name = "Circle"
    duration = 150
    cooldown = 50

    def start(self, boss_x, boss_y):
        super().start(boss_x, boss_y)
        n = 16
        for i in range(n):
            angle = 2 * math.pi * i / n
            vx = math.cos(angle) * BULLET_SPEED
            vy = math.sin(angle) * BULLET_SPEED
            self.bullets.append(Bullet(boss_x, boss_y, vx, vy))


class AttackAimed(AttackPattern):
    """Few bullets aimed at current soul position (pass player pos when starting for true aim)."""
    name = "Aimed"
    duration = 100
    cooldown = 40

    def start(self, boss_x, boss_y, target_x=None, target_y=None):
        super().start(boss_x, boss_y)
        tx = target_x if target_x is not None else SOUL_BOX_X + SOUL_BOX_W // 2
        ty = target_y if target_y is not None else SOUL_BOX_Y + SOUL_BOX_H // 2
        for _ in range(3):
            angle = math.atan2(ty - boss_y, tx - boss_x)
            angle += math.radians(random.uniform(-12, 12))
            vx = math.cos(angle) * (BULLET_SPEED * 1.2)
            vy = math.sin(angle) * (BULLET_SPEED * 1.2)
            self.bullets.append(Bullet(boss_x, boss_y, vx, vy))


class AttackWave(AttackPattern):
    """Sine-wave style bullets from the top."""
    name = "Wave"
    duration = 180
    cooldown = 40

    def start(self, boss_x, boss_y):
        super().start(boss_x, boss_y)
        for i in range(12):
            x = SOUL_BOX_X + (SOUL_BOX_W * (i / 11))
            self.bullets.append(Bullet(x, SOUL_BOX_Y - 10, 0, BULLET_SPEED))
        # Second wave offset
        for i in range(12):
            x = SOUL_BOX_X + (SOUL_BOX_W * (i / 11)) + 15
            self.bullets.append(Bullet(x, SOUL_BOX_Y - 10, 0, BULLET_SPEED * 0.8, color=ACCENT_CYAN))


# --------------- New attacks: revolving saws, ground spikes, mini spikes ---------------

class AttackRevolvingSaws(AttackPattern):
    """4 spiky saws revolving around the edge of the soul box; spin fast and stay whole phase."""
    name = "Revolving Saws"
    duration = 480   # 8 sec - saws stay the whole time, then next attack
    cooldown = 50

    def start(self, boss_x, boss_y):
        super().start(boss_x, boss_y)
        self.bullets = [
            RevolvingSaw(0),
            RevolvingSaw(0.25),
            RevolvingSaw(0.5),
            RevolvingSaw(0.75),
        ]


class AttackGroundSpikes(AttackPattern):
    """3 spikes from bottom, full height, consecutive random order, fast with 0.5s between."""
    name = "Ground Spikes"
    first_spike_warning_frames = 60  # 1 second for first spike (give player time to react)
    warning_frames = 12   # subsequent spikes
    spike_frames = 18
    wait_frames = 30     # 0.5 sec between spikes
    slot_width = SOUL_BOX_W // 3
    spike_height = SOUL_BOX_H   # full soul box height
    duration = (first_spike_warning_frames + spike_frames + wait_frames) + 2 * (warning_frames + spike_frames + wait_frames)

    def __init__(self):
        super().__init__()
        self.slots_order = []
        self.phase = "warning"  # "warning" | "spike" | "wait"
        self.slot_index = 0
        self.phase_timer = 0
        self.spike_hitbox = SpikeHitbox()
        self.warning_rect = None
        # Load images
        self._exclamation_img = None
        self._spike_img = None
        try:
            ex_img = pygame.image.load(EXCLAMATION_IMAGE_PATH).convert_alpha()
            self._exclamation_img = pygame.transform.smoothscale(ex_img, (60, 60))
        except (pygame.error, FileNotFoundError):
            self._exclamation_img = False
        try:
            spike_img = pygame.image.load(SPIKE_IMAGE_PATH).convert_alpha()
            self._spike_img = spike_img
        except (pygame.error, FileNotFoundError):
            self._spike_img = False

    def start(self, boss_x, boss_y):
        self.timer = 0
        self.finished = False
        self.bullets = []
        self.slots_order = [0, 1, 2]
        random.shuffle(self.slots_order)
        self.phase = "warning"
        self.slot_index = 0
        self.phase_timer = 0
        self.spike_hitbox.rect = None
        self.warning_rect = self._slot_rect(self.slots_order[0])

    def _slot_rect(self, slot):
        """Rect for this slot: full height of soul box (spike from bottom to top)."""
        x = SOUL_BOX_X + slot * self.slot_width
        return pygame.Rect(x, SOUL_BOX_Y, self.slot_width, self.spike_height)

    def update(self, boss_x, boss_y, player_x=None, player_y=None):
        self.timer += 1
        self.phase_timer += 1
        if self.phase == "warning":
            self.warning_rect = self._slot_rect(self.slots_order[self.slot_index])
            self.spike_hitbox.rect = None
            required = self.first_spike_warning_frames if self.slot_index == 0 else self.warning_frames
            if self.phase_timer >= required:
                self.phase = "spike"
                self.phase_timer = 0
                self.spike_hitbox.rect = self._slot_rect(self.slots_order[self.slot_index])
        elif self.phase == "spike":
            self.warning_rect = None
            if self.phase_timer >= self.spike_frames:
                self.spike_hitbox.rect = None
                self.phase = "wait"
                self.phase_timer = 0
        else:
            # wait phase (0.5s between spikes)
            self.warning_rect = None
            self.spike_hitbox.rect = None
            if self.phase_timer >= self.wait_frames:
                self.slot_index += 1
                if self.slot_index >= 3:
                    self.finished = True
                    return
                self.phase = "warning"
                self.phase_timer = 0
                self.warning_rect = self._slot_rect(self.slots_order[self.slot_index])
        if self.timer >= self.duration:
            self.finished = True

    def get_bullets(self):
        if self.spike_hitbox.rect is None:
            return []
        return [self.spike_hitbox]

    def draw(self, surface):
        if self.warning_rect is not None:
            # Translucent red glow
            s = pygame.Surface((self.warning_rect.width, self.warning_rect.height))
            s.set_alpha(120)
            s.fill((255, 60, 80))
            surface.blit(s, self.warning_rect.topleft)
            pygame.draw.rect(surface, (255, 100, 120), self.warning_rect, 2)
            # Exclamation mark image
            if self._exclamation_img and self._exclamation_img is not False:
                ex_rect = self._exclamation_img.get_rect(center=self.warning_rect.center)
                surface.blit(self._exclamation_img, ex_rect)
            else:
                # Fallback: text
                font = pygame.font.Font(None, 36)
                ex = font.render("!", True, (255, 200, 200))
                r = ex.get_rect(center=self.warning_rect.center)
                surface.blit(ex, r)
        if self.spike_hitbox.rect is not None:
            r = self.spike_hitbox.rect
            if self._spike_img and self._spike_img is not False:
                # Scale spike image to fit the rect (full height)
                scaled = pygame.transform.smoothscale(self._spike_img, (r.width, r.height))
                surface.blit(scaled, r.topleft)
            else:
                # Fallback: draw rect
                pygame.draw.rect(surface, DANGER_COLOR, r)
                pygame.draw.rect(surface, (200, 50, 70), r, 2)
                # Spike teeth at top of rect
                for i in range(5):
                    x1 = r.left + (r.width * i) // 4
                    x2 = r.left + (r.width * (i + 1)) // 4
                    pygame.draw.polygon(surface, (180, 40, 60), [
                        (x1, r.bottom), (x2, r.bottom), ((x1 + x2) // 2, r.top),
                    ])


class AttackMiniSpikes(AttackPattern):
    """Boss shoots player-sized mini spikes every 0.5s for 10s, aimed at player at spawn. Bullets despawn only when off-screen."""
    name = "Mini Spikes"
    duration = 600   # 10 sec at 60fps (stop spawning after this)
    cooldown = 40
    spawn_interval = 30   # 0.5 sec
    mini_speed = 3.4     # faster bullets
    mini_radius = PLAYER_RADIUS

    def start(self, boss_x, boss_y):
        super().start(boss_x, boss_y)
        self.next_spawn = 0

    def update(self, boss_x, boss_y, player_x=None, player_y=None):
        self.timer += 1
        if self.timer >= self.next_spawn and self.timer < self.duration:
            # Aim at where the player was when this spike spawned
            if player_x is not None and player_y is not None:
                tx, ty = player_x, player_y
            else:
                tx = SOUL_BOX_X + SOUL_BOX_W // 2
                ty = SOUL_BOX_Y + SOUL_BOX_H // 2
            angle = math.atan2(ty - boss_y, tx - boss_x)
            vx = math.cos(angle) * self.mini_speed
            vy = math.sin(angle) * self.mini_speed
            self.bullets.append(Bullet(boss_x, boss_y, vx, vy, radius=self.mini_radius, color=DANGER_COLOR))
            self.next_spawn = self.timer + self.spawn_interval
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]
        # Attack ends only when we've stopped spawning AND all bullets have flown off-screen
        if self.timer >= self.duration and len(self.bullets) == 0:
            self.finished = True


def _bullet_has_left_soul_box(bullet, margin=10):
    """True when bullet has fully left the soul box (despawn after crossing)."""
    return (
        bullet.x < SOUL_BOX_X - margin or bullet.x > SOUL_BOX_X + SOUL_BOX_W + margin
        or bullet.y < SOUL_BOX_Y - margin or bullet.y > SOUL_BOX_Y + SOUL_BOX_H + margin
    )


def _random_point_in_soul_box(margin=20):
    """Return (x, y) of a random point inside the soul box with margin from the edges."""
    x = SOUL_BOX_X + margin + random.random() * (SOUL_BOX_W - 2 * margin)
    y = SOUL_BOX_Y + margin + random.random() * (SOUL_BOX_H - 2 * margin)
    return (x, y)


class PassiveRandomAimed:
    """Passive hazard: every 2 sec, 4 bullets from one random perimeter point — 2 at player, 2 at random points inside box. 0.5s path preview. Despawn only when fully past soul box."""
    spawn_interval = 120      # 2 sec at 60fps
    preview_frames = 30       # 0.5 sec path preview
    bullets_per_volley = 4    # 2 at player, 2 toward random points in box
    bullet_speed = BULLET_SPEED
    path_length = 350
    path_alpha = 100

    def __init__(self):
        self.bullets = []
        self.timer = 0
        self.phase = "idle"
        self.preview_timer = 0
        self._spawn_points = []   # [(sx,sy,vx,vy), ...]
        self._target = None

    def update(self, player_x, player_y):
        tx = player_x if player_x is not None else SOUL_BOX_X + SOUL_BOX_W // 2
        ty = player_y if player_y is not None else SOUL_BOX_Y + SOUL_BOX_H // 2
        if self.phase == "idle":
            self.timer += 1
            if self.timer >= self.spawn_interval:
                self.phase = "preview"
                self.preview_timer = 0
                self._target = (tx, ty)
                self._spawn_points = []
                # 2 bullets aimed at player, each from a different perimeter point
                for _ in range(2):
                    sx, sy = _perimeter_position(random.random())
                    angle_aimed = math.atan2(ty - sy, tx - sx)
                    vx_a = math.cos(angle_aimed) * self.bullet_speed
                    vy_a = math.sin(angle_aimed) * self.bullet_speed
                    self._spawn_points.append((sx, sy, vx_a, vy_a))
                # 2 bullets toward random points inside the soul box, each from a different perimeter point
                for _ in range(2):
                    sx, sy = _perimeter_position(random.random())
                    rx, ry = _random_point_in_soul_box()
                    dx, dy = rx - sx, ry - sy
                    d = math.sqrt(dx * dx + dy * dy) or 1
                    vx = (dx / d) * self.bullet_speed
                    vy = (dy / d) * self.bullet_speed
                    self._spawn_points.append((sx, sy, vx, vy))
        elif self.phase == "preview":
            self.preview_timer += 1
            if self.preview_timer >= self.preview_frames:
                for sx, sy, vx, vy in self._spawn_points:
                    self.bullets.append(Bullet(sx, sy, vx, vy, radius=PLAYER_RADIUS))
                self.phase = "idle"
                self.timer = 0
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if not _bullet_has_left_soul_box(b)]

    def get_bullets(self):
        return list(self.bullets)

    def draw(self, surface):
        if self.phase == "preview" and self._spawn_points:
            path_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            path_color = (255, 80, 120, self.path_alpha)
            for sx, sy, vx, vy in self._spawn_points:
                d = math.sqrt(vx * vx + vy * vy) or 1
                ex = sx + (vx / d) * self.path_length
                ey = sy + (vy / d) * self.path_length
                pygame.draw.line(path_surf, path_color, (sx, sy), (ex, ey), 5)
            surface.blit(path_surf, (0, 0))
        for b in self.bullets:
            b.draw(surface)
