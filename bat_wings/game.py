import pgzrun
import math
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 480
TITLE = "Bat Wings"

# Animações do player usando arquivos individuais
PLAYER_IDLE = ["batroot_sleeping"]
PLAYER_FLY = ["bat_flying0", "bat_flying1", "bat_flying2", "bat_flying3"]
PLAYER_ATTACK = ["bat_attack0", "bat_attack1", "bat_attack2", "bat_attack3", "bat_attack4", "bat_attack5"]
PLAYER_HURT = ["batroot_hurt0", "batroot_hurt1", "batroot_hurt2", "batroot_hurt3"]
PLAYER_DEATH = ["batroot_death0", "batroot_death1", "batroot_death2", "batroot_death3", "batroot_death4", "batroot_death5", "batroot_death6"]
# Inimigos agora usam os sprites bettle1 até bettle4
ENEMY_IDLE = ["bettle1", "bettle2", "bettle3", "bettle4"]
ENEMY_FLY = ["bettle1", "bettle2", "bettle3", "bettle4"]
BULLET_IMG = "projectile"         # Agora usando o sprite projectile.png
BG_IMG = "background"              # Agora usando background.jpg
BG_MUSIC = "bg_music"
SND_SHOOT = "shoot"
SND_HIT = "hit"
SND_EXPLO = "explosion"

MENU, RUNNING, GAMEOVER = 0, 1, 2
state = MENU
sound_on = True
score = 0
lives = 3

menu_buttons = [
    {"label": "Start Game", "rect": Rect(320, 180, 160, 40)},
    {"label": "Sound On/Off", "rect": Rect(320, 240, 160, 40)},
    {"label": "Exit Game", "rect": Rect(320, 300, 160, 40)}
]

class Player:
    def __init__(self):
        self.x, self.y = 120, HEIGHT // 2
        self.vx, self.vy = 0, 0
        self.speed = 3.2
        self.anim = PLAYER_IDLE
        self.frame = 0
        self.frame_timer = 0
        self.shoot_cooldown = 0
        self.scale = 1.5  # Fator de escala do morcego
        self.width = int(48 * self.scale)
        self.height = int(32 * self.scale)
        self.rect = Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        self.alive = True
        self.is_dead = False  # Novo atributo
    def update(self):
        if self.is_dead:
            # Só anima o death
            self.anim = PLAYER_DEATH
            self.frame_timer += 1
            if self.frame_timer > 8:
                if self.frame < len(self.anim) - 1:
                    self.frame += 1
                self.frame_timer = 0
            return
        keys = keyboard
        self.vx = (keys.right - keys.left) * self.speed
        self.vy = (keys.down - keys.up) * self.speed
        self.x += self.vx
        self.y += self.vy
        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))
        self.y = max(self.height // 2, min(HEIGHT - self.height // 2, self.y))
        self.rect.topleft = (self.x - self.width // 2, self.y - self.height // 2)
        # Sempre usar PLAYER_FLY, mesmo parado
        new_anim = PLAYER_FLY
        if self.anim != new_anim:
            self.anim = new_anim
            self.frame = 0
        self.frame_timer += 1
        if self.frame_timer > 8:
            self.frame = (self.frame + 1) % len(self.anim)
            self.frame_timer = 0
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    def draw(self):
        screen.blit(self.anim[self.frame], (self.x - self.width // 2, self.y - self.height // 2))
    def shoot(self):
        if self.shoot_cooldown == 0 and not self.is_dead:
            bullets.append(Bullet(self.x+20, self.y, 7, 0))
            self.shoot_cooldown = 18

class Enemy:
    def __init__(self):
        self.x = WIDTH + 40
        self.y = random.randint(40, HEIGHT-40)
        self.vx = -random.uniform(3.5, 5.0)  # Mais rápido
        self.vy = math.sin(random.random()*math.pi*2) * random.uniform(0.5, 1.5)
        self.anim = ENEMY_FLY
        self.frame = 0
        self.frame_timer = 0
        self.rect = Rect(self.x-20, self.y-16, 40, 32)
        self.hp = 2
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y < 32 or self.y > HEIGHT-32:
            self.vy *= -1
        self.rect.topleft = (self.x-20, self.y-16)
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame = (self.frame + 1) % len(self.anim)
            self.frame_timer = 0
    def draw(self):
        screen.blit(self.anim[self.frame], (self.x-20, self.y-16))

class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.rect = Rect(self.x-8, self.y-4, 16, 8)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x-8, self.y-4)
    def draw(self):
        screen.blit(BULLET_IMG, (self.x-8, self.y-4))

player = Player()
enemies = []
bullets = []
spawn_timer = 0
# Variáveis para rolagem do fundo
bg_x1 = 0
bg_x2 = WIDTH
bg_scroll_speed = 4  # Mais rápido

# Variáveis para score por distância
meters = 0
meters_timer = 0
speed_increase_timer = 0

def reset_game():
    global player, enemies, bullets, score, lives, bg_x1, bg_x2, meters, meters_timer, speed_increase_timer, bg_scroll_speed
    player = Player()
    enemies.clear()
    bullets.clear()
    score = 0
    lives = 3
    bg_x1 = 0
    bg_x2 = WIDTH
    meters = 0
    meters_timer = 0
    speed_increase_timer = 0
    bg_scroll_speed = 4

def update():
    global state, spawn_timer, bg_x1, bg_x2, lives, score, meters, meters_timer, speed_increase_timer, bg_scroll_speed
    if state == MENU:
        return
    if state == GAMEOVER:
        player.is_dead = True  # Ativa animação de morte
        player.update()
        return
    # Rolagem do fundo
    bg_x1 -= bg_scroll_speed
    bg_x2 -= bg_scroll_speed
    if bg_x1 <= -WIDTH:
        bg_x1 = WIDTH
    if bg_x2 <= -WIDTH:
        bg_x2 = WIDTH
    # Score por metros percorridos
    meters_timer += 1
    if meters_timer >= 5:
        meters += 1
        meters_timer = 0
        score = meters
    speed_increase_timer += 1
    if speed_increase_timer >= 120:
        bg_scroll_speed += 0.3
        speed_increase_timer = 0
    player.update()
    for b in bullets[:]:
        b.update()
        if b.x > WIDTH+20:
            bullets.remove(b)
    enemies_to_remove = []
    bullets_to_remove = []
    for e in enemies:
        e.update()
        if e.x < -40:
            enemies_to_remove.append(e)
        for b in bullets:
            if e.rect.colliderect(b.rect):
                e.hp -= 1
                if b not in bullets_to_remove:
                    bullets_to_remove.append(b)
                if e.hp <= 0 and e not in enemies_to_remove:
                    enemies_to_remove.append(e)
                    score += 10
        if e.rect.colliderect(player.rect):
            if e not in enemies_to_remove:
                enemies_to_remove.append(e)
            lives -= 1
            if lives <= 0:
                state = GAMEOVER
                music.stop()
    for e in enemies_to_remove:
        if e in enemies:
            enemies.remove(e)
    for b in bullets_to_remove:
        if b in bullets:
            bullets.remove(b)
    spawn_timer += 1
    if spawn_timer > 50:
        enemies.append(Enemy())
        spawn_timer = 0

def draw():
    screen.clear()
    # Desenha o fundo com rolagem infinita na posição padrão (y=0)
    screen.blit(BG_IMG, (bg_x1, 0))
    screen.blit(BG_IMG, (bg_x2, 0))
    if state == MENU:
        draw_menu()
    elif state == RUNNING:
        player.draw()
        for e in enemies:
            e.draw()
        for b in bullets:
            b.draw()
        draw_hud()
    elif state == GAMEOVER:
        draw_gameover()

def draw_menu():
    screen.draw.text(TITLE, center=(WIDTH//2, 100), fontsize=64, color="white", owidth=2, ocolor="black")
    for btn in menu_buttons:
        screen.draw.filled_rect(btn["rect"], (60,60,60))
        screen.draw.rect(btn["rect"], "white")
        screen.draw.text(btn["label"], center=btn["rect"].center, fontsize=32, color="white")
    screen.draw.text("by YourName", center=(WIDTH//2, 400), fontsize=24, color="gray")

def draw_hud():
    screen.draw.text(f"Score: {score}", (20, 10), fontsize=32, color="yellow")
    screen.draw.text(f"Metros: {meters}", (20, 44), fontsize=28, color="white")
    screen.draw.text(f"Velocidade: {bg_scroll_speed:.1f}", (20, 74), fontsize=24, color="gray")
    screen.draw.text(f"Lives: {lives}", (WIDTH-140, 10), fontsize=32, color="red")

def draw_gameover():
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2-40), fontsize=64, color="red", owidth=2, ocolor="black")
    screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2+20), fontsize=36, color="white")
    screen.draw.text(f"Distância: {meters} m", center=(WIDTH//2, HEIGHT//2+60), fontsize=32, color="yellow")
    screen.draw.text("Press ENTER to return to menu", center=(WIDTH//2, HEIGHT//2+100), fontsize=28, color="gray")

def on_key_down(key):
    global state, sound_on
    if state == MENU:
        if key == keys.RETURN:
            start_game()
    elif state == RUNNING:
        if key == keys.SPACE or key == keys.Z:
            player.shoot()
    elif state == GAMEOVER:
        if key == keys.RETURN:
            state = MENU
            if sound_on:
                music.play(BG_MUSIC)
            else:
                music.stop()

def on_mouse_down(pos):
    global state, sound_on
    if state != MENU:
        return
    for i, btn in enumerate(menu_buttons):
        if btn["rect"].collidepoint(pos):
            if i == 0:
                start_game()
            elif i == 1:
                sound_on = not sound_on
                if sound_on:
                    music.play(BG_MUSIC)
                else:
                    music.stop()
            elif i == 2:
                exit()

def start_game():
    global state
    reset_game()
    state = RUNNING
    if sound_on:
        music.play(BG_MUSIC)
    else:
        music.stop()

pgzrun.go() 