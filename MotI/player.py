"""Undertale red-soul style player: confined to a box, move with arrow keys."""

import math
import pygame
from config import (
    SOUL_BOX_X, SOUL_BOX_Y, SOUL_BOX_W, SOUL_BOX_H,
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_COLOR, PLAYER_SAFE_COLOR,
)


class Player:
    """Red soul that can only move within the soul box."""

    def __init__(self):
        self.x = SOUL_BOX_X + SOUL_BOX_W // 2
        self.y = SOUL_BOX_Y + SOUL_BOX_H // 2
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.invuln_timer = 0
        self.invuln_duration = 90  # ~1.5 sec at 60fps

    def get_bounds(self):
        """Movement bounds (inside the box with margin)."""
        margin = self.radius + 2
        return (
            SOUL_BOX_X + margin,
            SOUL_BOX_Y + margin,
            SOUL_BOX_X + SOUL_BOX_W - margin,
            SOUL_BOX_Y + SOUL_BOX_H - margin,
        )

    def update(self, keys):
        left, top, right, bottom = self.get_bounds()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        if dx and dy:
            # Normalize diagonal so speed is consistent
            d = math.sqrt(dx * dx + dy * dy)
            dx = dx / d * self.speed
            dy = dy / d * self.speed

        self.x = max(left, min(right, self.x + dx))
        self.y = max(top, min(bottom, self.y + dy))

        if self.invuln_timer > 0:
            self.invuln_timer -= 1

    def hit(self):
        """Called when hit by a bullet; starts invulnerability."""
        self.invuln_timer = self.invuln_duration

    def is_invulnerable(self):
        return self.invuln_timer > 0

    def draw(self, surface):
        # Blink when invulnerable
        if self.is_invulnerable() and (self.invuln_timer // 4) % 2 == 0:
            return
        color = PLAYER_SAFE_COLOR if self.is_invulnerable() else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        # Small highlight for JS&B style
        pygame.draw.circle(
            surface, (255, 200, 200),
            (int(self.x) - 2, int(self.y) - 2), 2
        )

    def get_rect(self):
        """For collision (circle as rect for simplicity)."""
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )

    def center(self):
        return self.x, self.y
