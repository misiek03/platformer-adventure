import random
import pygame

import config
from Character import Character
from config import sound_attack


class Player(Character):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    ANIMATION_DELAY = 6

    def __init__(self, x, y, w, h, character_name):
        super().__init__(x, y, w, h, "Player", character_name)
        self.jump_count = 0
        self.rect = self.sprite.get_rect(midtop=(x - 56, y - 56))
        self.hitbox = self.sprite.get_rect(center=(x, y - 15))
        old_center = self.rect.center
        self.rect = self.sprite.get_rect(center=old_center)
        self.mask = pygame.mask.from_surface(self.sprite)

        # Hearts system
        self.hearts = 3
        self.max_hearts = 3

        # Hurt state
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 60  # 1 second at 60 FPS
        self.invincibility_timer = 0
        self.invincibility_duration = 90  # 1.5 seconds of invincibility after being hurt

        # Knockback system
        self.knockback_vel = 0
        self.knockback_timer = 0

        # Attack system
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 40
        self.attack_hitbox = None
        self.attack_range = 50  # How far the attack reaches
        self.attack_height = h  # Height of attack hitbox (same as player height)
        self.attack_active_start = 8  # Frame when attack becomes active
        self.attack_active_end = 25  # Frame when attack stops being active
        self.attack_rand = 1  # Random number 1-3, to choose attack animation

    def jump(self):
        if self.knockback_timer > 5 or self.is_attacking:
            return
        self.y_vel = -self.GRAVITY * 12
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def attack(self):
        if self.is_attacking or self.is_hurt or self.knockback_timer > 0:
            return False

        sound_attack.play()
        self.is_attacking = True
        self.attack_timer = self.attack_duration
        self.animation_count = 0
        self.attack_rand = random.randint(1, 3)
        return True

    def update_attack_hitbox(self):
        # Only create hitbox during active attack frames
        if not self.is_attacking or self.attack_timer > (
                self.attack_duration - self.attack_active_start) or self.attack_timer < (
                self.attack_duration - self.attack_active_end):
            self.attack_hitbox = None
            return

        # Position attack hitbox in front of player
        if self.direction == "right":
            attack_x = self.hitbox.right
        else:
            attack_x = self.hitbox.left - self.attack_range

        attack_y = self.hitbox.centery - (self.attack_height // 2)

        self.attack_hitbox = pygame.Rect(attack_x, attack_y, self.attack_range, self.attack_height)

    def landed(self):
        self.fall_count = 0
        self.jump_count = 0
        self.y_vel = 0

    def hit_head(self):
        self.y_vel *= -0.5

    def move(self, dx, dy):
        super().move(dx, dy)
        self.hitbox.x += dx
        self.hitbox.y += dy

    def move_left(self, vel):
        # Don't allow movement during hurt animation, early invincibility, or attack
        if self.knockback_timer > 0 or self.is_attacking:
            return

        super().move_left(vel)

    def move_right(self, vel):
        # Don't allow movement during hurt animation, early invincibility, or attack
        if self.knockback_timer > 0 or self.is_attacking:
            return

        super().move_right(vel)

    def take_damage(self):
        if self.invincibility_timer > 0:  # Player is invincible
            return

        config.sound_player_hurt.play()

        self.hearts -= 1
        self.is_hurt = True
        self.hurt_timer = self.hurt_duration
        self.invincibility_timer = self.invincibility_duration
        self.animation_count = 0

        # Cancel attack if player gets hurt
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_hitbox = None

        # Add knockback effect - stronger and more persistent
        knockback_force = 12
        if self.direction == "right":
            self.knockback_vel = -knockback_force
        else:
            self.knockback_vel = knockback_force

        self.knockback_timer = 30  # Knockback lasts for 0.5 seconds

    def loop(self, fps):
        # Handle attack timer
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_hitbox = None
            else:
                self.update_attack_hitbox()

        # Handle hurt state timer
        if self.is_hurt:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.is_hurt = False

        # Handle invincibility timer
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Handle knockback timer
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            # Apply knockback velocity
            self.x_vel = self.knockback_vel
            # Reduce knockback over time
            self.knockback_vel *= 0.85
        elif not (self.is_hurt or self.invincibility_timer > 60 or self.is_attacking):
            # Only reset x_vel if not in hurt state, early invincibility, or attacking
            pass

        # Don't move horizontally during attack
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        if self.y_vel > 15:
            self.y_vel = 15

        # Apply movement (restrict horizontal movement during attack)
        if self.is_attacking:
            self.move(0, self.y_vel)  # Only vertical movement during attack
        else:
            self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self, sprite_sheet="idle"):
        # Prioritize attack animation
        if self.is_attacking:
            sprite_sheet = f"attack{self.attack_rand}"
        # Then hurt animation
        elif self.is_hurt:
            sprite_sheet = "hurt"
        elif self.y_vel < 0:
            if self.jump_count > 0:
                sprite_sheet = "jump"
        elif any(pygame.key.get_pressed()[k] for k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d)):
            sprite_sheet = "run"

        if self.hearts <= 0:
            sprite_sheet = "idle"
        
        super().update_sprite(sprite_sheet)
        self.update()

    def update(self):
        super().update()
        self.rect = self.sprite.get_rect(center=self.rect.center)
        self.update_hitbox()

    def update_hitbox(self):
        bounds = self.mask.get_bounding_rects()[0]

        global_x = self.rect.x + bounds.x
        global_y = self.rect.y + bounds.y

        hit = pygame.Rect(0, 0, self.width, self.height)
        hit.midbottom = (global_x + bounds.width // 2, global_y + bounds.height)
        self.hitbox = hit

    def draw(self, screen, offset_x, offset_y):
        # Flicker effect during invincibility
        if self.invincibility_timer > 0 and self.invincibility_timer % 8 < 4 and self.hearts > 0:
            # Don't draw the player (flicker effect)
            pass
        else:
            screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

        # Draw hitbox for debugging
        # pygame.draw.rect(screen, (255, 0, 0),
        #                  (self.hitbox.x - offset_x, self.hitbox.y - offset_y, self.hitbox.width, self.hitbox.height), 2)
        #
        # # Draw attack hitbox for debugging
        # if self.attack_hitbox:
        #     pygame.draw.rect(screen, (255, 255, 0),
        #                      (self.attack_hitbox.x - offset_x, self.attack_hitbox.y - offset_y,
        #                       self.attack_hitbox.width, self.attack_hitbox.height), 2)