import pygame
import sys
import math
import os
import random
from inequality_matrix import InequalityMatrix

# --- vensterpositie instellen
os.environ['SDL_VIDEO_WINDOW_POS'] = "60,60"
pygame.init()

# --- basisresolutie
BASE_W, BASE_H = 2400, 1200
base_surface = pygame.Surface((BASE_W, BASE_H))

# --- schermgrootte bepalen en canvas schalen indien nodig
info = pygame.display.Info()
screen_w, screen_h = info.current_w, info.current_h
scale_factor = 0.9 * min(screen_w / BASE_W, screen_h / BASE_H, 1)  # max 1
screen = pygame.display.set_mode(
    (int(BASE_W * scale_factor), int(BASE_H * scale_factor)), pygame.RESIZABLE)
pygame.display.set_caption("Point Descriptor Precedence - Interactive Viewer")

# --- limieten
LEFT_LIMIT = 0
RIGHT_LIMIT = 1200
MARGIN = 50
CIRCLE_RADIUS = 8
HIT_RADIUS = 16

# --- kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_RGBA = (255, 0, 0, 120)
DARK_BLUE = (0, 120, 200)
ORANGE = (255, 165, 0)

# pijlpunt sets (k en l)
arrow_sets = [
    [[200, BASE_H // 3 - 60], [450, BASE_H // 3 + 20], [700, BASE_H // 3 - 40]],  # k
    [[240, 2 * BASE_H // 3 + 40], [500, 2 * BASE_H // 3 - 80], [720, 2 * BASE_H // 3 + 60]]  # l
]
dragging = [[False, False, False], [False, False, False]]

# knop instellingen
button_rect = pygame.Rect(RIGHT_LIMIT + 1000, 30, 120, 40)
button_color = (200, 200, 200)
button_hover = (170, 170, 170)
start_distance_factor = 1.45

clock = pygame.time.Clock()
placed_dots = []  # lijst van ((x,y), color)

xoffset = RIGHT_LIMIT + 30
yoffset = 100
xoffset2 = RIGHT_LIMIT + 30
yoffset2 = 600
xoffset_new = xoffset + 6*66 + 120
yoffset_new = yoffset

def clamp_position(x, y):
    x = max(LEFT_LIMIT + MARGIN + HIT_RADIUS,
            min(RIGHT_LIMIT - MARGIN - HIT_RADIUS, x))
    y = max(MARGIN + HIT_RADIUS,
            min(BASE_H - MARGIN - HIT_RADIUS, y))
    return [x, y]

def draw_circle_with_highlight(surface, pos, selected, label, font):
    pygame.draw.circle(surface, WHITE, pos, CIRCLE_RADIUS)
    pygame.draw.circle(surface, BLACK, pos, CIRCLE_RADIUS, 1)
    if selected:
        highlight_surface = pygame.Surface((CIRCLE_RADIUS*2, CIRCLE_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, HIGHLIGHT_RGBA, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)
        surface.blit(highlight_surface, (pos[0]-CIRCLE_RADIUS, pos[1]-CIRCLE_RADIUS))
    text = font.render(str(label), True, BLACK)
    text_rect = text.get_rect(midbottom=(pos[0], pos[1] - CIRCLE_RADIUS - 14))
    surface.blit(text, text_rect)

def draw_arrow(surface, p1, p2):
    pygame.draw.line(surface, BLACK, p1, p2, 2)
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    angle = math.atan2(dy, dx)
    length = 12
    wing = math.radians(25)
    left = (p2[0] - length*math.cos(angle-wing),
            p2[1] - length*math.sin(angle-wing))
    right = (p2[0] - length*math.cos(angle+wing),
             p2[1] - length*math.sin(angle+wing))
    pygame.draw.polygon(surface, BLACK, [p2, left, right])

def draw_dashed_line(surface, color, start, end, width=2, dash_length=12, gap_length=8):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    angle = math.atan2(dy, dx)
    step = dash_length + gap_length
    i = 0
    while i < length:
        x1 = start[0] + math.cos(angle) * i
        y1 = start[1] + math.sin(angle) * i
        i2 = min(i + dash_length, length)
        x2 = start[0] + math.cos(angle) * i2
        y2 = start[1] + math.sin(angle) * i2
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)
        i += step

def positions_to_valuelist(positions, axis='x'):
    n = len(positions)
    ai = 0 if axis == 'x' else 1
    mat = [[None]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i][j] = None
            else:
                a = positions[i][ai]
                b = positions[j][ai]
                mat[i][j] = 1 if a < b else -1 if a > b else 0
    return mat

def draw_scene(temp_l2_prime=None):
    font = pygame.font.SysFont("Arial", 24)
    italicfont = pygame.font.SysFont("Arial", 28, italic=True)
    bigfont = pygame.font.SysFont("Arial", 40, bold=True)

    base_surface.fill(WHITE)
    #pygame.draw.line(base_surface, BLACK, (RIGHT_LIMIT, 0), (RIGHT_LIMIT, BASE_H), 3)

    title = bigfont.render("Point Descriptor Precedence - inverse", True, BLACK)
    base_surface.blit(title, (45, 20))

    mx, my = pygame.mouse.get_pos()
    sx, sy = screen.get_size()
    mx_scaled = mx * BASE_W / sx
    my_scaled = my * BASE_H / sy
    current_color = button_hover if button_rect.collidepoint(mx_scaled, my_scaled) else button_color
    pygame.draw.rect(base_surface, current_color, button_rect, border_radius=6)
    btn_font = pygame.font.SysFont("Arial", 24)
    btn_text = btn_font.render("start", True, BLACK)
    text_rect = btn_text.get_rect(center=button_rect.center)
    base_surface.blit(btn_text, text_rect)

    labels = [italicfont.render("k", True, BLACK),
              italicfont.render("l", True, BLACK)]
    for si, nodes in enumerate(arrow_sets):
        base_surface.blit(labels[si], (nodes[0][0]-15, nodes[0][1]-50))
        draw_arrow(base_surface, nodes[0], nodes[1])
        draw_arrow(base_surface, nodes[1], nodes[2])
        for ni, pos in enumerate(nodes):
            draw_circle_with_highlight(base_surface, pos, dragging[si][ni], ni+1, font)

    k = arrow_sets[0]
    l = arrow_sets[1]
    l1, l2, l3 = l[0], l[1], l[2]
    d12 = math.dist(l1, l2)
    d23 = math.dist(l2, l3)
    default_dist = max(d12, d23) * start_distance_factor
    diag = default_dist / math.sqrt(2)
    default_l2_prime = [int(l2[0] + diag), int(l2[1] + diag)]
    l2_prime_to_use = temp_l2_prime if temp_l2_prime else default_l2_prime

    pygame.draw.circle(base_surface, DARK_BLUE, l2_prime_to_use, CIRCLE_RADIUS)
    pygame.draw.circle(base_surface, BLACK, l2_prime_to_use, CIRCLE_RADIUS, 1)
    draw_dashed_line(base_surface, DARK_BLUE, l1, l2_prime_to_use, width=3)
    draw_dashed_line(base_surface, DARK_BLUE, l2_prime_to_use, l3, width=3)

    positions = [k[0], l[0], k[1], l[1], k[2], l[2]]
    positions_l2prime = positions.copy()
    positions_l2prime[3] = l2_prime_to_use

    valuelist_x_orig = positions_to_valuelist(positions, axis='x')
    valuelist_x_l2prime = positions_to_valuelist(positions_l2prime, axis='x')
    valuelist_y_orig = positions_to_valuelist(positions, axis='y')
    valuelist_y_l2prime = positions_to_valuelist(positions_l2prime, axis='y')

    labels_text = ["k|t_1","l|t_1","k|t_2","l|t_2","k|t_3","l|t_3"]

    matrix_top_left = InequalityMatrix("d_1", 66, labels_text, valuelist_x_orig, pos=(xoffset, yoffset))
    matrix_top_right = InequalityMatrix("d_1", 66, labels_text, valuelist_x_l2prime, pos=(xoffset_new, yoffset_new))
    matrix_bottom_left = InequalityMatrix("d_2", 66, labels_text, valuelist_y_orig, pos=(xoffset2, yoffset2))
    matrix_bottom_right = InequalityMatrix("d_2", 66, labels_text, valuelist_y_l2prime, pos=(xoffset_new, yoffset_new+500))

    matrix_top_left.draw(base_surface)
    matrix_top_right.draw(base_surface)
    matrix_bottom_left.draw(base_surface)
    matrix_bottom_right.draw(base_surface)

    for (px, py), color in placed_dots:
        pygame.draw.circle(base_surface, color, (int(px), int(py)), 6)

    scaled = pygame.transform.smoothscale(base_surface, screen.get_size())
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            sx, sy = screen.get_size()
            mx = mx * BASE_W / sx
            my = my * BASE_H / sy
            if button_rect.collidepoint(mx, my):
                k = arrow_sets[0]
                l = arrow_sets[1]
                l1, l2, l3 = l[0], l[1], l[2]
                d12 = math.dist(l1, l2)
                d23 = math.dist(l2, l3)
                base_start_distance = max(d12, d23) * start_distance_factor

                for _ in range(100):  # 100 keer opnieuw
                    angle = random.uniform(0, 2*math.pi)
                    start_distance = base_start_distance
                    while True:
                        dx = math.cos(angle) * start_distance
                        dy = math.sin(angle) * start_distance
                        l2_prime = [int(l2[0] + dx), int(l2[1] + dy)]
                        draw_scene(temp_l2_prime=l2_prime)

                        positions = [k[0], l[0], k[1], l[1], k[2], l[2]]
                        positions_l2prime = positions.copy()
                        positions_l2prime[3] = l2_prime

                        val_top_left = positions_to_valuelist(positions, axis='x')
                        val_top_right = positions_to_valuelist(positions_l2prime, axis='x')
                        val_bottom_left = positions_to_valuelist(positions, axis='y')
                        val_bottom_right = positions_to_valuelist(positions_l2prime, axis='y')

                        if val_top_left == val_top_right and val_bottom_left == val_bottom_right:
                            placed_dots.append((tuple(l2_prime), ORANGE))
                            draw_scene(temp_l2_prime=l2_prime)
                            print(True)
                            pygame.time.wait(50)
                            break
                        else:
                            placed_dots.append((tuple(l2_prime), BLACK))
                            draw_scene(temp_l2_prime=l2_prime)
                            pygame.time.wait(50)
                            start_distance *= 0.5
                    # hier gaat hij automatisch terug en kiest nieuwe hoek

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = [[False]*3 for _ in arrow_sets]

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            sx, sy = screen.get_size()
            mx = mx * BASE_W / sx
            my = my * BASE_H / sy
            for si in range(len(arrow_sets)):
                for ni in range(3):
                    if dragging[si][ni]:
                        arrow_sets[si][ni] = clamp_position(mx, my)

    draw_scene()
    clock.tick(60)

pygame.quit()
sys.exit()
