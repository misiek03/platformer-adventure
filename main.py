from os.path import join, isfile

import pygame
import random
import math
import csv
import os
# from os import listdir
# from os.path import isfile, join


pygame.init()

pygame.display.set_caption("My Game")

SIZE = WIDTH, HEIGHT = 1280, 960
FPS = 60
PLAYER_VEL = 5

screen = pygame.display.set_mode(SIZE)

zombie_surf = pygame.transform.scale_by(pygame.image.load("assets/Player/zombie1.png"), 2)
zombie_rect = zombie_surf.get_rect()

background = pygame.image.load("assets/BG.png").convert()

class Tile(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        pygame.sprite.Sprite.__init__(self)
        original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class TileMap():
    def __init__(self, filename):
        self.tile_size = 64
        self.start_x, self.start_y = 0, 0
        self.tiles = self.load_tiles(filename)
        self.map_surf = pygame.Surface((self.map_w, self.map_h))
        self.map_surf.set_colorkey((0, 0, 0))
        self.load_map()

    def draw_map(self, surf):
        surf.blit(self.map_surf, (0, 0))

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surf)

    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map

    def load_tiles(self, filename):
        tiles = []
        map = self.read_csv(filename)
        x, y = 0, 0

        for row in map:
            x = 0
            for tile in row:
                tile = int(tile)
                if 0 <= int(tile) <= 15:
                    path = f'assets/Tile/{tile+1}.png'
                    print("SCiezka", path)
                    tiles.append(Tile(path, x * self.tile_size, y * self.tile_size))
                x += 1
            y += 1

        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def trim_sprite(sprite):
    mask = pygame.mask.from_surface(sprite)
    rect = mask.get_bounding_rects()[0]  # granica nieprzezroczystych pikseli
    trimmed = sprite.subsurface(rect).copy()

    return trimmed

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in os.listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            surface = trim_sprite(surface)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprite_sheet

    return all_sprites

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 10
    CHARACTER_NAME = "Woodcutter"
    SPRITES = load_sprite_sheets("Player", CHARACTER_NAME, 48, 48, True)
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

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

    def loop(self, fps):
        # self.y_vel = self.GRAVITY
        self.move(self.x_vel, self.y_vel)

    def draw(self, screen):
        sprite = self.SPRITES[self.CHARACTER_NAME + "_idle_" + self.direction][0]
        screen.blit(sprite, (self.rect.x, self.rect.y))


def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if(keys[pygame.K_RIGHT]):
        player.move_right(PLAYER_VEL)

def draw(screen, background, map, player):
    screen.blit(background, (0, 0))
    map.draw_map(screen)
    player.draw(screen)
    pygame.display.flip()


def main(screen):
    clock = pygame.time.Clock()

    map = TileMap("assets/maps/MainMap.csv")
    player = Player(WIDTH - 50, HEIGHT - 50, 50, 50)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        player.loop(FPS)
        handle_move(player)
        draw(screen, background, map, player)
        clock.tick(FPS)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(screen)

