import os
from os.path import join, isfile
import pygame


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def trim_sprite(surface):
    mask = pygame.mask.from_surface(surface)
    rect = mask.get_bounding_rects()
    if not rect or rect[0].width == 0 or rect[0].height == 0:
        return surface
    trimmed = surface.subsurface(rect[0]).copy()
    return trimmed


def trim_sprite_sides(surface):
    mask = pygame.mask.from_surface(surface)
    rects = mask.get_bounding_rects()
    if not rects:
        return surface
    x, y, w, h = rects[0]
    trimmed = surface.subsurface(pygame.Rect(x, 0, w, surface.get_height())).copy()
    return trimmed


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in os.listdir(path) if isfile(join(path, f))]

    all_sprites = {}
    scale = 2.5

    if dir2 == "Coin":
        scale = 0.4

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            frame = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            frame.blit(sprite_sheet, (0, 0), pygame.Rect(i * width, 0, width, height))

            if dir1 == "Player":
                trimmed = trim_sprite_sides(frame)
            else:
                trimmed = trim_sprite(frame)

            w2, h2 = int(trimmed.get_width() * scale), int(trimmed.get_height() * scale)
            sprites.append(pygame.transform.scale(trimmed, (w2, h2)))

        key_base = image.replace(".png", "")
        if direction:
            r = "right"
            l = "left"

            if dir1 == "Enemy":
                r = "left"
                l = "right"

            all_sprites[f"{key_base}_{r}"] = sprites
            all_sprites[f"{key_base}_{l}"] = [pygame.transform.flip(s, True, False) for s in sprites]
        else:
            all_sprites[key_base] = sprites

    return all_sprites