"""Boss entity and attack orchestration. Customize ATTACK_CLASSES to change behavior."""

import pygame
from config import BOSS_X, BOSS_Y, BOSS_SIZE, BOSS_COLOR, ACCENT_MAGENTA, BOSS_IMAGE_PATH
from attacks import (
    AttackSpread,
    AttackGroundSpikes,
    AttackAimed,
    AttackMiniSpikes,
    PassiveRandomAimed,
    RevolvingSaw,
)

# Add or remove attack classes here to customize the boss (saws + random aimed bullets are passive, always present)
ATTACK_CLASSES = [
    AttackSpread,
    AttackGroundSpikes,
    AttackAimed,
    AttackMiniSpikes,
]


class Boss:
    def __init__(self):
        self.x = BOSS_X
        self.y = BOSS_Y
        self.size = BOSS_SIZE
        self.color = BOSS_COLOR
        self.attack_index = 0
        self.current_attack = None
        self.cooldown_timer = 0
        self._image = None
        # Saws always revolve around the soul box (not an attack, permanent hazard)
        self.revolving_saws = [
            RevolvingSaw(0),
            RevolvingSaw(0.25),
            RevolvingSaw(0.5),
            RevolvingSaw(0.75),
        ]
        # Passive random aimed bullets: every 2s, 3 bullets from perimeter toward player, 0.5s path preview
        self.passive_random_aimed = PassiveRandomAimed()
        if BOSS_IMAGE_PATH:
            try:
                img = pygame.image.load(BOSS_IMAGE_PATH)
                img.set_colorkey((0, 0, 0))
                self._image = pygame.transform.smoothscale(img, (self.size * 2, self.size * 2))
            except (pygame.error, FileNotFoundError):
                self._image = None

    def start_attack(self, player_x, player_y):
        """Start next attack in rotation. Pass player position for aimed attacks."""
        if self.current_attack is not None:
            return
        Klass = ATTACK_CLASSES[self.attack_index % len(ATTACK_CLASSES)]
        self.attack_index += 1
        self.current_attack = Klass()
        # Aimed attack gets player position
        if isinstance(self.current_attack, AttackAimed):
            self.current_attack.start(self.x, self.y, player_x, player_y)
        else:
            self.current_attack.start(self.x, self.y)
        self.cooldown_timer = 0

    def update(self, player_x, player_y):
        for saw in self.revolving_saws:
            saw.update()
        self.passive_random_aimed.update(player_x, player_y)
        if self.current_attack is not None:
            self.current_attack.update(self.x, self.y, player_x, player_y)
            if self.current_attack.finished:
                self.cooldown_timer = self.current_attack.cooldown
                self.current_attack = None
        else:
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1
            else:
                self.start_attack(player_x, player_y)

    def draw(self, surface):
        if self._image is not None:
            rect = self._image.get_rect(center=(self.x, self.y))
            surface.blit(self._image, rect)
        else:
            # Fallback: geometric boss shape
            rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect, 3)
            pygame.draw.rect(surface, ACCENT_MAGENTA, rect.inflate(-10, -10), 2)
            cx, cy = self.x, self.y
            r = self.size // 4
            points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surface, ACCENT_MAGENTA, points, 2)

    def get_bullets(self):
        hazards = list(self.revolving_saws)
        hazards.extend(self.passive_random_aimed.get_bullets())
        if self.current_attack is not None:
            hazards.extend(self.current_attack.get_bullets())
        return hazards

    def reset_attacks_after_minigame(self):
        """Clear all attacks and give a short grace period so the player isn't hit right after the minigame."""
        self.current_attack = None
        self.cooldown_timer = 90   # 1.5 sec at 60fps before next main attack
        self.passive_random_aimed.bullets = []
        self.passive_random_aimed.timer = 0
        self.passive_random_aimed.phase = "idle"
        self.passive_random_aimed.preview_timer = 0

    def draw_attacks(self, surface):
        for saw in self.revolving_saws:
            saw.draw(surface)
        self.passive_random_aimed.draw(surface)
        if self.current_attack is not None:
            self.current_attack.draw(surface)
