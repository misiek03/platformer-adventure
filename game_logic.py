import pygame
import os
import config
from Player import Player
from Tile import TileMap


def reset_game(character_name, map_csv_file, map_theme):
    map_full_path = os.path.join(config.MAP_ASSETS_PATH, map_csv_file)

    tile_map_obj = TileMap(map_full_path, map_theme, character_name)

    player_obj = tile_map_obj.player
    enemies_list = tile_map_obj.enemies
    coins = tile_map_obj.coins
    current_score = 0
    time_remaining = config.INITIAL_TIME

    map_w, map_h = 0, 0
    if tile_map_obj and tile_map_obj.map_size:
        map_w, map_h = tile_map_obj.map_size
    else:
        print(f"Warning: Map size not available. Using default screen size.")
        map_w, map_h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

    return tile_map_obj, player_obj, enemies_list, current_score, time_remaining, map_w, map_h, coins


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    if not player: return collided_objects
    for obj in objects:
        if hasattr(obj, 'rect') and player.hitbox.colliderect(obj.rect):
            if dy > 0:  # Falling down
                player.rect.bottom = obj.rect.top
                player.hitbox.bottom = obj.rect.top
                player.landed()
            elif dy < 0:  # Jumping
                player.rect.top = obj.rect.bottom
                player.hitbox.top = obj.rect.bottom
                player.hit_head()
            player.update()  # Update player's mask and other properties after position change
            collided_objects.append(obj)
    return collided_objects


def check_horizontal_collision(player, objects, dx):
    if not player:
        return None

    original_x = player.rect.x
    original_hitbox_x = player.hitbox.x

    player.rect.x += dx
    player.hitbox.x += dx
    player.update()

    collided_object = None
    for obj in objects:
        if hasattr(obj, 'rect') and player.hitbox.colliderect(obj.rect):
            collided_object = obj
            break

    # Move player back to original position after check
    player.rect.x = original_x
    player.hitbox.x = original_hitbox_x
    player.update()

    return collided_object


def handle_player_move(player, objects, map_width):
    if not player: return

    keys = pygame.key.get_pressed()

    if player.knockback_timer <= 0:  # Player can control movement
        player.x_vel = 0  # Reset horizontal velocity if no keys are pressed (or allow player class to manage this)

    can_move_left = player.hitbox.left > config.PLAYER_VEL
    can_move_right = player.hitbox.right < map_width - config.PLAYER_VEL

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if can_move_left and not check_horizontal_collision(player, objects, -config.PLAYER_VEL):
            player.move_left(config.PLAYER_VEL)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if can_move_right and not check_horizontal_collision(player, objects, config.PLAYER_VEL):
            player.move_right(config.PLAYER_VEL)


def check_player_fall_off_map(player, map_height):
    if not player:
        return False
    fall_threshold = map_height + 200  # Give some buffer below the map
    return player.rect.top > fall_threshold


def check_enemy_player_collision(player, enemies):
    if not player or player.invincibility_timer > 0:  # Player is invincible
        return False
    for enemy in enemies:
        if hasattr(enemy, 'rect') and enemy.is_alive and enemy.can_damage_player:
            if player.hitbox.colliderect(enemy.rect):
                return True  # Collision detected
    return False


def check_player_attack_on_enemies(player, enemies):
    if not player or not player.is_attacking or not player.attack_hitbox:
        return 0  # No attack or no hitbox

    kills = 0
    for enemy in enemies:
        if hasattr(enemy, 'rect') and enemy.is_alive and not enemy.is_hurt and not enemy.is_dying:
            if player.attack_hitbox.colliderect(enemy.rect):
                if enemy.take_damage():  # take_damage returns True if damage was taken
                    kills += 1
    return kills


def check_coin_collection(player, coins):
    if not player:
        return 0

    points_earned = 0
    for coin in coins:
        if not coin.collected and player.hitbox.colliderect(coin.rect):
            points_earned += coin.collect()

    return points_earned


def is_level_complete(player, map_width):
    if not player: return False
    # Finish line is 32 pixels from the very right edge of the map
    finish_threshold = map_width - 32
    return player.hitbox.centerx >= finish_threshold