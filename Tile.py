import csv
import os
import pygame
from Player import Player
from Enemy import Enemy
from Coin import Coin


class Tile(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        pygame.sprite.Sprite.__init__(self)
        original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, (64, 64))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class TileMap:
    def __init__(self, filename, map_name, player_character_name):
        self.tile_size = 64
        self.start_x, self.start_y = 0, 0
        self.player_character_name = player_character_name

        # Enemy configuration dictionary
        self.enemy_config = {
            "Snake": {"width": 72, "height": 32, "sprite_name": "Snake"},
            "Scorpio": {"width": 80, "height": 48, "sprite_name": "Scorpio"},
            "Hyena": {"width": 108, "height": 56, "sprite_name": "Hyena", "speed": 3},
            "Mummy": {"width": 52, "height": 84, "sprite_name": "Mummy"},
            "Deceased": {"width": 42, "height": 84, "sprite_name": "Deceased"},
            "Vulture": {"width": 42, "height": 84, "sprite_name": "Deceased"}
        }

        self.tiles, self.map_size, self.player, self.enemies, self.coins = self.load_tiles(filename, map_name)
        if self.map_size:
            self.map_w, self.map_h = self.map_size
            self.map_surf = pygame.Surface((self.map_w, self.map_h)).convert_alpha()
            self.map_surf.set_colorkey((0, 0, 0))
            self.load_map()
        else:
            # Handle error: map could not be loaded
            print(f"Error: Map size not determined for {filename}. Map surface not created.")
            self.map_surf = None
            self.map_w, self.map_h = 0, 0

    def draw_map(self, surf, offset_x, offset_y):
        if self.map_surf:
            surf.blit(self.map_surf, (0 - offset_x, 0 - offset_y))

    def load_map(self):
        if not self.map_surf:
            return
        for tile in self.tiles:
            tile.draw(self.map_surf)

    def read_csv(self, filename):
        map_data = []
        try:
            with open(os.path.join(filename)) as data:
                data = csv.reader(data, delimiter=',')
                for row in data:
                    map_data.append(list(row))
        except FileNotFoundError:
            print(f"Error: Map file not found at {filename}")
            return None
        return map_data

    def load_tiles(self, filename, map_name):  # map_name is the theme for tile assets
        tiles = []
        coins = []
        enemies = []
        player = None
        map_data = self.read_csv(filename)

        if not map_data:
            return tiles, None, player, enemies, coins  # Return None if map reading failed

        x, y = 0, 0
        max_x = 0

        for row_index, row in enumerate(map_data):
            x = 0
            for col_index, tile_val in enumerate(row):
                # Check if it's a numeric tile (terrain)
                if tile_val.isdigit() or (tile_val.startswith('-') and tile_val[1:].isdigit()):
                    tile_num = int(tile_val)
                    if tile_num >= 0:
                        path = f'assets/Tile/{map_name}/{tile_num + 1}.png'
                        if os.path.exists(path):
                            tiles.append(Tile(path, x * self.tile_size, y * self.tile_size))
                        else:
                            print(f"Warning: Tile image not found: {path}")

                elif tile_val == "Player":
                    player = Player(x * self.tile_size + self.tile_size // 2,
                                    y * self.tile_size + self.tile_size,
                                    50, 70, self.player_character_name)  #

                elif tile_val == "Coin":
                    coin = Coin(x * self.tile_size + self.tile_size // 2,
                               y * self.tile_size + self.tile_size // 2)
                    coins.append(coin)

                elif tile_val.startswith("E_"):
                    enemy_type = tile_val[2:]
                    if enemy_type in self.enemy_config:
                        config = self.enemy_config[enemy_type]
                        enemy = Enemy(
                            x * self.tile_size,
                            y * self.tile_size,
                            config["width"],
                            config["height"],
                            config["sprite_name"],
                            config.get("speed", 1)
                        )
                        enemies.append(enemy)
                    else:
                        print(f"Warning: Unknown enemy type '{enemy_type}' at position ({x}, {y})")

                elif tile_val in self.enemy_config:
                    config = self.enemy_config[tile_val]
                    enemy = Enemy(
                        x * self.tile_size,
                        y * self.tile_size,
                        config["width"],
                        config["height"],
                        config["sprite_name"],
                        config.get("speed", 1)
                    )
                    enemies.append(enemy)

                elif tile_val != "-1" and tile_val.strip():
                    print(f"Warning: Unknown tile type '{tile_val}' at position ({x}, {y})")

                x += 1
            if x > max_x:  # Determine max width for map_size
                max_x = x
            y += 1

        map_w_calc = max_x * self.tile_size
        map_h_calc = y * self.tile_size
        map_size_val = (map_w_calc, map_h_calc)

        return tiles, map_size_val, player, enemies, coins