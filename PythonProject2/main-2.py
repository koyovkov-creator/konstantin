import pygame
import sys

pygame.init()*

# SETTINGS
WIDTH, HEIGHT = 1920, 600
FPS = 60
GRAVITY = 0.6
MAX_FALL_SPEED = 18

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Platformer")

clock = pygame.time.Clock()

# COLORS
SKY_TOP = (92, 148, 252)
SKY_BOT = (135, 206, 235)
BROWN = (181, 101, 29)
DARK_BROWN = (120, 60, 10)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 140, 30)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)
BRICK_RED = (196, 80, 40)
BRICK_DARK = (140, 50, 20)
GROUND_GREEN = (80, 180, 60)
GROUND_DARK = (100, 70, 30)
UNDERGROUND_BG = (0, 0, 0)
UNDERGROUND_BLOCK = (100, 80, 60)
UNDERGROUND_DARK = (60, 45, 30)
PIPE_GREEN = (0, 168, 68)
PIPE_DARK = (0, 100, 40)
COIN_YELLOW = (255, 200, 0)
GOOMBA_BROWN = (190, 120, 50)
GOOMBA_DARK = (130, 70, 20)
CLOUD_WHITE = (255, 255, 255)
CLOUD_GRAY = (230, 230, 230)

font_big = pygame.font.SysFont("Arial Black", 52)
font_med = pygame.font.SysFont("Arial", 32)
font_small = pygame.font.SysFont("Arial", 22)

# ─── PIXEL ART DRAWING HELPERS ───────────────────────────────────────────────

def draw_pixel_mario(surface, x, y, facing_right=True, scale=3):
    """Draw a proper pixel-art Mario sprite."""
    # 16×16 pixel Mario, colours: R=red, B=brown(skin), S=blue(suit), Y=yellow(buttons), K=black, W=white
    hat_r = (200, 30, 30)
    skin  = (253, 187, 122)
    suit  = (0, 68, 204)
    shoe  = (120, 60, 10)
    musta = (100, 50, 10)

    pixels = [
        # row 0-1: hat
        "....RRRRRR......",
        "...RRRRRRRRRR...",
        # row 2-3: face
        "..BBBBBBBBBBB...",
        ".BBBBBBBBBBBBB..",
        # row 4: eyes / moustache
        "..BBkBBBBkBBBB..",
        "..BkkkBBBkkkBBB.",
        # row 5: moustache thick
        "...BBBBBBBBBBB..",
        # row 6-7: body
        ".SSSSSSSSSSSS...",
        "SSSSSSSSSSSSSS..",
        # row 8: buttons
        "SSYSSSSSSYSSSS..",
        # row 9-10: legs
        ".SSSSSSSSSSS...",
        "..SSSSS.SSSSS...",
        # row 11-12: shoes
        "..EEEEE.EEEEE...",
        "..EEEEE.EEEEE...",
    ]

    color_map = {
        'R': hat_r,
        'B': skin,
        'S': suit,
        'Y': COIN_YELLOW,
        'k': BLACK,
        'E': shoe,
        'm': musta,
        '.': None,
    }

    # Simple scaled block render
    w = 16 * scale
    h = len(pixels) * scale
    if not hasattr(draw_pixel_mario, '_cache'):
        draw_pixel_mario._cache = {}

    key = (scale, facing_right)
    if key not in draw_pixel_mario._cache:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for row_i, row in enumerate(pixels):
            for col_i, ch in enumerate(row[:16]):
                col = color_map.get(ch)
                if col:
                    pygame.draw.rect(surf, col,
                                     (col_i * scale, row_i * scale, scale, scale))
        if not facing_right:
            surf = pygame.transform.flip(surf, True, False)
        draw_pixel_mario._cache[key] = surf

    surface.blit(draw_pixel_mario._cache[key], (x, y))
    return w, h


def draw_brick_block(surface, x, y, w=64, h=64):
    """Draw a Mario-style brick block."""
    pygame.draw.rect(surface, BRICK_RED, (x, y, w, h))
    # mortar lines horizontal
    for row in range(0, h, 16):
        pygame.draw.line(surface, BRICK_DARK, (x, y + row), (x + w, y + row), 2)
    # mortar lines vertical (staggered)
    for row in range(0, h, 16):
        offset = 0 if (row // 16) % 2 == 0 else w // 2
        for cx in range(offset, w + 1, w // 2):
            pygame.draw.line(surface, BRICK_DARK,
                             (x + cx, y + row), (x + cx, y + row + 16), 2)
    # highlight top-left
    pygame.draw.line(surface, (220, 110, 60), (x + 1, y + 1), (x + w - 1, y + 1), 1)
    pygame.draw.line(surface, (220, 110, 60), (x + 1, y + 1), (x + 1, y + h - 1), 1)


def draw_ground_block(surface, x, y, w=64, h=64, underground=False):
    """Draw a ground tile."""
    if underground:
        base = UNDERGROUND_BLOCK
        dark = UNDERGROUND_DARK
        top_col = (130, 100, 70)
    else:
        base = (200, 150, 80)
        dark = (140, 90, 40)
        top_col = GROUND_GREEN

    pygame.draw.rect(surface, base, (x, y, w, h))
    # top green strip
    pygame.draw.rect(surface, top_col, (x, y, w, 8))
    # grid lines
    for gx in range(0, w, 16):
        pygame.draw.line(surface, dark, (x + gx, y + 8), (x + gx, y + h), 1)
    for gy in range(8, h, 16):
        pygame.draw.line(surface, dark, (x, y + gy), (x + w, y + gy), 1)


def draw_platform(surface, x, y, w, h):
    """Draw a floating platform block."""
    pygame.draw.rect(surface, (80, 200, 80), (x, y, w, h))
    pygame.draw.rect(surface, (50, 150, 50), (x, y + h // 2, w, h // 2))
    pygame.draw.rect(surface, (120, 240, 100), (x, y, w, 6))
    pygame.draw.rect(surface, (40, 100, 40), (x, y, w, h), 2)


def draw_pipe(surface, x, y, h=80, camera_x=0):
    rx = x - camera_x
    pw = 48
    # body
    pygame.draw.rect(surface, PIPE_GREEN, (rx + 4, y + 16, pw - 8, h - 16))
    pygame.draw.rect(surface, PIPE_DARK, (rx + pw - 8 - 4, y + 16, 8, h - 16))
    # lip
    pygame.draw.rect(surface, PIPE_GREEN, (rx, y, pw, 16))
    pygame.draw.rect(surface, PIPE_DARK, (rx + pw - 8, y, 8, 16))
    # highlight
    pygame.draw.line(surface, (100, 230, 120), (rx + 6, y + 2), (rx + 6, y + h), 3)


def draw_cloud(surface, cx, cy, camera_x):
    x = cx - camera_x
    for ox, oy, r in [(0, 0, 30), (28, -12, 22), (-28, -10, 22), (0, -18, 25)]:
        pygame.draw.circle(surface, CLOUD_WHITE, (x + ox, cy + oy), r)
    for ox, oy, r in [(0, 0, 30), (28, -12, 22), (-28, -10, 22), (0, -18, 25)]:
        pygame.draw.circle(surface, CLOUD_GRAY, (x + ox + 2, cy + oy + 2), r)
    for ox, oy, r in [(0, 0, 30), (28, -12, 22), (-28, -10, 22), (0, -18, 25)]:
        pygame.draw.circle(surface, CLOUD_WHITE, (x + ox, cy + oy), r)


def draw_goomba(surface, x, y, camera_x):
    rx = x - camera_x
    # body
    pygame.draw.ellipse(surface, GOOMBA_BROWN, (rx, y + 8, 44, 36))
    # head
    pygame.draw.ellipse(surface, GOOMBA_BROWN, (rx + 2, y, 40, 28))
    # brow (angry)
    pygame.draw.line(surface, GOOMBA_DARK, (rx + 6, y + 6), (rx + 18, y + 10), 3)
    pygame.draw.line(surface, GOOMBA_DARK, (rx + 38, y + 6), (rx + 26, y + 10), 3)
    # eyes
    pygame.draw.circle(surface, WHITE, (rx + 12, y + 14), 5)
    pygame.draw.circle(surface, WHITE, (rx + 32, y + 14), 5)
    pygame.draw.circle(surface, BLACK, (rx + 13, y + 15), 3)
    pygame.draw.circle(surface, BLACK, (rx + 33, y + 15), 3)
    # feet
    pygame.draw.ellipse(surface, GOOMBA_DARK, (rx - 2, y + 36, 20, 12))
    pygame.draw.ellipse(surface, GOOMBA_DARK, (rx + 26, y + 36, 20, 12))


def draw_sky_gradient(surface, underground):
    if underground:
        surface.fill(UNDERGROUND_BG)
    else:
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_flag(surface, x, y, camera_x):
    rx = x - camera_x
    pygame.draw.line(surface, (200, 200, 200), (rx, y), (rx, y + 300), 4)
    pygame.draw.polygon(surface, (0, 200, 0),
                        [(rx, y), (rx + 40, y + 20), (rx, y + 40)])
    pygame.draw.rect(surface, DARK_BROWN, (rx - 20, y + 296, 40, 12))


# ─── COIN ────────────────────────────────────────────────────────────────────
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 16, y - 16, 16, 16)
        self.collected = False
        self.anim = 0

    def draw(self, surface, camera_x):
        if not self.collected:
            self.anim = (self.anim + 3) % 360
            import math
            scale = abs(math.cos(math.radians(self.anim)))
            w = max(4, int(14 * scale))
            cx = self.rect.x - camera_x + 8
            cy = self.rect.y + 8
            pygame.draw.ellipse(surface, COIN_YELLOW,
                                (cx - w // 2, cy - 8, w, 16))
            pygame.draw.ellipse(surface, (255, 240, 80),
                                (cx - max(2, w // 2 - 2), cy - 6,
                                 max(2, w - 4), 12))


# ─── PLAYER ──────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 52)
        self.vel_y = 0
        self.vel_x = 0
        self.speed = 5
        self.jump_power = -14
        self.on_ground = False
        self.dead = False
        self.facing_right = True
        self.score = 0

        # jump buffer
        self.jump_buffer = 0

    def move(self, blocks):
        keys = pygame.key.get_pressed()

        dx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.facing_right = False

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.facing_right = True

        # smooth movement
        self.vel_x += (dx - self.vel_x) * 0.3

        if abs(self.vel_x) < 0.3:
            self.vel_x = 0

        # gravity
        self.vel_y += GRAVITY

        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.on_ground = False

        # X collision
        self.rect.x += int(self.vel_x)

        for block in blocks:
            if self.rect.colliderect(block):

                if self.vel_x > 0:
                    self.rect.right = block.left
                    self.vel_x = 0

                elif self.vel_x < 0:
                    self.rect.left = block.right
                    self.vel_x = 0

        # Y collision
        self.rect.y += int(self.vel_y)

        for block in blocks:
            if self.rect.colliderect(block):

                # landing
                if self.vel_y > 0:
                    self.rect.bottom = block.top
                    self.vel_y = 0
                    self.on_ground = True

                # head hit
                elif self.vel_y < 0:
                    self.rect.top = block.bottom
                    self.vel_y = 0

        # jump buffer timer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        # instant jump after landing
        if self.jump_buffer > 0 and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.jump_buffer = 0

        # fall off map
        if self.rect.y > 900:
            self.dead = True

    def request_jump(self):
        # saves jump input for few frames
        self.jump_buffer = 10

    def draw(self, surface, camera_x):
        px = self.rect.x - camera_x
        py = self.rect.y
        draw_pixel_mario(surface, px - 3, py - 2,
                          self.facing_right, scale=3)
# ─── ENEMY ───────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 44, 44)
        self.direction = 1
        self.speed = 2
        self.alive = True
        self.squish_timer = 0

    def move(self, blocks):
        self.rect.x += self.direction * self.speed

        hit_wall = False
        for block in blocks:
            if self.rect.colliderect(block):
                if self.direction > 0:
                    self.rect.right = block.left
                else:
                    self.rect.left = block.right
                hit_wall = True

        if hit_wall:
            self.direction *= -1

        # Turn around at edges
        edge_check = pygame.Rect(
            self.rect.x + self.direction * self.rect.width,
            self.rect.bottom + 2, 4, 4)
        on_ground = any(edge_check.colliderect(b) for b in blocks)
        if not on_ground:
            self.direction *= -1

    def draw(self, surface, camera_x):
        if self.alive:
            draw_goomba(surface, self.rect.x, self.rect.y, camera_x)
        elif self.squish_timer > 0:
            rx = self.rect.x - camera_x
            pygame.draw.ellipse(surface, GOOMBA_BROWN,
                                (rx, self.rect.y + 28, 44, 16))
            self.squish_timer -= 1


# ─── PIPE (collidable) ───────────────────────────────────────────────────────
class Pipe:
    def __init__(self, x, y, h=80):
        self.rect = pygame.Rect(x, y, 48, h)
        self.h = h

    def draw(self, surface, camera_x):
        draw_pipe(surface, self.rect.x, self.rect.y, self.h, camera_x)


# ─── LEVEL BUILDER ───────────────────────────────────────────────────────────

def make_ground(x_start, x_end, y=536, step=64, underground=False):
    blocks = []
    for i in range(x_start, x_end, step):
        blocks.append(('ground', pygame.Rect(i, y, step, 64), underground))
    return blocks


def make_platform(x, y, w, h=20):
    return [('platform', pygame.Rect(x, y, w, h), False)]


def make_brick(x, y, w=64, h=64):
    return [('brick', pygame.Rect(x, y, w, h), False)]


def build_level(ground_data, platform_data, brick_data, pipe_list,
                enemy_list, coin_list, flag_x, underground=False):
    all_blocks = ground_data + platform_data + brick_data
    all_rects = [b[1] for b in all_blocks] + [p.rect for p in pipe_list]
    return {
        'blocks': all_blocks,
        'rects': all_rects,
        'enemies': enemy_list,
        'coins': coin_list,
        'pipes': pipe_list,
        'flag_x': flag_x,
        'underground': underground,
    }


levels = []

# ── LEVEL 1 ── Overworld, gentle introduction ──────────────────────────────
gnd1 = make_ground(0, 5000, underground=False)
plat1 = (
    make_platform(350, 460, 180) +
    make_platform(700, 410, 140) +
    make_platform(1050, 360, 200) +
    make_platform(1400, 420, 160) +
    make_platform(1800, 380, 200) +
    make_platform(2200, 440, 160) +
    make_platform(2600, 390, 200) +
    make_platform(3000, 340, 240) +
    make_platform(3500, 400, 160) +
    make_platform(3900, 350, 200)
)
bricks1 = (
    make_brick(380, 370, 64) + make_brick(448, 370, 64) +
    make_brick(1100, 290, 64) + make_brick(1164, 290, 64) +
    make_brick(2250, 360, 64) + make_brick(2314, 360, 64)
)
pipes1 = [Pipe(600, 456, 80), Pipe(1600, 456, 96), Pipe(2800, 456, 112), Pipe(3700, 456, 80)]
enemies1 = [Enemy(750, 490), Enemy(1200, 490), Enemy(1700, 490),
            Enemy(2400, 490), Enemy(2900, 490), Enemy(3300, 490), Enemy(3800, 490)]
coins1 = [Coin(r.x, r.y) for r in [
    pygame.Rect(390, 370, 1, 1), pygame.Rect(720, 390, 1, 1),
    pygame.Rect(1110, 270, 1, 1), pygame.Rect(1420, 400, 1, 1),
    pygame.Rect(1820, 360, 1, 1), pygame.Rect(2230, 420, 1, 1),
    pygame.Rect(2620, 370, 1, 1), pygame.Rect(3020, 320, 1, 1),
]]
levels.append(build_level(gnd1, plat1, bricks1, pipes1, enemies1, coins1, flag_x=4600))

# ── LEVEL 2 ── Overworld, more platforms ───────────────────────────────────
gnd2 = make_ground(0, 5500, underground=False)
plat2 = (
    make_platform(300, 450, 160) + make_platform(550, 390, 160) +
    make_platform(900, 350, 200) + make_platform(1250, 300, 180) +
    make_platform(1600, 430, 140) + make_platform(1900, 380, 200) +
    make_platform(2300, 320, 200) + make_platform(2700, 370, 180) +
    make_platform(3100, 300, 220) + make_platform(3600, 350, 200) +
    make_platform(4100, 420, 180) + make_platform(4400, 370, 160)
)
bricks2 = (
    make_brick(560, 300, 64) + make_brick(624, 300, 64) +
    make_brick(1300, 220, 64) + make_brick(1364, 220, 64) +
    make_brick(2350, 240, 64)
)
pipes2 = [Pipe(450, 456, 80), Pipe(1000, 456, 96), Pipe(2100, 456, 80), Pipe(3400, 456, 112)]
enemies2 = [Enemy(650, 490), Enemy(1100, 490), Enemy(1700, 490), Enemy(2000, 490),
            Enemy(2600, 490), Enemy(3000, 490), Enemy(3700, 490), Enemy(4200, 490)]
coins2 = [Coin(r.x, r.y) for r in [
    pygame.Rect(560, 280, 1, 1), pygame.Rect(920, 330, 1, 1),
    pygame.Rect(1270, 280, 1, 1), pygame.Rect(1920, 360, 1, 1),
    pygame.Rect(2320, 300, 1, 1), pygame.Rect(2720, 350, 1, 1),
    pygame.Rect(3120, 280, 1, 1), pygame.Rect(4120, 400, 1, 1),
]]
levels.append(build_level(gnd2, plat2, bricks2, pipes2, enemies2, coins2, flag_x=5100))

# ── LEVEL 3 ── Underground ──────────────────────────────────────────────────
gnd3 = make_ground(0, 5000, underground=True)
# ceiling
ceiling3 = [('brick', pygame.Rect(i, 0, 64, 32), True) for i in range(0, 5000, 64)]
plat3 = (
    make_platform(400, 450, 200) + make_platform(800, 390, 180) +
    make_platform(1300, 330, 220) + make_platform(1800, 280, 200) +
    make_platform(2300, 350, 180) + make_platform(2800, 300, 240) +
    make_platform(3300, 380, 200) + make_platform(3800, 330, 200)
)
bricks3 = (
    make_brick(420, 360, 128, 32) + make_brick(820, 300, 128, 32) +
    make_brick(1600, 260, 64) + make_brick(2400, 280, 128, 32)
)
pipes3 = [Pipe(600, 456, 80), Pipe(1500, 456, 96), Pipe(2600, 456, 80), Pipe(3600, 456, 80)]
enemies3 = [Enemy(700, 490), Enemy(1100, 490), Enemy(1600, 490),
            Enemy(2200, 490), Enemy(2900, 490), Enemy(3400, 490), Enemy(3900, 490)]
coins3 = [Coin(r.x, r.y) for r in [
    pygame.Rect(430, 340, 1, 1), pygame.Rect(840, 280, 1, 1),
    pygame.Rect(1320, 310, 1, 1), pygame.Rect(1830, 260, 1, 1),
    pygame.Rect(2330, 330, 1, 1), pygame.Rect(2830, 280, 1, 1),
    pygame.Rect(3320, 360, 1, 1), pygame.Rect(3830, 310, 1, 1),
]]
levels.append(build_level(gnd3, plat3, bricks3 + ceiling3, pipes3, enemies3, coins3,
                          flag_x=4600, underground=True))

# ── LEVEL 4 ── Underground harder ───────────────────────────────────────────
gnd4 = make_ground(0, 6000, underground=True)
ceiling4 = [('brick', pygame.Rect(i, 0, 64, 32), True) for i in range(0, 6000, 64)]
plat4 = (
    make_platform(350, 460, 140) + make_platform(600, 400, 140) +
    make_platform(900, 340, 160) + make_platform(1200, 280, 180) +
    make_platform(1600, 380, 140) + make_platform(1950, 320, 160) +
    make_platform(2350, 260, 200) + make_platform(2800, 350, 160) +
    make_platform(3200, 280, 200) + make_platform(3700, 350, 160) +
    make_platform(4200, 300, 200) + make_platform(4700, 380, 160)
)
bricks4 = (
    make_brick(370, 380, 64) + make_brick(620, 320, 64) +
    make_brick(930, 260, 64) + make_brick(1240, 200, 64) +
    make_brick(2380, 180, 128, 32) + make_brick(3230, 200, 128, 32)
)
pipes4 = [Pipe(500, 456, 80), Pipe(1400, 456, 96), Pipe(2200, 456, 112),
          Pipe(3100, 456, 80), Pipe(4500, 456, 96)]
enemies4 = [Enemy(650, 490), Enemy(1000, 490), Enemy(1500, 490), Enemy(2000, 490),
            Enemy(2500, 490), Enemy(3000, 490), Enemy(3600, 490),
            Enemy(4100, 490), Enemy(4800, 490)]
coins4 = [Coin(r.x, r.y) for r in [
    pygame.Rect(370, 360, 1, 1), pygame.Rect(620, 300, 1, 1),
    pygame.Rect(930, 240, 1, 1), pygame.Rect(1220, 260, 1, 1),
    pygame.Rect(1630, 360, 1, 1), pygame.Rect(2370, 240, 1, 1),
    pygame.Rect(2830, 330, 1, 1), pygame.Rect(3220, 260, 1, 1),
    pygame.Rect(4230, 280, 1, 1), pygame.Rect(4730, 360, 1, 1),
]]
levels.append(build_level(gnd4, plat4, bricks4 + ceiling4, pipes4, enemies4, coins4,
                          flag_x=5600, underground=True))


# ─── RESET ───────────────────────────────────────────────────────────────────
def reset_game():
    global player, current_level, camera_x, score_total
    player = Player(100, 400)
    current_level = 0
    camera_x = 0
    score_total = 0
    # Respawn all enemies & coins
    for lvl in levels:
        for e in lvl['enemies']:
            e.alive = True
            e.squish_timer = 0
        for c in lvl['coins']:
            c.collected = False


reset_game()

# ─── CLOUDS ──────────────────────────────────────────────────────────────────
clouds = [(i * 450 + 200, 80 + (i % 3) * 40) for i in range(20)]

# ─── STARS (underground) ─────────────────────────────────────────────────────
import random
random.seed(42)
stars = [(random.randint(0, 5000), random.randint(0, HEIGHT)) for _ in range(200)]

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
running = True

while running:
    clock.tick(FPS)

    lvl = levels[current_level]
    blocks_rects = lvl['rects']
    enemies = lvl['enemies']
    coins = lvl['coins']
    pipes = lvl['pipes']
    underground = lvl['underground']
    flag_x = lvl['flag_x']

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                player.request_jump()

            if player.dead and event.key == pygame.K_RETURN:
                reset_game()

    # ── UPDATE ──
    if not player.dead:
        player.move(blocks_rects)

        # CAMERA (smooth follow)
        target_cam = player.rect.centerx - WIDTH // 2
        camera_x += (target_cam - camera_x) * 0.15
        camera_x = max(0, camera_x)

        # ENEMY UPDATE
        for enemy in enemies:
            if enemy.alive:
                enemy.move(blocks_rects)

                if player.rect.colliderect(enemy.rect):
                    if player.vel_y > 0 and player.rect.bottom - enemy.rect.top < 20:
                        enemy.alive = False
                        enemy.squish_timer = 30
                        player.vel_y = -10
                        player.score += 100
                    else:
                        player.dead = True

        # COIN COLLECT
        for coin in coins:
            if not coin.collected and player.rect.colliderect(coin.rect):
                coin.collected = True
                player.score += 50

        # NEXT LEVEL
        if player.rect.x > flag_x:
            current_level += 1
            if current_level >= len(levels):
                current_level = 0
            player.rect.x = 100
            player.rect.y = 400
            player.vel_x = 0
            player.vel_y = 0
            camera_x = 0

    # ── DRAW ──
    draw_sky_gradient(screen, underground)

    if underground:
        # Stars
        for sx, sy in stars:
            rx = sx - int(camera_x * 0.3) % WIDTH
            if random.random() < 0.01:
                pass
            pygame.draw.circle(screen, WHITE, (rx % WIDTH, sy), 1)
    else:
        # Clouds (parallax)
        for cx, cy in clouds:
            rx = cx - int(camera_x * 0.4)
            if -100 < rx < WIDTH + 100:
                draw_cloud(screen, cx, cy, int(camera_x * 0.4))

        # Distant hills
        for hx in range(0, 6000, 400):
            rx = hx - int(camera_x * 0.6)
            if -200 < rx < WIDTH + 200:
                pygame.draw.ellipse(screen, (80, 160, 60), (rx, 450, 240, 120))

    # DRAW BLOCKS
    for btype, brect, bunder in lvl['blocks']:
        rx = brect.x - int(camera_x)
        if -80 < rx < WIDTH + 80:
            if btype == 'ground':
                draw_ground_block(screen, rx, brect.y, brect.width, brect.height, bunder)
            elif btype == 'brick':
                draw_brick_block(screen, rx, brect.y, brect.width, brect.height)
            elif btype == 'platform':
                draw_platform(screen, rx, brect.y, brect.width, brect.height)

    # DRAW PIPES
    for pipe in pipes:
        if -60 < pipe.rect.x - int(camera_x) < WIDTH + 60:
            pipe.draw(screen, int(camera_x))

    # DRAW FLAG
    if not underground:
        draw_flag(screen, flag_x, 236, int(camera_x))

    # DRAW COINS
    for coin in coins:
        if not coin.collected:
            rx = coin.rect.x - int(camera_x)
            if -40 < rx < WIDTH + 40:
                coin.draw(screen, int(camera_x))

    # DRAW ENEMIES
    for enemy in enemies:
        rx = enemy.rect.x - int(camera_x)
        if -60 < rx < WIDTH + 60:
            enemy.draw(screen, int(camera_x))

    # DRAW PLAYER
    player.draw(screen, int(camera_x))

    # HUD
    hud_surf = pygame.Surface((WIDTH, 44), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 120))
    screen.blit(hud_surf, (0, 0))

    lvl_text = font_small.render(f"LEVEL {current_level + 1}", True, WHITE)
    score_text = font_small.render(f"SCORE: {player.score}", True, COIN_YELLOW)
    ctrl_text = font_small.render("A/D or ←/→ | SPACE/↑ = Jump", True, (200, 200, 200))

    screen.blit(lvl_text, (20, 12))
    screen.blit(score_text, (200, 12))
    screen.blit(ctrl_text, (WIDTH - ctrl_text.get_width() - 20, 12))

    # GAME OVER
    if player.dead:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        go_text = font_big.render("GAME OVER", True, RED)
        restart_text = font_med.render("Press ENTER to restart", True, WHITE)
        score_final = font_med.render(f"Score: {player.score}", True, COIN_YELLOW)

        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(score_final, (WIDTH // 2 - score_final.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.update()
