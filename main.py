# main.py
import pygame
import config
import asset_manager
import ui_manager
import game_logic
import score_store

# --- Pygame Initialization ---
pygame.init()
ui_manager.init_fonts()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Adventure")
clock = pygame.time.Clock()

# --- Global Game Variables ---
game_state = config.MENU_STATE
# Variables for menu selection
selected_character_index = 0
selected_map_index = 0
selected_menu_item_index = 0  # 0: Start, 1: Character, 2: Map

# Variables for score animation
animated_display_score = 0
animated_display_bonus = 0
target_final_score_anim = 0  # For GAME_OVER, this is the total. For LEVEL_COMPLETE, this is the base score part.
target_final_bonus_anim = 0  # For LEVEL_COMPLETE time bonus.
score_animation_phase = 0  # 0: done, 1: animating base score, 2: animating bonus
score_at_end_of_level = 0  # Stores score when player dies/finishes, before bonus calculation for display

# Game play variables
current_map_obj = None
player_obj = None
enemies_list = []
current_score = 0
time_left_seconds = config.INITIAL_TIME
map_width, map_height = 0, 0
camera_offset_x, camera_offset_y = 0, 0
game_over_player_death_timer = 0  # Timer for showing player death before game over screen

# Music and sounds
music_playing = False
score_sound_playing = False
game_over_sound_playing = False

def draw_game_scene(current_game_map, player_instance, game_enemies, cam_offset_x, cam_offset_y, map_w, score_val,
                    time_val, coins_list):
    screen.blit(asset_manager.get_game_background(), (0, 0))

    if current_game_map:
        current_game_map.draw_map(screen, cam_offset_x, cam_offset_y)

    for enemy in list(game_enemies):
        if enemy.is_alive:
            enemy.draw(screen, cam_offset_x, cam_offset_y)

    # Draw coins
    for coin in coins_list:
        coin.draw(screen, cam_offset_x, cam_offset_y)

    if player_instance:
        player_instance.draw(screen, cam_offset_x, cam_offset_y)
        ui_manager.draw_hearts(screen, player_instance.hearts)

    ui_manager.draw_timer(screen, time_val)
    ui_manager.draw_score_hud(screen, score_val)


def main_loop():
    global game_state, selected_character_index, selected_map_index, selected_menu_item_index
    global animated_display_score, animated_display_bonus, target_final_score_anim, target_final_bonus_anim
    global score_animation_phase, score_at_end_of_level
    global current_map_obj, player_obj, enemies_list, current_score, time_left_seconds
    global map_width, map_height, camera_offset_x, camera_offset_y, game_over_player_death_timer
    global music_playing, score_sound_playing, game_over_sound_playing

    asset_manager.load_game_assets()  # Load all assets at the start

    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0  # Delta time in seconds
        # Score increment per frame, adjust for smoother animation
        score_increment_per_frame = int(config.SCORE_ANIMATION_SPEED_PPS * dt)
        if score_increment_per_frame == 0:
            score_increment_per_frame = 1

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == config.MENU_STATE:
                    if event.key == pygame.K_UP:
                        selected_menu_item_index = (selected_menu_item_index - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        selected_menu_item_index = (selected_menu_item_index + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if selected_menu_item_index == 0:  # Start Game
                            available_chars = asset_manager.get_available_characters_list()
                            available_maps = asset_manager.get_available_maps_list()
                            if available_chars and available_maps:
                                char_name = available_chars[selected_character_index]
                                map_file, map_theme, _, bg_filename, bg_scale = available_maps[selected_map_index].values()
                                asset_manager.load_background_for_map(bg_filename, bg_scale)

                                current_map_obj, player_obj, enemies_list, current_score, time_left_seconds, map_width, map_height, coins = game_logic.reset_game(char_name, map_file, map_theme)

                                camera_offset_x, camera_offset_y = 0, 0
                                game_state = config.PLAYING_STATE
                                game_over_player_death_timer = 0
                                score_at_end_of_level = 0  # Reset for new game
                                animated_display_score = 0
                                animated_display_bonus = 0
                                score_animation_phase = 0  # Reset animation phase
                            else:
                                print("Error: No characters or maps available to start game.")

                    # Left/Right for character/map selection when item is highlighted
                    current_chars = asset_manager.get_available_characters_list()
                    current_maps = asset_manager.get_available_maps_list()
                    if selected_menu_item_index == 1 and current_chars:  # Change Character with arrows
                        if event.key == pygame.K_LEFT:
                            selected_character_index = (selected_character_index - 1 + len(current_chars)) % len(
                                current_chars)
                            asset_manager.update_character_preview(current_chars[selected_character_index])
                        elif event.key == pygame.K_RIGHT:
                            selected_character_index = (selected_character_index + 1) % len(current_chars)
                            asset_manager.update_character_preview(current_chars[selected_character_index])
                    elif selected_menu_item_index == 2 and current_maps:  # Change Map with arrows
                        if event.key == pygame.K_LEFT:
                            selected_map_index = (selected_map_index - 1 + len(current_maps)) % len(current_maps)
                        elif event.key == pygame.K_RIGHT:
                            selected_map_index = (selected_map_index + 1) % len(current_maps)

                elif game_state == config.GAME_OVER_STATE or game_state == config.LEVEL_COMPLETE_STATE:
                    if event.key == pygame.K_RETURN and score_animation_phase == 0:  # Return to menu if animation done
                        game_state = config.MENU_STATE
                        selected_menu_item_index = 0  # Reset menu focus to "Start Game"

                elif game_state == config.PLAYING_STATE and player_obj:
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and player_obj.jump_count < 1:
                        player_obj.jump()
                    elif event.key == pygame.K_SPACE:
                        player_obj.attack()

        # --- Game State Logic & Updates ---
        if game_state == config.PLAYING_STATE:
            if not music_playing:
                pygame.mixer.music.play(-1)
                music_playing = True

            game_over_sound_playing = False

            time_left_seconds -= dt

            if time_left_seconds <= 0:
                time_left_seconds = 0
                score_at_end_of_level = current_score
                score_store.score_store.update_high_score(score_at_end_of_level)
                game_state = config.GAME_OVER_STATE
                game_over_player_death_timer = config.GAME_OVER_ANIM_DELAY
                target_final_score_anim = score_at_end_of_level
                target_final_bonus_anim = 0
                animated_display_score = 0
                animated_display_bonus = 0
                score_animation_phase = 1

            # Update enemies
            for enemy in enemies_list:
                if hasattr(current_map_obj, 'tiles'):
                    enemy.loop(current_map_obj.tiles)
                else:
                    enemy.loop([])

            # Update coins animation
            for coin in coins:
                coin.update()

            # Handle player movement and collisions
            game_logic.handle_player_move(player_obj,
                                          current_map_obj.tiles if hasattr(current_map_obj, 'tiles') else [], map_width)

            player_obj.loop(config.FPS)

            game_logic.handle_vertical_collision(player_obj,
                                                 current_map_obj.tiles if hasattr(current_map_obj, 'tiles') else [],
                                                 player_obj.y_vel)

            # Check coin collection
            coin_points = game_logic.check_coin_collection(player_obj, coins)
            if coin_points > 0:
                current_score += coin_points

            # Rest of the collision checks...
            kills = game_logic.check_player_attack_on_enemies(player_obj, enemies_list)
            if kills > 0:
                current_score += kills * config.ENEMY_KILL_POINTS

            if game_logic.check_enemy_player_collision(player_obj, enemies_list):
                player_obj.take_damage()
                if player_obj.hearts <= 0:
                    score_at_end_of_level = current_score
                    score_store.score_store.update_high_score(score_at_end_of_level)
                    game_state = config.GAME_OVER_STATE
                    game_over_player_death_timer = config.GAME_OVER_ANIM_DELAY
                    target_final_score_anim = score_at_end_of_level
                    animated_display_score = 0  # Reset for animation
                    score_animation_phase = 1
                    # continue

            if game_logic.check_player_fall_off_map(player_obj, map_height):
                score_at_end_of_level = current_score
                score_store.score_store.update_high_score(score_at_end_of_level)
                game_state = config.GAME_OVER_STATE
                game_over_player_death_timer = config.GAME_OVER_ANIM_DELAY
                target_final_score_anim = score_at_end_of_level
                animated_display_score = 0
                score_animation_phase = 1
                # continue

            if game_logic.is_level_complete(player_obj, map_width):
                time_bonus_points = int(time_left_seconds * config.TIME_BONUS_MULTIPLIER)
                score_at_end_of_level = current_score  # Base score before bonus

                game_state = config.LEVEL_COMPLETE_STATE
                target_final_score_anim = score_at_end_of_level  # This is the base score target for animation
                target_final_bonus_anim = time_bonus_points

                animated_display_score = 0  # Base score animation starts from 0
                animated_display_bonus = 0  # Bonus animation starts after base score
                score_animation_phase = 1  # 1 = animating base score

            # Camera scrolling logic
            if player_obj:
                if ((player_obj.hitbox.right - camera_offset_x) >= (config.SCREEN_WIDTH - config.SCROLL_AREA_WIDTH) and
                        (player_obj.hitbox.right + config.SCROLL_AREA_WIDTH < map_width) and player_obj.x_vel > 0 or
                        (
                                player_obj.hitbox.left - camera_offset_x <= config.SCROLL_AREA_WIDTH < player_obj.hitbox.left) and player_obj.x_vel < 0):
                    new_offset_x = camera_offset_x + player_obj.x_vel
                    camera_offset_x = max(0, min(new_offset_x, map_width - config.SCREEN_WIDTH))

                if ((player_obj.rect.bottom - camera_offset_y) >= (
                        config.SCREEN_HEIGHT - config.SCROLL_AREA_HEIGHT) and player_obj.y_vel > 0 or
                        (player_obj.rect.top - camera_offset_y <= config.SCROLL_AREA_HEIGHT) and player_obj.y_vel < 0):
                    new_offset_y = camera_offset_y + player_obj.y_vel
                    max_offset_y = max(0, map_height - config.SCREEN_HEIGHT)  # Prevent scrolling beyond map bottom
                    camera_offset_y = max(0, min(new_offset_y, max_offset_y))  # Prevent scrolling above map top

        elif game_state == config.GAME_OVER_STATE:
            pygame.mixer.music.stop()
            music_playing = False

            if game_over_player_death_timer > 0:
                game_over_player_death_timer -= 1
                # Delay before showing the score screen
            else:  # Animation/delay done, now animate score
                if not game_over_sound_playing:
                    config.sound_game_over.play()
                    game_over_sound_playing = True
                if score_animation_phase == 1:  # Animating score
                    if animated_display_score < target_final_score_anim:
                        animated_display_score += score_increment_per_frame
                        if animated_display_score >= target_final_score_anim:
                            animated_display_score = target_final_score_anim
                            score_animation_phase = 0  # Animation done
                    else:  # Already at or beyond target
                        animated_display_score = target_final_score_anim
                        score_animation_phase = 0

        elif game_state == config.LEVEL_COMPLETE_STATE:
            if score_animation_phase and not score_sound_playing:
                config.sound_score_count.play(-1)
                score_sound_playing = True
            else:
                config.sound_score_count.stop()
                score_sound_playing = False
            pygame.mixer.music.stop()
            music_playing = False
            game_over_sound_playing = False

            if score_animation_phase == 1:  # Animating base score
                if animated_display_score < target_final_score_anim:
                    animated_display_score += score_increment_per_frame
                    if animated_display_score >= target_final_score_anim:
                        animated_display_score = target_final_score_anim
                        score_animation_phase = 2  # Base score done, start animating bonus
                else:  # Already at or beyond target
                    animated_display_score = target_final_score_anim
                    score_animation_phase = 2

            elif score_animation_phase == 2:  # Animating bonus
                if animated_display_bonus < target_final_bonus_anim:
                    # Animate bonus a bit slower or at least by 1
                    bonus_increment = int(
                        score_increment_per_frame * 0.75) if score_increment_per_frame * 0.75 >= 1 else 1
                    animated_display_bonus += bonus_increment
                    if animated_display_bonus >= target_final_bonus_anim:
                        animated_display_bonus = target_final_bonus_anim
                        score_animation_phase = 0  # Bonus animation done
                else:  # Already at or beyond target
                    animated_display_bonus = target_final_bonus_anim
                    score_animation_phase = 0

            score_store.score_store.update_high_score(animated_display_score + animated_display_bonus)

        # --- Drawing ---
        screen.fill(config.COLOR_BLACK)  # Default background, will be overdrawn

        if game_state == config.MENU_STATE:
            ui_manager.draw_menu(screen, selected_character_index, selected_map_index, selected_menu_item_index,
                                 asset_manager.get_character_preview_surface(),
                                 asset_manager.get_available_characters_list(),
                                 asset_manager.get_available_maps_list(),
                                 score_store.score_store.get_high_score())
        elif game_state == config.PLAYING_STATE:
            draw_game_scene(current_map_obj, player_obj, enemies_list, camera_offset_x, camera_offset_y,
                            map_width, current_score, time_left_seconds, coins)
        elif game_state == config.GAME_OVER_STATE:
            if game_over_player_death_timer > 0:  # Still show game scene during player death anim
                draw_game_scene(current_map_obj, player_obj, enemies_list, camera_offset_x, camera_offset_y,
                                map_width, score_at_end_of_level, time_left_seconds if time_left_seconds > 0 else 0, coins)
            else:
                ui_manager.draw_game_over_screen(screen, animated_display_score)
        elif game_state == config.LEVEL_COMPLETE_STATE:
            current_total_score_for_display = animated_display_score + animated_display_bonus
            ui_manager.draw_level_complete_screen(screen, animated_display_score, animated_display_bonus,
                                                  current_total_score_for_display)

        pygame.display.flip()

    score_store.score_store.save_high_score()
    pygame.quit()
    quit()


if __name__ == "__main__":
    main_loop()