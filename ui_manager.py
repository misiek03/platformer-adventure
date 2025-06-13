import os
import pygame
import config

FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None
FONT_TIMER = None
FONT_SCORE_HUD = None
FONT_GAMEOVER_LARGE = None
FONT_GAMEOVER_MEDIUM = None
FONT_LEVELCOMPLETE_LARGE = None
FONT_LEVELCOMPLETE_MEDIUM = None

def init_fonts():
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TIMER, FONT_SCORE_HUD
    global FONT_GAMEOVER_LARGE, FONT_GAMEOVER_MEDIUM, FONT_LEVELCOMPLETE_LARGE, FONT_LEVELCOMPLETE_MEDIUM

    try:
        FONT_LARGE = pygame.font.Font(config.FONT_PATH, 60)
        FONT_MEDIUM = pygame.font.Font(config.FONT_PATH, 36)
        FONT_SMALL = pygame.font.Font(config.FONT_PATH, 28)
        FONT_TIMER = pygame.font.Font(config.FONT_PATH, 48)
        FONT_SCORE_HUD = pygame.font.Font(config.FONT_PATH, 36)
        FONT_GAMEOVER_LARGE = pygame.font.Font(config.FONT_PATH, 70)
        FONT_GAMEOVER_MEDIUM = pygame.font.Font(config.FONT_PATH, 42)
        FONT_LEVELCOMPLETE_LARGE = pygame.font.Font(config.FONT_PATH, 70)
        FONT_LEVELCOMPLETE_MEDIUM = pygame.font.Font(config.FONT_PATH, 42)
    except pygame.error as e:
        print(f"CRITICAL: Font '{config.FONT_PATH}' not loaded. Error: {e}.")


def draw_menu(screen, selected_char_idx, selected_map_idx, selected_menu_item_idx, char_preview_surf, available_chars,
              available_maps, high_score):
    screen.fill(config.COLOR_MENU_BG)

    title_text = FONT_LARGE.render("Platformer Adventure", True, config.COLOR_WHITE)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 280))
    screen.blit(title_text, title_rect)

    hs_surf = FONT_MEDIUM.render(f"High score: {high_score:06d}", True, config.COLOR_YELLOW)
    hs_rect = hs_surf.get_rect(center=(config.SCREEN_WIDTH // 2, title_rect.bottom + 40))
    screen.blit(hs_surf, hs_rect)

    if char_preview_surf:
        preview_rect = char_preview_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 150))
        screen.blit(char_preview_surf, preview_rect)

    current_char_name_display = "None"
    if available_chars and selected_char_idx < len(available_chars):
        current_char_name_display = available_chars[selected_char_idx]

    char_display_text = FONT_SMALL.render(f"{current_char_name_display}", True, (200, 200, 200))
    char_name_y_offset = (char_preview_surf.get_height() // 2 if char_preview_surf else 0) + 30
    char_display_rect = char_display_text.get_rect(
        center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 150 + char_name_y_offset))
    screen.blit(char_display_text, char_display_rect)

    map_display_name = "N/A"
    if available_maps and selected_map_idx < len(available_maps):
        map_display_name = available_maps[selected_map_idx]['name']

    menu_items_text = [
        "Start Game",
        f"Character: < {current_char_name_display} >",
        f"Map: < {map_display_name} >"
    ]

    start_y = config.SCREEN_HEIGHT // 2
    line_height = 60

    for i, item_text_val in enumerate(menu_items_text):
        color = config.COLOR_YELLOW if i == selected_menu_item_idx else config.COLOR_WHITE
        text_surf = FONT_MEDIUM.render(item_text_val, True, color)
        text_rect = text_surf.get_rect(center=(config.SCREEN_WIDTH // 2, start_y + i * line_height))
        screen.blit(text_surf, text_rect)

    instructions_text = FONT_SMALL.render("UP/DOWN: Navigate | ENTER: Select | LEFT/RIGHT: Change Option", True,
                                          (180, 180, 180))
    instructions_rect = instructions_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 60))
    screen.blit(instructions_text, instructions_rect)


def draw_game_over_screen(screen, current_score_to_display):
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(config.COLOR_OVERLAY_BG_DARK)
    screen.blit(overlay, (0, 0))

    game_over_text = FONT_GAMEOVER_LARGE.render("GAME OVER", True, (200, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 120))
    screen.blit(game_over_text, game_over_rect)

    score_text_surf = FONT_GAMEOVER_MEDIUM.render(f"Score: {current_score_to_display:06d}", True, (220, 220, 220))
    score_rect = score_text_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 20))
    screen.blit(score_text_surf, score_rect)

    restart_text_surf = FONT_GAMEOVER_MEDIUM.render("Press ENTER to Return to Menu", True, config.COLOR_WHITE)
    restart_rect = restart_text_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 80))
    screen.blit(restart_text_surf, restart_rect)


def draw_level_complete_screen(screen, base_score_val, bonus_val, total_score_val):
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(config.COLOR_OVERLAY_BG_PURPLEISH)
    screen.blit(overlay, (0, 0))

    complete_text = FONT_LEVELCOMPLETE_LARGE.render("LEVEL COMPLETE!", True, (0, 200, 0))
    complete_rect = complete_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 180))
    screen.blit(complete_text, complete_rect)

    base_score_surf = FONT_LEVELCOMPLETE_MEDIUM.render(f"Base Score: {base_score_val:06d}", True, (220, 220, 220))
    base_score_rect = base_score_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 80))
    screen.blit(base_score_surf, base_score_rect)

    bonus_surf = FONT_LEVELCOMPLETE_MEDIUM.render(f"Time Bonus: +{bonus_val:06d}", True, config.COLOR_YELLOW)
    bonus_rect = bonus_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 20))
    screen.blit(bonus_surf, bonus_rect)

    total_score_surf = FONT_LEVELCOMPLETE_MEDIUM.render(f"Total Score: {total_score_val:06d}", True, config.COLOR_WHITE)
    total_score_rect = total_score_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 40))
    screen.blit(total_score_surf, total_score_rect)

    restart_text_surf = FONT_LEVELCOMPLETE_MEDIUM.render("Press ENTER to Return to Menu", True, config.COLOR_WHITE)
    restart_rect = restart_text_surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 140))
    screen.blit(restart_text_surf, restart_rect)


def draw_hearts(screen, hearts_count):
    heart_size = 48
    try:
        heart_surf = pygame.image.load(os.path.join(config.UI_ASSETS_PATH, 'heart.png')).convert_alpha()
        heart_gray_surf = pygame.image.load(os.path.join(config.UI_ASSETS_PATH, 'heart_gray.png')).convert_alpha()
    except pygame.error as e:
        print(f"Error loading heart images: {e}")
        return

    for i in range(3):  # Max 3 hearts
        x_pos = 20 + (i * (heart_size + 10))
        y_pos = 20
        if i < hearts_count:
            screen.blit(heart_surf, (x_pos + heart_size // 4, y_pos + heart_size // 3))
        else:
            screen.blit(heart_gray_surf, (x_pos + heart_size // 4, y_pos + heart_size // 3))


def draw_timer(screen, time_left_seconds):
    minutes = int(time_left_seconds) // 60
    seconds = int(time_left_seconds) % 60
    time_text = f"{minutes:02d}:{seconds:02d}"
    timer_surface = FONT_TIMER.render(time_text, True, config.COLOR_WHITE)
    timer_rect = timer_surface.get_rect(topleft=(42, 80))
    screen.blit(timer_surface, timer_rect)


def draw_score_hud(screen, current_score):
    score_text = f"SCORE: {current_score:05d}"
    score_surface = FONT_SCORE_HUD.render(score_text, True, config.COLOR_WHITE)
    score_rect = score_surface.get_rect(midbottom=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 20))
    screen.blit(score_surface, score_rect)
