import random
import pygame
from enums import Element
from enemy import Enemy

class Kingdom:
    def __init__(self, name, element, bg_color, bg_image_path=None):
        self.name = name
        self.element = element
        self.bg_color = bg_color
        self.completed = False
        self.obstacles = []
        self.enemies = []
        
        # Load background image
        self.bg_image = None
        if bg_image_path:
            try:
                self.bg_image = pygame.image.load(bg_image_path).convert()
                # Scale to screen size (assuming 1366x768)
                self.bg_image = pygame.transform.scale(self.bg_image, (1366, 768))
            except:
                print(f"Warning: Could not load background image {bg_image_path}")
                self.bg_image = None
        
        self.generate_world()
    
    def generate_world(self):
        # No obstacles in platform mode
        self.obstacles = []
        
        # Générer des ennemis
        enemy_count = 5 if self.element != Element.NONE else 3
        for _ in range(enemy_count):
            x = random.randint(500, 1500)
            y = random.randint(300, 1200)
            enemy_type = random.choice(["mini", "normal"])
            self.enemies.append(Enemy(x, y, enemy_type, self.element))
        
        # Boss à la fin
        if self.element != Element.NONE:
            boss_x = 1700
            boss_y = 700
            self.enemies.append(Enemy(boss_x, boss_y, "boss", self.element))
