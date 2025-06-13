import pygame
from utils import load_sprite_sheets
from config import sound_pickup_coin

class Coin(pygame.sprite.Sprite):
    ANIMATION_DELAY = 8  # Slower animation than player for coins

    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 32, 32  # Coin size
        self.animation_count = 0
        self.collected = False

        # Load coin sprites - assuming you have coin animation frames
        # If you don't have animated coins, we'll create a simple rotating effect
        self.SPRITES = load_sprite_sheets("Other", "Coin", 120, 120, False)
        # Try to get coin animation frames
        if "coin" in self.SPRITES:
            self.sprites = self.SPRITES["coin"]

        # Set initial sprite
        self.sprite = self.sprites[0]
        self.rect = self.sprite.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.sprite)

        # Add floating animation
        self.float_offset = 0
        self.float_speed = 0.1
        self.original_y = y

    def update(self):
        """Update coin animation and floating effect"""
        if self.collected:
            return

        # Update animation
        self.animation_count += 1
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.sprite = self.sprites[sprite_index]

        # Update mask for collision detection
        self.mask = pygame.mask.from_surface(self.sprite)

    def collect(self):
        """Mark coin as collected"""
        self.collected = True
        sound_pickup_coin.play()
        return 75  # Return points value

    def draw(self, screen, offset_x, offset_y):
        """Draw the coin if not collected"""
        if not self.collected:
            screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

    def check_collision(self, player_hitbox):
        """Check if coin collides with player"""
        if self.collected:
            return False
        return self.rect.colliderect(player_hitbox)