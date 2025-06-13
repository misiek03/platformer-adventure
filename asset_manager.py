import pygame
import os
import config

# --- Asset Storage ---
AVAILABLE_CHARACTERS = []
AVAILABLE_MAPS_CONFIG = []
character_preview_surf = None
game_background_surf = None


def load_game_assets():
    global game_background_surf
    _load_available_characters()
    _load_map_configurations()
    _load_character_preview()


def load_background_for_map(bg_filename, bg_scale):
    global game_background_surf

    full_path = os.path.join(config.BACKGROUND_PATH, bg_filename)
    try:
        orig = pygame.image.load(full_path).convert_alpha()
        game_background_surf = pygame.transform.scale_by(orig, bg_scale)
    except pygame.error as e:
        print(f"Error loading background '{full_path}': {e}")
        game_background_surf = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        game_background_surf.fill((100, 100, 100))


def _load_available_characters():
    global AVAILABLE_CHARACTERS
    AVAILABLE_CHARACTERS = []
    if os.path.exists(config.PLAYER_ASSETS_PATH):
        AVAILABLE_CHARACTERS = [
            d for d in os.listdir(config.PLAYER_ASSETS_PATH)
            if os.path.isdir(os.path.join(config.PLAYER_ASSETS_PATH, d))
        ]

    if not AVAILABLE_CHARACTERS:
        AVAILABLE_CHARACTERS = [config.DEFAULT_CHARACTER]


def _load_map_configurations():
    global AVAILABLE_MAPS_CONFIG

    AVAILABLE_MAPS_CONFIG = [
        {"csv": "Map4.csv", "tileset": "Swamp", "name": "Swamp Challenge", "bg_filename": "Swamp.png", "bg_scale": 3},
        {"csv": "Map2.csv", "tileset": "Desert", "name": "Desert Dunes", "bg_filename": "Desert.png", "bg_scale": 1},
    ]


def _load_character_preview(character_name=None):
    global character_preview_surf
    if not AVAILABLE_CHARACTERS:
        character_preview_surf = None
        print("Cannot load character preview: No characters available.")
        return

    char_to_load = character_name
    if char_to_load is None:
        char_to_load = AVAILABLE_CHARACTERS[0]

    if char_to_load not in AVAILABLE_CHARACTERS:
        char_to_load = AVAILABLE_CHARACTERS[0]

    img_path = os.path.join(config.PLAYER_ASSETS_PATH, char_to_load, f"{char_to_load}.png")

    if os.path.exists(img_path):
        original_image = pygame.image.load(img_path).convert_alpha()
        preview_width = 96
        aspect_ratio = original_image.get_width() / original_image.get_height()
        preview_height = int(preview_width / aspect_ratio) if aspect_ratio > 0 else preview_width
        character_preview_surf = pygame.transform.scale(original_image, (preview_width, preview_height))
    else:
        character_preview_surf = None
        print(f"Warning: Character preview image not found: {img_path}")


def get_character_preview_surface():
    return character_preview_surf


def get_available_characters_list():
    return AVAILABLE_CHARACTERS


def get_available_maps_list():
    return AVAILABLE_MAPS_CONFIG


def get_game_background():
    return game_background_surf


def update_character_preview(character_name):
    _load_character_preview(character_name)