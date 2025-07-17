# movement_patterns.py
import pygame
import random
import math
import colors

class MovingPoint:
    def __init__(self, x, y, color, speed, screen_width, screen_height):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = 5

        # For random movement
        self.d_ang = math.radians(random.uniform(0, 360))
        self.move_duration_frames = 30
        self.current_frame_count = 0

        # For linear movements
        self.direction_x = 0  # -1 for left, 1 for right, 0 for none
        self.direction_y = 0  # -1 for up, 1 for down, 0 for none

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def update_random(self):
        if self.current_frame_count <= 0:
            self.d_ang = math.radians(random.uniform(0, 360))
            self.current_frame_count = self.move_duration_frames

        self.x += self.speed * math.cos(self.d_ang)
        self.y += self.speed * math.sin(self.d_ang)

        # Boundary collision for random movement
        if self.x < 0:
            self.x = 0
            self.d_ang = math.radians(180) - self.d_ang
        elif self.x > self.screen_width-500:
            self.x = self.screen_width-500
            self.d_ang = math.radians(180) - self.d_ang

        if self.y < 300:
            self.y = 300
            self.d_ang = math.radians(360) - self.d_ang
        elif self.y > self.screen_height:
            self.y = self.screen_height
            self.d_ang = math.radians(360) - self.d_ang
        
        self.current_frame_count -= 1

    def update_up_to_down(self):
        self.y += self.speed
        if self.y > self.screen_height:
            self.y = 300  # Reset to top

    def update_down_to_up(self):
        self.y -= self.speed
        if self.y < 300:
            self.y = self.screen_height  # Reset to bottom

    def update_right_to_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = self.screen_width-500  # Reset to right

    def update_left_to_right(self):
        self.x += self.speed
        if self.x > self.screen_width-500:
            self.x = 0  # Reset to left