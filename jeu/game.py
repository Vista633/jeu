import pygame
import sys
import random
import math
from constants import *
from enums import GameState, Element, Direction
from particles import Particle
from ui import Button
from player import Player
from kingdom import Kingdom

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Avatar : L'Équilibre Perdu")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        
        # Polices - scaled for 1366x768
        self.title_font = pygame.font.Font(None, 90)
        self.subtitle_font = pygame.font.Font(None, 55)
        self.text_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 30)
        
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
            Kingdom("Royaume de l'Eau", Element.EAU, (50, 100, 150), "eau.jpg"),
            Kingdom("Royaume de la Terre", Element.TERRE, (100, 70, 40), "jungle.jpg"),
            Kingdom("Royaume de l'Air", Element.AIR, (135, 206, 235), "air.jpg"),
            Kingdom("Royaume du Feu", Element.FEU, (139, 50, 30), "feu.jpg")
        ]
        self.current_kingdom_index = 0
        self.current_kingdom = None
        
        # Dialogue
        self.dialogue_text = ""
        self.dialogue_timer = 0
    
    def start_game(self):
        self.player = Player(100, 630)  # Spawn on the bridge
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
        for i in range(11):
            offset = math.sin((self.menu_animation_offset + i * 36) / 30) * 25
            x = 120 + i * 110
            y = 60 + offset
            pygame.draw.circle(self.screen, (34, 139, 34), (int(x), int(y)), 35)
            pygame.draw.circle(self.screen, (50, 180, 50), (int(x), int(y)), 30)
        
        # Titre
        title_text = self.title_font.render("AVATAR", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        
        # Ombre du titre
        shadow_text = self.title_font.render("AVATAR", True, (139, 69, 19))
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 5, 185))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Sous-titre
        subtitle_text = self.subtitle_font.render("Héritier des 4 Mondes", True, (255, 250, 205))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Boutons
        start_button = Button(SCREEN_WIDTH // 2 - 175, 360, 350, 75, 
                            "Commencer le Jeu", (34, 139, 34), (50, 180, 50))
        quit_button = Button(SCREEN_WIDTH // 2 - 175, 460, 350, 75,
                           "Quitter le Jeu", (139, 0, 0), (180, 0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        start_button.draw(self.screen)
        quit_button.draw(self.screen)
        
        # Texte d'ambiance
        ambient_text = self.small_font.render("Le destin d'Aelyra repose entre tes mains...", True, (200, 200, 150))
        ambient_rect = ambient_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(ambient_text, ambient_rect)
        
        if start_button.is_clicked(mouse_pos, mouse_pressed):
            self.start_game()
        
        if quit_button.is_clicked(mouse_pos, mouse_pressed):
            pygame.quit()
            sys.exit()
    
    def draw_game(self):
        # Fond du royaume - use image if available, otherwise use color
        if self.current_kingdom.bg_image:
            self.screen.blit(self.current_kingdom.bg_image, (0, 0))
        else:
            self.screen.fill(self.current_kingdom.bg_color)
        
        # No grid or obstacles in platform mode
        
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
        hud_surface = pygame.Surface((SCREEN_WIDTH, 110))
        hud_surface.set_alpha(180)
        hud_surface.fill((20, 20, 40))
        self.screen.blit(hud_surface, (0, 0))
        
        # Barre de vie
        hp_text = self.text_font.render(f"HP:", True, WHITE)
        self.screen.blit(hp_text, (25, 25))
        
        hp_bar_width = 320
        hp_bar_height = 35
        hp_percentage = self.player.hp / self.player.max_hp
        
        pygame.draw.rect(self.screen, RED, (100, 25, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.screen, GREEN, (100, 25, int(hp_bar_width * hp_percentage), hp_bar_height))
        pygame.draw.rect(self.screen, WHITE, (100, 25, hp_bar_width, hp_bar_height), 3)
        
        hp_value = self.small_font.render(f"{self.player.hp}/{self.player.max_hp}", True, WHITE)
        self.screen.blit(hp_value, (230, 32))
        
        # Royaume actuel
        kingdom_text = self.small_font.render(f"Royaume: {self.current_kingdom.name}", 
                                             True, YELLOW)
        self.screen.blit(kingdom_text, (25, 70))
        
        # Ennemis restants
        enemies_text = self.small_font.render(f"Ennemis: {len(self.current_kingdom.enemies)}", 
                                             True, WHITE)
        self.screen.blit(enemies_text, (450, 70))
        
        # Éléments débloqués
        elem_x = 720
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
                pygame.draw.circle(self.screen, color, (elem_x, 50), 18)
            else:
                pygame.draw.circle(self.screen, GRAY, (elem_x, 50), 18)
            pygame.draw.circle(self.screen, WHITE, (elem_x, 50), 18, 2)
            elem_x += 45
        
        # Contrôles
        controls = self.small_font.render("ZQSD/Flèches: Bouger | ESPACE: Attaquer | E: Soin", 
                                        True, (200, 200, 200))
        self.screen.blit(controls, (SCREEN_WIDTH - 650, 70))
    
    def draw_dialogue(self):
        # Boîte de dialogue en bas
        dialogue_height = 120
        dialogue_width = SCREEN_WIDTH - 150
        dialogue_surface = pygame.Surface((dialogue_width, dialogue_height))
        dialogue_surface.set_alpha(220)
        dialogue_surface.fill((20, 20, 40))
        self.screen.blit(dialogue_surface, (75, SCREEN_HEIGHT - dialogue_height - 30))
        
        pygame.draw.rect(self.screen, YELLOW, 
                       (75, SCREEN_HEIGHT - dialogue_height - 30, dialogue_width, dialogue_height), 3)
        
        # Texte
        lines = []
        words = self.dialogue_text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.text_font.size(test_line)[0] < dialogue_width - 80:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        y = SCREEN_HEIGHT - dialogue_height - 5
        for line in lines[:3]:
            text_surf = self.text_font.render(line.strip(), True, WHITE)
            self.screen.blit(text_surf, (100, y))
            y += 40
    
    def update_game(self, keys):
        # Mettre à jour le joueur
        self.player.update(keys, self.current_kingdom.obstacles)
        
        # Tir avec clic gauche de la souris
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # Left click
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
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(victory_text, victory_rect)
        
        # Messages
        messages = [
            "Tu as libéré tous les Gardiens !",
            "L'équilibre est restauré dans Aelyra.",
            "Le Néant a été vaincu.",
            "Tu es le véritable Avatar !"
        ]
        
        y = 300
        for message in messages:
            msg_text = self.text_font.render(message, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(msg_text, msg_rect)
            y += 55
        
        # Bouton retour au menu
        menu_button = Button(SCREEN_WIDTH // 2 - 175, 540, 350, 75,
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
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(gameover_text, gameover_rect)
        
        # Message
        msg_text = self.text_font.render("Le Néant a triomphé...", True, WHITE)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(msg_text, msg_rect)
        
        # Boutons
        retry_button = Button(SCREEN_WIDTH // 2 - 175, 420, 350, 75,
                            "Réessayer", (139, 0, 0), (180, 0, 0))
        menu_button = Button(SCREEN_WIDTH // 2 - 175, 520, 350, 75,
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
                    self.player.y = 630  # Spawn on the bridge
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
