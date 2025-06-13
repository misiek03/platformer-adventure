import pygame
from utils import load_sprite_sheets


class Character(pygame.sprite.Sprite):
    GRAVITY = 1
    ANIMATION_DELAY = 6

    def __init__(self, x, y, w, h, asset_folder, character_name):
        super().__init__()
        self.x_vel = 0
        self.y_vel = 0
        self.fall_count = 0
        self.width, self.height = w, h
        self.direction = "left"
        self.animation_count = 0
        self.CHARACTER = character_name
        # Sprites
        self.SPRITES = load_sprite_sheets(asset_folder, self.CHARACTER,48, 48,True)
        self.sprite = self.SPRITES[f"{self.CHARACTER}_idle_{self.direction}"][0]
        self.sprite = pygame.transform.scale(self.sprite, (w, h))
        self.rect = self.sprite.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self, sprite_sheet="idle"):

        sprite_sheet_name = self.CHARACTER + "_" + sprite_sheet + "_" + self.direction

        if sprite_sheet_name not in self.SPRITES:
            sprite_sheet_name = self.CHARACTER + "_idle_" + self.direction

        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1