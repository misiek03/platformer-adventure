import pygame
from utils import load_sprite_sheets
from Character import Character


class Enemy(Character):
    ANIMATION_DELAY = 8

    def __init__(self, x, y, width, height, character, speed):
        super().__init__(x, y, width, height, "Enemy", character)
        self.rect.topleft = (x, y)

        # Movement properties
        self.base_speed = speed
        self.current_speed = self.base_speed
        self.fall_count = 0

        # Health and damage system
        self.is_alive = True
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 15
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 30
        self.can_damage_player = True

    def take_damage(self):
        if not self.is_alive or self.is_hurt or self.is_dying:
            return False

        self.is_hurt = True
        self.hurt_timer = self.hurt_duration
        self.animation_count = 0
        self.can_damage_player = False

        # Stop movement during hurt
        self.x_vel = 0

        return True

    def die(self):
        if self.is_dying:
            return

        self.is_dying = True
        self.death_timer = self.death_duration
        self.animation_count = 0
        self.can_damage_player = False
        self.x_vel = 0
        self.y_vel = 0

    def check_wall_collision(self, tiles, dx):
        # Create a temporary rect to test collision
        test_rect = self.rect.copy()
        test_rect.x += dx

        for tile in tiles:
            if test_rect.colliderect(tile.rect):
                return True
        return False

    def check_edge(self, tiles):
        # Check a point slightly ahead and below the enemy
        check_distance = 32  # Distance ahead to check
        check_x = self.rect.centerx + (check_distance if self.direction == "right" else -check_distance)
        check_y = self.rect.bottom + 10  # Slightly below the enemy's feet

        # Create a small rect to check for ground
        check_rect = pygame.Rect(check_x - 5, check_y, 10, 10)

        # Check if there's any tile at this position (ground to stand on)
        for tile in tiles:
            if check_rect.colliderect(tile.rect):
                return False  # There is ground, not an edge

        return True  # No ground found, this is an edge

    def change_direction(self):
        if self.direction == "left":
            self.direction = "right"
            self.current_speed = self.base_speed
        else:
            self.direction = "left"
            self.current_speed = -self.base_speed
        self.animation_count = 0

    def apply_gravity(self, tiles):
        # Don't apply gravity if dying
        if self.is_dying:
            return

        # Simple gravity implementation
        self.y_vel += min(1, (self.fall_count / 60) * self.GRAVITY)
        if self.y_vel > 15:
            self.y_vel = 15

        # Move vertically and check for collision
        self.move(0, self.y_vel)

        # Check for ground collision
        landed = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.y_vel > 0:  # Falling down
                    self.rect.bottom = tile.rect.top
                    self.y_vel = 0
                    self.fall_count = 0
                    landed = True
                    break

        if not landed:
            self.fall_count += 1

    def update_movement(self, tiles):
        # Don't move if hurt, dying, or dead
        if self.is_hurt or self.is_dying or not self.is_alive:
            return

        # Determine movement direction and speed
        if self.direction == "right":
            next_x_vel = self.base_speed
        else:
            next_x_vel = -self.base_speed

        # Check for wall collision
        if self.check_wall_collision(tiles, next_x_vel * 2):
            self.change_direction()
            next_x_vel = -next_x_vel

        # Check for edge
        elif self.check_edge(tiles):
            self.change_direction()
            next_x_vel = -next_x_vel

        # Apply horizontal movement
        self.x_vel = next_x_vel
        self.move(self.x_vel, 0)

        self.apply_gravity(tiles)

    def loop(self, tiles=None):
        # Handle hurt state
        if self.is_hurt:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.is_hurt = False
                # Start death sequence after hurt animation
                self.die()

        # Handle death state
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.is_alive = False
                # Enemy is now completely dead and should be removed

        # Only update movement if alive and not in special states
        if self.is_alive and not self.is_hurt and not self.is_dying:
            if tiles is not None:
                self.update_movement(tiles)
            else:
                # Fallback to simple movement if no tiles provided
                self.move(self.x_vel, self.y_vel)
        elif self.is_alive:  # Still alive but hurt/dying, apply gravity only
            if tiles is not None:
                self.apply_gravity(tiles)

        self.update_sprite()

    def update_sprite(self, sprite_sheet="walk"):
        if self.is_dying:
            sprite_sheet = "death"
        elif self.is_hurt:
            sprite_sheet = "hurt"
        elif self.x_vel == 0:
            sprite_sheet = "idle"
        else:
            sprite_sheet = "walk"

        super().update_sprite(sprite_sheet)
        self.update()

    def draw(self, screen, offset_x, offset_y):
        # Don't draw if completely dead
        if not self.is_alive:
            return

        # Flicker effect when hurt
        if self.is_hurt and self.hurt_timer % 4 < 2:
            # Don't draw (flicker effect)
            pass
        else:
            screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

        # Draw enemy hitbox for debugging
        # if self.is_alive:
        #     color = (255, 0, 0) if self.can_damage_player else (128, 128, 128)
        #     pygame.draw.rect(screen, color,
        #                      (self.rect.x - offset_x, self.rect.y - offset_y, self.rect.width, self.rect.height), 2)