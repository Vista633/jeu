import pygame
from enums import Direction, Element
from constants import WHITE

class Projectile:
    def __init__(self, x, y, direction, element, damage):
        self.x = x
        self.y = y
        self.direction = direction
        self.element = element
        self.damage = damage
        self.speed = 8
        self.size = 12
        self.lifetime = 100
        
        # Couleur selon l'élément
        if element == Element.FEU:
            self.color = (255, 100, 30)
        elif element == Element.EAU:
            self.color = (50, 150, 255)
        elif element == Element.TERRE:
            self.color = (139, 90, 43)
        elif element == Element.AIR:
            self.color = (200, 230, 255)
        else:
            self.color = (200, 200, 200)
    
    def update(self):
        if self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        
        self.lifetime -= 1
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), self.size, 2)
    
    def is_dead(self):
        return self.lifetime <= 0
