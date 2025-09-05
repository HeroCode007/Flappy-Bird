import sys
import math
import random
import pygame

# -----------------------------
# Configuration
# -----------------------------
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 2200.0
FLAP_IMPULSE = -520.0
PIPE_GAP = 160
PIPE_SPEED = -160.0
PIPE_SPAWN_EVERY = 1.25
GROUND_HEIGHT = 100
BIRD_X = 84
MAX_DROP_ANGLE = 80
MAX_RISE_ANGLE = -25

pygame.init()
pygame.display.set_caption("Flappy Bird — SYED SAIF ALI")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# -----------------------------
# Asset Loading
# -----------------------------
def load_image(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

# Background (scaled to window)
BG = load_image("assets/background-day.png", (WIDTH, HEIGHT))

# Ground
GROUND = load_image("assets/base.png", (WIDTH, GROUND_HEIGHT))

# Pipes
PIPE_BODY = load_image("assets/pipe-green.png")
PIPE_BODY_TOP = pygame.transform.flip(PIPE_BODY, False, True)

# Bird frames
BIRD_FRAMES = [
    load_image("assets/yellowbird-upflap.png"),
    load_image("assets/yellowbird-midflap.png"),
    load_image("assets/yellowbird-downflap.png"),
]

# Font (keep default for now)
font = pygame.font.SysFont("Arial", 28)

# -----------------------------
# Entities
# -----------------------------
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = BIRD_FRAMES
        self.frame_index = 0.0
        self.image = self.frames[0]
        self.base_image = self.image
        self.rect = self.image.get_rect(midleft=(x, y))
        self.vel_y = 0.0
        self.alive = True

    def flap(self):
        if self.alive:
            self.vel_y = FLAP_IMPULSE

    def update(self, dt):
        if self.alive:
            self.vel_y += GRAVITY * dt
            self.rect.y += int(self.vel_y * dt)
            # animate wings
            self.frame_index = (self.frame_index + 10.0 * dt) % len(self.frames)
            self.base_image = self.frames[int(self.frame_index)]
        # tilt
        angle = 0.0
        if self.vel_y > 0:
            t = min(1.0, self.vel_y / 600.0)
            angle = MAX_DROP_ANGLE * t
        else:
            t = min(1.0, -self.vel_y / 500.0)
            angle = MAX_RISE_ANGLE * t
        self.image = pygame.transform.rotozoom(self.base_image, angle, 1.0)
        self.mask = pygame.mask.from_surface(self.image)

class PipePair:
    def __init__(self, x, gap_y, gap_size=PIPE_GAP):
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.x = x
        self.passed = False

        self.top_img = PIPE_BODY_TOP
        self.bottom_img = PIPE_BODY

        self.top_rect = self.top_img.get_rect(midbottom=(x, gap_y - gap_size // 2))
        self.bottom_rect = self.bottom_img.get_rect(midtop=(x, gap_y + gap_size // 2))

        self.top_mask = pygame.mask.from_surface(self.top_img)
        self.bottom_mask = pygame.mask.from_surface(self.bottom_img)

    def update(self, dt):
        dx = PIPE_SPEED * dt
        self.x += dx
        self.top_rect.centerx = int(self.x)
        self.bottom_rect.centerx = int(self.x)

    def draw(self, target):
        target.blit(self.top_img, self.top_rect)
        target.blit(self.bottom_img, self.bottom_rect)

    def offscreen(self):
        return self.top_rect.right < -5

    def collide(self, bird):
        # top pipe
        offset_top = (self.top_rect.left - bird.rect.left, self.top_rect.top - bird.rect.top)
        if bird.mask.overlap(self.top_mask, offset_top):
            return True
        # bottom pipe
        offset_bottom = (self.bottom_rect.left - bird.rect.left, self.bottom_rect.top - bird.rect.top)
        if bird.mask.overlap(self.bottom_mask, offset_bottom):
            return True
        return False

# -----------------------------
# Game State
# -----------------------------
def spawn_gap_y():
    margin = 48
    return random.randint(margin + PIPE_GAP // 2, HEIGHT - GROUND_HEIGHT - margin - PIPE_GAP // 2)

def reset_game():
    bird = Bird(BIRD_X, HEIGHT // 2)
    pipes = [PipePair(WIDTH + 80, spawn_gap_y())]
    score = 0
    t_accum = 0.0
    return bird, pipes, score, t_accum

def draw_ground(scroll_x):
    x1 = -(scroll_x % WIDTH)
    screen.blit(GROUND, (x1, HEIGHT - GROUND_HEIGHT))
    screen.blit(GROUND, (x1 + WIDTH, HEIGHT - GROUND_HEIGHT))

def draw_score(score, big=False):
    surf = font.render(str(score), True, (40, 40, 40))
    if big:
        surf = pygame.transform.smoothscale(surf, (int(surf.get_width()*1.2), int(surf.get_height()*1.2)))
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 40))
     
 
def show_start_screen():
    waiting = True
    while waiting:
        screen.blit(BG, (0, 0))
        draw_ground(0)

        title = font.render("Flappy Bird", True, (20, 20, 20))
        instr1 = font.render("SPACE - Fly", True, (20, 20, 20))
        instr2 = font.render("R - Restart", True, (20, 20, 20))
        instr3 = font.render("ESC - Quit", True, (20, 20, 20))

        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(instr1, (WIDTH//2 - instr1.get_width()//2, HEIGHT//2))
        screen.blit(instr2, (WIDTH//2 - instr2.get_width()//2, HEIGHT//2 + 40))
        screen.blit(instr3, (WIDTH//2 - instr3.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:   # Start game
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
   

# -----------------------------
# Main Loop
# -----------------------------
def main():    
    show_start_screen()   # 👈 show instructions first
    bg_scroll = 0.0
    bird, pipes, score, t_accum = reset_game()
    running = True
    started = False
    game_over = False


    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if not started:
                        started = True
                    if game_over:
                        bird, pipes, score, t_accum = reset_game()
                        started = False
                        game_over = False
                    else:
                        bird.flap()

        # Update
        if started and not game_over:
            bird.update(dt)
            for p in pipes:
                p.update(dt)
            bg_scroll += -PIPE_SPEED * 0.25 * dt
            t_accum += dt

            if t_accum >= PIPE_SPAWN_EVERY:
                t_accum -= PIPE_SPAWN_EVERY
                pipes.append(PipePair(WIDTH + 20, spawn_gap_y()))

            pipes = [p for p in pipes if not p.offscreen()]

            for p in pipes:
                if not p.passed and p.top_rect.centerx < bird.rect.centerx:
                    p.passed = True
                    score += 1
                if p.collide(bird):
                    game_over = True
                    bird.alive = False

            if bird.rect.top < -40:
                bird.rect.top = -40
                bird.vel_y = 0
            ground_y = HEIGHT - GROUND_HEIGHT - bird.image.get_height() + 10
            if bird.rect.top >= ground_y:
                bird.rect.top = ground_y
                bird.vel_y = 0
                game_over = True
                bird.alive = False
        else:
            # idle bobbing
            bird.frame_index = (bird.frame_index + 6.0 * dt) % len(bird.frames)
            bird.base_image = bird.frames[int(bird.frame_index)]
            bird.image = bird.base_image
            bird.mask = pygame.mask.from_surface(bird.image)
            t = pygame.time.get_ticks() / 1000.0
            bird.rect.centery = HEIGHT // 2 + int(math.sin(t * 2.2) * 8)

        # Draw
        screen.blit(BG, (0, 0))
        for p in pipes:
            p.draw(screen)
        screen.blit(bird.image, bird.rect)
        draw_ground(bg_scroll)

        if not started:
            tip = font.render("Press SPACE to start", True, (20, 20, 20))
            screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 110))
        elif game_over:
            over = font.render("Game Over — SPACE to retry", True, (30, 30, 30))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 20))
            draw_score(score, big=True)
        else:
            draw_score(score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
