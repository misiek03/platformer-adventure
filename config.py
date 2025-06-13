# Screen dimensions and FPS
import pygame.mixer

pygame.mixer.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FPS = 60
BACKGROUND_SCALE = 3

# Player settings
PLAYER_VEL = 5

# Game States
MENU_STATE = 0
PLAYING_STATE = 1
GAME_OVER_STATE = 2
LEVEL_COMPLETE_STATE = 3

# Score and Timer constants
INITIAL_TIME = 100  # Seconds per level
ENEMY_KILL_POINTS = 125
COIN_POINTS = 75
TIME_BONUS_MULTIPLIER = 10  # Points per second remaining

# Paths
FONT_PATH = 'assets/Font/PixelifySans-SemiBold.ttf'
BACKGROUND_PATH = 'assets/Background'
PLAYER_ASSETS_PATH = 'assets/Player'
MAP_ASSETS_PATH = 'assets/maps'
TILE_ASSETS_PATH = 'assets/Tile'
UI_ASSETS_PATH = 'assets/UI'
OTHER_ASSETS_PATH = 'assets/Other'

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_MENU_BG = (20, 20, 40)
COLOR_OVERLAY_BG_DARK = (0,0,0)
COLOR_OVERLAY_BG_PURPLEISH = (10,0,10)

# Scroll area for camera
SCROLL_AREA_WIDTH = 350
SCROLL_AREA_HEIGHT = 200

# Game Over delay
GAME_OVER_ANIM_DELAY = 30

# Score animation speed
# Points Per Second, scaled by delta time in main loop
SCORE_ANIMATION_SPEED_PPS = 1000

# Music and sounds
pygame.mixer.music.load("sounds/music_bg.mp3")
pygame.mixer.music.set_volume(0.3)
sound_pickup_coin = pygame.mixer.Sound("sounds/pickup_coin.wav")
sound_attack = pygame.mixer.Sound("sounds/attack.wav")
sound_attack.set_volume(0.4)
sound_game_over = pygame.mixer.Sound("sounds/game_over.wav")
sound_score_count = pygame.mixer.Sound("sounds/score_count.wav")
sound_player_hurt = pygame.mixer.Sound("sounds/player_hurt.wav")
