import pygame
import sys
import random
import math
from enum import Enum

# Initialisation de Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 50)
GRAY = (100, 100, 100)
DARK_GREEN = (20, 80, 20)
LIGHT_BLUE = (150, 200, 255)
ORANGE = (255, 150, 50)
BROWN = (139, 90, 43)

class GameState(Enum):
    MENU = 1
    GAME = 2
    DIALOGUE = 3
    VICTORY = 4
    GAME_OVER = 5

class Element(Enum):
    NONE = 0
    EAU = 1
    TERRE = 2
    AIR = 3
    FEU = 4

class Direction(Enum):
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3

# Classe pour les particules d'effet
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

# Classe bouton
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 40)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

# Classe projectile
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

# Classe joueur Avatar
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50
        self.speed = 4
        self.direction = Direction.DOWN
        
        # Stats
        self.max_hp = 100
        self.hp = 100
        self.attack = 15
        self.defense = 5
        self.elements = {Element.NONE}
        
        # Animation
        self.animation_frame = 0
        self.animation_counter = 0
        self.is_moving = False
        
        # Combat
        self.attack_cooldown = 0
        self.invincible_frames = 0
        
        # Couleurs pour le dessin
        self.body_color = (100, 150, 255)
        self.head_color = (255, 220, 180)
    
    def unlock_element(self, element):
        self.elements.add(element)
        if element == Element.EAU:
            self.max_hp += 20
            self.hp = min(self.hp + 20, self.max_hp)
        elif element == Element.TERRE:
            self.defense += 5
        elif element == Element.FEU:
            self.attack += 10
        elif element == Element.AIR:
            self.speed += 1
    
    def move(self, dx, dy, obstacles):
        # Sauvegarder la position actuelle
        old_x, old_y = self.x, self.y
        
        # Calculer la nouvelle position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Créer un rectangle pour la collision
        player_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        
        # Vérifier les collisions avec les obstacles
        can_move = True
        for obstacle in obstacles:
            if player_rect.colliderect(obstacle):
                can_move = False
                break
        
        # Vérifier les limites du monde
        if new_x < 0 or new_x + self.width > 2000:
            can_move = False
        if new_y < 0 or new_y + self.height > 1500:
            can_move = False
        
        # Appliquer le mouvement si possible
        if can_move:
            self.x = new_x
            self.y = new_y
            self.is_moving = True
        else:
            self.is_moving = False
    
    def update(self, keys, obstacles):
        dx, dy = 0, 0
        
        # Détection des touches
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx = -self.speed
            self.direction = Direction.LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.direction = Direction.RIGHT
        
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            dy = -self.speed
            self.direction = Direction.UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.direction = Direction.DOWN
        
        # Mouvement
        if dx != 0 or dy != 0:
            self.move(dx, dy, obstacles)
        else:
            self.is_moving = False
        
        # Animation
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= 10:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_counter = 0
        else:
            self.animation_frame = 0
        
        # Cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
    
    def shoot(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 30
            
            # Position du projectile
            proj_x = self.x + self.width // 2
            proj_y = self.y + self.height // 2
            
            # Élément à utiliser (prendre le plus puissant)
            element = Element.NONE
            if Element.FEU in self.elements:
                element = Element.FEU
            elif Element.AIR in self.elements:
                element = Element.AIR
            elif Element.TERRE in self.elements:
                element = Element.TERRE
            elif Element.EAU in self.elements:
                element = Element.EAU
            
            return Projectile(proj_x, proj_y, self.direction, element, self.attack)
        return None
    
    def take_damage(self, damage):
        if self.invincible_frames <= 0:
            actual_damage = max(1, damage - self.defense)
            self.hp -= actual_damage
            self.invincible_frames = 60
            return actual_damage
        return 0
    
    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Effet de clignotement si invincible
        if self.invincible_frames > 0 and self.invincible_frames % 10 < 5:
            return
        
        # Décalage d'animation de marche
        walk_offset = 0
        if self.is_moving:
            walk_offset = math.sin(self.animation_frame * math.pi / 2) * 3
        
        # Corps
        body_rect = pygame.Rect(screen_x + 10, screen_y + 20, 20, 25)
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 2)
        
        # Tête
        pygame.draw.circle(screen, self.head_color, 
                         (screen_x + 20, int(screen_y + 15 + walk_offset)), 12)
        pygame.draw.circle(screen, BLACK, 
                         (screen_x + 20, int(screen_y + 15 + walk_offset)), 12, 2)
        
        # Yeux
        eye_y = int(screen_y + 13 + walk_offset)
        pygame.draw.circle(screen, BLACK, (screen_x + 16, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (screen_x + 24, eye_y), 2)
        
        # Bras
        if self.direction == Direction.RIGHT:
            pygame.draw.line(screen, self.head_color, 
                           (screen_x + 30, screen_y + 30), 
                           (screen_x + 38, screen_y + 35), 4)
        elif self.direction == Direction.LEFT:
            pygame.draw.line(screen, self.head_color,
                           (screen_x + 10, screen_y + 30),
                           (screen_x + 2, screen_y + 35), 4)
        else:
            pygame.draw.line(screen, self.head_color,
                           (screen_x + 10, screen_y + 30),
                           (screen_x + 5, screen_y + 38), 4)
            pygame.draw.line(screen, self.head_color,
                           (screen_x + 30, screen_y + 30),
                           (screen_x + 35, screen_y + 38), 4)
        
        # Jambes
        leg_offset = int(walk_offset * 2)
        pygame.draw.line(screen, BLUE,
                       (screen_x + 15, screen_y + 45),
                       (screen_x + 13, screen_y + 60 + leg_offset), 4)
        pygame.draw.line(screen, BLUE,
                       (screen_x + 25, screen_y + 45),
                       (screen_x + 27, screen_y + 60 - leg_offset), 4)
        
        # Indicateur d'élément actif
        if len(self.elements) > 1:
            element = None
            if Element.FEU in self.elements:
                element_color = (255, 100, 30)
            elif Element.AIR in self.elements:
                element_color = (200, 230, 255)
            elif Element.TERRE in self.elements:
                element_color = (139, 90, 43)
            elif Element.EAU in self.elements:
                element_color = (50, 150, 255)
            
            if 'element_color' in locals():
                pygame.draw.circle(screen, element_color, 
                                 (screen_x + 35, screen_y + 10), 5)

# Classe ennemi
class Enemy:
    def __init__(self, x, y, enemy_type, element):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 40
        self.enemy_type = enemy_type
        self.element = element
        
        # Stats selon le type
        if enemy_type == "mini":
            self.max_hp = 30
            self.hp = 30
            self.attack = 8
            self.speed = 2
            self.size = 30
        elif enemy_type == "normal":
            self.max_hp = 50
            self.hp = 50
            self.attack = 12
            self.speed = 1.5
            self.size = 35
        else:  # boss
            self.max_hp = 100
            self.hp = 100
            self.attack = 20
            self.speed = 1
            self.size = 50
        
        # Couleur selon l'élément
        if element == Element.FEU:
            self.color = (255, 100, 50)
        elif element == Element.EAU:
            self.color = (50, 150, 255)
        elif element == Element.TERRE:
            self.color = (139, 90, 43)
        elif element == Element.AIR:
            self.color = (200, 230, 255)
        else:
            self.color = (80, 50, 100)
        
        # IA
        self.direction = random.choice([0, 1, 2, 3])
        self.move_timer = 0
        self.attack_cooldown = 0
        self.aggro_range = 300
    
    def update(self, player_x, player_y, obstacles):
        # Calculer la distance au joueur
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Si le joueur est proche, le suivre
        if distance < self.aggro_range:
            # Normaliser la direction
            if distance > 0:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                
                # Essayer de bouger
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # Vérifier les collisions
                enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
                can_move = True
                
                for obstacle in obstacles:
                    if enemy_rect.colliderect(obstacle):
                        can_move = False
                        break
                
                if can_move:
                    self.x = new_x
                    self.y = new_y
        else:
            # Mouvement aléatoire
            self.move_timer += 1
            if self.move_timer >= 60:
                self.direction = random.choice([0, 1, 2, 3])
                self.move_timer = 0
            
            move_x, move_y = 0, 0
            if self.direction == 0:  # Haut
                move_y = -self.speed
            elif self.direction == 1:  # Bas
                move_y = self.speed
            elif self.direction == 2:  # Gauche
                move_x = -self.speed
            elif self.direction == 3:  # Droite
                move_x = self.speed
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            # Vérifier les limites
            if 0 < new_x < 2000 - self.width and 0 < new_y < 1500 - self.height:
                enemy_rect = pygame.Rect(new_x, new_y, self.width, self.height)
                can_move = True
                
                for obstacle in obstacles:
                    if enemy_rect.colliderect(obstacle):
                        can_move = False
                        break
                
                if can_move:
                    self.x = new_x
                    self.y = new_y
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Corps de l'ennemi
        pygame.draw.circle(screen, self.color, 
                         (screen_x + self.width // 2, screen_y + self.height // 2), 
                         self.size // 2)
        pygame.draw.circle(screen, BLACK,
                         (screen_x + self.width // 2, screen_y + self.height // 2),
                         self.size // 2, 2)
        
        # Yeux méchants
        eye_y = screen_y + self.height // 2 - 5
        pygame.draw.circle(screen, RED, (screen_x + self.width // 2 - 8, eye_y), 4)
        pygame.draw.circle(screen, RED, (screen_x + self.width // 2 + 8, eye_y), 4)
        
        # Barre de vie
        hp_bar_width = self.size
        hp_bar_height = 5
        hp_percentage = self.hp / self.max_hp
        
        pygame.draw.rect(screen, RED,
                       (screen_x, screen_y - 10, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, GREEN,
                       (screen_x, screen_y - 10, int(hp_bar_width * hp_percentage), hp_bar_height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def take_damage(self, damage):
        self.hp -= damage
        return self.hp <= 0

# Classe royaume/niveau
class Kingdom:
    def __init__(self, name, element, bg_color):
        self.name = name
        self.element = element
        self.bg_color = bg_color
        self.completed = False
        self.obstacles = []
        self.enemies = []
        self.generate_world()
    
    def generate_world(self):
        # Générer des obstacles (arbres, rochers, etc.)
        for _ in range(20):
            x = random.randint(100, 1800)
            y = random.randint(100, 1300)
            width = random.randint(40, 80)
            height = random.randint(40, 80)
            self.obstacles.append(pygame.Rect(x, y, width, height))
        
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

# Classe principale du jeu
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Avatar : L'Équilibre Perdu")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        
        # Polices
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 50)
        self.text_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        
        # Animation du menu
        self.menu_animation_offset = 0
        
        # Jeu
        self.player = None
        self.camera_x = 0
        self.camera_y = 0
        self.particles = []
        self.projectiles = []
        
        # Royaumes
        self.kingdoms = [
            Kingdom("Royaume de l'Eau", Element.EAU, (50, 100, 150)),
            Kingdom("Royaume de la Terre", Element.TERRE, (100, 70, 40)),
            Kingdom("Royaume de l'Air", Element.AIR, (135, 206, 235)),
            Kingdom("Royaume du Feu", Element.FEU, (139, 50, 30))
        ]
        self.current_kingdom_index = 0
        self.current_kingdom = None
        
        # Dialogue
        self.dialogue_text = ""
        self.dialogue_timer = 0
    
    def start_game(self):
        self.player = Player(100, 100)
        self.current_kingdom = self.kingdoms[self.current_kingdom_index]
        self.camera_x = 0
        self.camera_y = 0
        self.projectiles = []
        self.particles = []
        self.state = GameState.GAME
        self.show_dialogue(f"Bienvenue dans le {self.current_kingdom.name}...")
    
    def show_dialogue(self, text):
        self.dialogue_text = text
        self.dialogue_timer = 180
    
    def update_camera(self):
        # Centrer la caméra sur le joueur
        target_x = self.player.x - SCREEN_WIDTH // 2 + self.player.width // 2
        target_y = self.player.y - SCREEN_HEIGHT // 2 + self.player.height // 2
        
        # Limiter la caméra aux bords du monde
        target_x = max(0, min(target_x, 2000 - SCREEN_WIDTH))
        target_y = max(0, min(target_y, 1500 - SCREEN_HEIGHT))
        
        # Mouvement fluide de la caméra
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
    
    def create_particles(self, x, y, color, count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(x, y, color, velocity))
    
    def draw_menu(self):
        # Fond animé style jungle
        self.menu_animation_offset = (self.menu_animation_offset + 1) % 360
        
        # Dégradé de fond
        for y in range(0, SCREEN_HEIGHT, 5):
            color_value = int(20 + 40 * math.sin((y + self.menu_animation_offset) / 100))
            color_r = max(0, min(255, color_value))
            color_g = max(0, min(255, 50 + color_value))
            color_b = max(0, min(255, color_value))
            color = (color_r, color_g, color_b)
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, 5))
        
        # Feuilles décoratives animées
        for i in range(10):
            offset = math.sin((self.menu_animation_offset + i * 36) / 30) * 20
            x = 100 + i * 120
            y = 50 + offset
            pygame.draw.circle(self.screen, (34, 139, 34), (int(x), int(y)), 30)
            pygame.draw.circle(self.screen, (50, 180, 50), (int(x), int(y)), 25)
        
        # Titre
        title_text = self.title_font.render("AVATAR", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Ombre du titre
        shadow_text = self.title_font.render("AVATAR", True, (139, 69, 19))
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 5, 155))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Sous-titre
        subtitle_text = self.subtitle_font.render("Héritier des 4 Mondes", True, (255, 250, 205))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Boutons
        start_button = Button(SCREEN_WIDTH // 2 - 150, 350, 300, 70, 
                            "Commencer le Jeu", (34, 139, 34), (50, 180, 50))
        quit_button = Button(SCREEN_WIDTH // 2 - 150, 450, 300, 70,
                           "Quitter le Jeu", (139, 0, 0), (180, 0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        start_button.draw(self.screen)
        quit_button.draw(self.screen)
        
        # Texte d'ambiance
        ambient_text = self.small_font.render("Le destin d'Aelyra repose entre tes mains...", True, (200, 200, 150))
        ambient_rect = ambient_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(ambient_text, ambient_rect)
        
        if start_button.is_clicked(mouse_pos, mouse_pressed):
            self.start_game()
        
        if quit_button.is_clicked(mouse_pos, mouse_pressed):
            pygame.quit()
            sys.exit()
    
    def draw_game(self):
        # Fond du royaume
        self.screen.fill(self.current_kingdom.bg_color)
        
        # Grille du sol
        for x in range(0, 2000, 50):
            for y in range(0, 1500, 50):
                screen_x = x - int(self.camera_x)
                screen_y = y - int(self.camera_y)
                if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                    pygame.draw.rect(self.screen, 
                                   (self.current_kingdom.bg_color[0] + 10,
                                    self.current_kingdom.bg_color[1] + 10,
                                    self.current_kingdom.bg_color[2] + 10),
                                   (screen_x, screen_y, 48, 48), 1)
        
        # Dessiner les obstacles
        for obstacle in self.current_kingdom.obstacles:
            screen_x = obstacle.x - int(self.camera_x)
            screen_y = obstacle.y - int(self.camera_y)
            
            if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
                # Dessiner comme un rocher ou arbre selon l'élément
                if self.current_kingdom.element == Element.TERRE:
                    # Rocher
                    pygame.draw.rect(self.screen, (100, 80, 60), 
                                   (screen_x, screen_y, obstacle.width, obstacle.height))
                    pygame.draw.rect(self.screen, (80, 60, 40),
                                   (screen_x, screen_y, obstacle.width, obstacle.height), 3)
                else:
                    # Arbre/végétation
                    pygame.draw.rect(self.screen, (101, 67, 33),
                                   (screen_x + obstacle.width // 3, screen_y,
                                    obstacle.width // 3, obstacle.height))
                    pygame.draw.circle(self.screen, (34, 139, 34),
                                     (screen_x + obstacle.width // 2, screen_y + obstacle.height // 3),
                                     obstacle.width // 2)
        
        # Dessiner les ennemis
        for enemy in self.current_kingdom.enemies:
            enemy.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dessiner les projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dessiner les particules
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Dessiner le joueur
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # HUD
        self.draw_hud()
        
        # Dialogue
        if self.dialogue_timer > 0:
            self.draw_dialogue()
            self.dialogue_timer -= 1
    
    def draw_hud(self):
        # Panneau HUD semi-transparent
        hud_surface = pygame.Surface((SCREEN_WIDTH, 100))
        hud_surface.set_alpha(180)
        hud_surface.fill((20, 20, 40))
        self.screen.blit(hud_surface, (0, 0))
        
        # Barre de vie
        hp_text = self.text_font.render(f"HP:", True, WHITE)
        self.screen.blit(hp_text, (20, 20))
        
        hp_bar_width = 300
        hp_bar_height = 30
        hp_percentage = self.player.hp / self.player.max_hp
        
        pygame.draw.rect(self.screen, RED, (80, 20, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.screen, GREEN, (80, 20, int(hp_bar_width * hp_percentage), hp_bar_height))
        pygame.draw.rect(self.screen, WHITE, (80, 20, hp_bar_width, hp_bar_height), 3)
        
        hp_value = self.small_font.render(f"{self.player.hp}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_value, (200, 25))
        
        # Royaume actuel
        kingdom_text = self.small_font.render(f"Royaume: {self.current_kingdom.name}", 
                                             True, YELLOW)
        self.screen.blit(kingdom_text, (20, 60))
        
        # Ennemis restants
        enemies_text = self.small_font.render(f"Ennemis: {len(self.current_kingdom.enemies)}", 
                                             True, WHITE)
        self.screen.blit(enemies_text, (400, 60))
        
        # Éléments débloqués
        elem_x = 600
        for elem in [Element.EAU, Element.TERRE, Element.AIR, Element.FEU]:
            if elem in self.player.elements:
                if elem == Element.EAU:
                    color = BLUE
                elif elem == Element.TERRE:
                    color = BROWN
                elif elem == Element.AIR:
                    color = LIGHT_BLUE
                else:
                    color = RED
                pygame.draw.circle(self.screen, color, (elem_x, 40), 15)
            else:
                pygame.draw.circle(self.screen, GRAY, (elem_x, 40), 15)
            pygame.draw.circle(self.screen, WHITE, (elem_x, 40), 15, 2)
            elem_x += 40
        
        # Contrôles
        controls = self.small_font.render("ZQSD/Flèches: Bouger | ESPACE: Attaquer | E: Soin", 
                                        True, (200, 200, 200))
        self.screen.blit(controls, (SCREEN_WIDTH - 600, 60))
    
    def draw_dialogue(self):
        # Boîte de dialogue en bas
        dialogue_height = 120
        dialogue_surface = pygame.Surface((SCREEN_WIDTH - 100, dialogue_height))
        dialogue_surface.set_alpha(220)
        dialogue_surface.fill((20, 20, 40))
        self.screen.blit(dialogue_surface, (50, SCREEN_HEIGHT - dialogue_height - 20))
        
        pygame.draw.rect(self.screen, YELLOW, 
                       (50, SCREEN_HEIGHT - dialogue_height - 20, SCREEN_WIDTH - 100, dialogue_height), 3)
        
        # Texte
        lines = []
        words = self.dialogue_text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.text_font.size(test_line)[0] < SCREEN_WIDTH - 140:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        y = SCREEN_HEIGHT - dialogue_height
        for line in lines[:3]:
            text_surf = self.text_font.render(line.strip(), True, WHITE)
            self.screen.blit(text_surf, (70, y))
            y += 35
    
    def update_game(self, keys):
        # Mettre à jour le joueur
        self.player.update(keys, self.current_kingdom.obstacles)
        
        # Tir
        if keys[pygame.K_SPACE]:
            projectile = self.player.shoot()
            if projectile:
                self.projectiles.append(projectile)
        
        # Soin
        if keys[pygame.K_e] and Element.EAU in self.player.elements:
            if self.player.hp < self.player.max_hp:
                heal_amount = self.player.heal(30)
                if heal_amount > 0:
                    self.create_particles(self.player.x + self.player.width // 2,
                                        self.player.y + self.player.height // 2,
                                        BLUE, 20)
                    self.show_dialogue(f"Soigné de {heal_amount} HP !")
        
        # Mettre à jour les ennemis
        for enemy in self.current_kingdom.enemies[:]:
            enemy.update(self.player.x, self.player.y, self.current_kingdom.obstacles)
            
            # Collision avec le joueur
            player_rect = pygame.Rect(self.player.x, self.player.y, 
                                     self.player.width, self.player.height)
            if enemy.get_rect().colliderect(player_rect):
                damage = self.player.take_damage(enemy.attack)
                if damage > 0:
                    self.create_particles(self.player.x + self.player.width // 2,
                                        self.player.y + self.player.height // 2,
                                        RED, 15)
        
        # Mettre à jour les projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            
            # Vérifier collision avec ennemis
            proj_rect = pygame.Rect(projectile.x - projectile.size, 
                                   projectile.y - projectile.size,
                                   projectile.size * 2, projectile.size * 2)
            
            for enemy in self.current_kingdom.enemies[:]:
                if proj_rect.colliderect(enemy.get_rect()):
                    if enemy.take_damage(projectile.damage):
                        self.current_kingdom.enemies.remove(enemy)
                        self.create_particles(enemy.x + enemy.width // 2,
                                            enemy.y + enemy.height // 2,
                                            YELLOW, 30)
                    else:
                        self.create_particles(enemy.x + enemy.width // 2,
                                            enemy.y + enemy.height // 2,
                                            projectile.color, 15)
                    
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break
            
            if projectile.is_dead() and projectile in self.projectiles:
                self.projectiles.remove(projectile)
        
        # Mettre à jour les particules
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Vérifier victoire du royaume
        if len(self.current_kingdom.enemies) == 0 and not self.current_kingdom.completed:
            self.current_kingdom.completed = True
            self.player.unlock_element(self.current_kingdom.element)
            self.show_dialogue(f"Royaume libéré ! Élément {self.current_kingdom.element.name} débloqué !")
            
            # Passer au royaume suivant
            self.current_kingdom_index += 1
            if self.current_kingdom_index >= len(self.kingdoms):
                self.state = GameState.VICTORY
            else:
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000, 1)
        
        # Vérifier game over
        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER
        
        # Mettre à jour la caméra
        self.update_camera()
    
    def draw_victory(self):
        self.screen.fill((20, 20, 40))
        
        # Particules de victoire
        for _ in range(3):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.create_particles(x, y, random.choice([YELLOW, (255, 215, 0), (255, 255, 150)]), 5)
        
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Titre de victoire
        victory_text = self.title_font.render("VICTOIRE !", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(victory_text, victory_rect)
        
        # Messages
        messages = [
            "Tu as libéré tous les Gardiens !",
            "L'équilibre est restauré dans Aelyra.",
            "Le Néant a été vaincu.",
            "Tu es le véritable Avatar !"
        ]
        
        y = 280
        for message in messages:
            msg_text = self.text_font.render(message, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(msg_text, msg_rect)
            y += 50
        
        # Bouton retour au menu
        menu_button = Button(SCREEN_WIDTH // 2 - 150, 520, 300, 70,
                           "Retour au Menu", (34, 139, 34), (50, 180, 50))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        menu_button.check_hover(mouse_pos)
        menu_button.draw(self.screen)
        
        if menu_button.is_clicked(mouse_pos, mouse_pressed):
            self.__init__()
    
    def draw_game_over(self):
        self.screen.fill((20, 0, 0))
        
        # Titre Game Over
        gameover_text = self.title_font.render("GAME OVER", True, RED)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(gameover_text, gameover_rect)
        
        # Message
        msg_text = self.text_font.render("Le Néant a triomphé...", True, WHITE)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(msg_text, msg_rect)
        
        # Boutons
        retry_button = Button(SCREEN_WIDTH // 2 - 150, 400, 300, 70,
                            "Réessayer", (139, 0, 0), (180, 0, 0))
        menu_button = Button(SCREEN_WIDTH // 2 - 150, 500, 300, 70,
                           "Menu Principal", (100, 100, 100), (150, 150, 150))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        retry_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
        
        retry_button.draw(self.screen)
        menu_button.draw(self.screen)
        
        if retry_button.is_clicked(mouse_pos, mouse_pressed):
            self.__init__()
            self.start_game()
        
        if menu_button.is_clicked(mouse_pos, mouse_pressed):
            self.__init__()
    
    def run(self):
        running = True
        keys_pressed = pygame.key.get_pressed()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Timer pour passer au royaume suivant
                if event.type == pygame.USEREVENT + 1:
                    self.current_kingdom = self.kingdoms[self.current_kingdom_index]
                    self.player.x = 100
                    self.player.y = 100
                    self.projectiles = []
                    self.show_dialogue(f"Bienvenue dans le {self.current_kingdom.name}...")
            
            # Mettre à jour les touches
            keys_pressed = pygame.key.get_pressed()
            
            # Dessiner selon l'état
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.GAME:
                self.update_game(keys_pressed)
                self.draw_game()
            elif self.state == GameState.VICTORY:
                self.draw_victory()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()