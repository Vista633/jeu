import random
import pygame
from constants import BLACK

class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = 60
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = (self.velocity[0] * 0.95, self.velocity[1] + 0.2)  # Gravité
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)
    
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / 60))
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)))
            s.set_alpha(alpha)
            s.set_colorkey(BLACK)
            pygame.draw.circle(s, self.color, (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))
