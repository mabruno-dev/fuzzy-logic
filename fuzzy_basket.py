import pygame
import random
import math
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =============================================================================
# 1. LÓGICA FUZZY AVANÇADA
# =============================================================================

distancia_universe = np.arange(0, 26, 1)
angulo_universe = np.arange(0, 91, 1)
forca_universe = np.arange(0, 31, 1)
chance_universe = np.arange(0, 101, 1)

distancia = ctrl.Antecedent(distancia_universe, 'distancia')
angulo = ctrl.Antecedent(angulo_universe, 'angulo')
forca = ctrl.Antecedent(forca_universe, 'forca')
chance = ctrl.Consequent(chance_universe, 'chance')

distancia['muito_curta'] = fuzz.trimf(distancia.universe, [0, 1, 4])
distancia['curta_ideal'] = fuzz.trimf(distancia.universe, [3, 6, 9])
distancia['media'] = fuzz.trimf(distancia.universe, [8, 13, 17])
distancia['longa'] = fuzz.trimf(distancia.universe, [16, 20, 25])

angulo['baixo'] = fuzz.trimf(angulo.universe, [0, 20, 35])
angulo['medio_ideal'] = fuzz.trimf(angulo.universe, [30, 48, 60])
angulo['alto'] = fuzz.trimf(angulo.universe, [55, 75, 90])

forca['fraca'] = fuzz.trimf(forca.universe, [0, 5, 12])
forca['ideal'] = fuzz.gaussmf(forca.universe, mean=18, sigma=4)
forca['forte'] = fuzz.trimf(forca.universe, [20, 25, 30])

chance['minima'] = fuzz.trimf(chance.universe, [0, 0, 25])
chance['baixa'] = fuzz.trimf(chance.universe, [15, 30, 45])
chance['media'] = fuzz.trimf(chance.universe, [40, 55, 70])
chance['alta'] = fuzz.trimf(chance.universe, [65, 80, 90])
chance['altissima'] = fuzz.trimf(chance.universe, [85, 100, 100])

regras = [
    ctrl.Rule(distancia['curta_ideal'] & angulo['medio_ideal'] & forca['ideal'], chance['altissima']),
    ctrl.Rule(distancia['muito_curta'] & angulo['baixo'] & forca['fraca'], chance['altissima']),
    ctrl.Rule(distancia['curta_ideal'] & angulo['medio_ideal'] & forca['fraca'], chance['alta']),
    ctrl.Rule(distancia['media'] & angulo['medio_ideal'] & forca['ideal'], chance['alta']),
    ctrl.Rule(distancia['longa'] & angulo['medio_ideal'] & forca['forte'], chance['media']),
    ctrl.Rule(distancia['media'] & angulo['medio_ideal'] & forca['forte'], chance['media']),
    ctrl.Rule(forca['forte'] & angulo['baixo'], chance['baixa']),
    ctrl.Rule(distancia['longa'] & forca['ideal'], chance['baixa']),
    ctrl.Rule(angulo['alto'], chance['baixa']),
    ctrl.Rule(distancia['longa'] & forca['fraca'], chance['minima']),
    ctrl.Rule(forca['forte'] & distancia['muito_curta'], chance['minima'])
]

sistema_chance = ctrl.ControlSystem(regras)


# =============================================================================
# 2. CONFIGURAÇÃO GRÁFICA
# =============================================================================

pygame.init()
WIDTH, HEIGHT = 1024, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robô Basqueteiro v5.1 - Ajuste Fino")

SKY_TOP, SKY_BOTTOM = (23, 38, 63), (62, 83, 120)
BUILDING_COLOR = (18, 28, 48)
COURT_COLOR, COURT_LINES = (186, 93, 54), (255, 255, 255)
BALL_COLOR, BALL_HIGHLIGHT = (224, 86, 34), (255, 136, 54)
TRAIL_COLOR = (255, 215, 0)
ROBOT_BODY, ROBOT_ACCENT, ROBOT_EYE = (128, 140, 158), (214, 93, 79), (255, 215, 0)
BASKET_POLE, BASKET_BOARD, BASKET_RIM = (80, 80, 80), (150, 150, 150, 180), (214, 93, 79)
SCOREBOARD_BG, SCOREBOARD_TEXT, SCOREBOARD_HEADER = (10, 20, 35, 200), (230, 230, 230), (255, 215, 0)

try:
    UI_FONT_BODY = pygame.font.SysFont('Consolas', 20)
    UI_FONT_HEADER = pygame.font.SysFont('Consolas', 24, bold=True)
    RESULT_FONT = pygame.font.SysFont('Impact', 100)
except:
    UI_FONT_BODY = pygame.font.SysFont('Arial', 18)
    UI_FONT_HEADER = pygame.font.SysFont('Arial', 22, bold=True)
    RESULT_FONT = pygame.font.SysFont('Arial', 90, bold=True)

clock = pygame.time.Clock()
ROBOT_Y = HEIGHT - 130
BASKET_X, BASKET_Y = WIDTH - 100, HEIGHT - 350
PIXELS_POR_METRO = (WIDTH * 0.7) / 22

BUILDING_SHAPES = []

# =============================================================================
# 3. FUNÇÕES DE DESENHO E ANIMAÇÃO (AJUSTADAS)
# =============================================================================

def gerar_cenario_inicial():
    BUILDING_SHAPES.clear()
    for _ in range(25):
        x = random.randint(-50, WIDTH)
        h = random.randint(50, 350)
        w = random.randint(30, 80)
        building_rect = pygame.Rect(x, HEIGHT - h - 80, w, h)
        BUILDING_SHAPES.append(building_rect)

def desenhar_fundo():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio)
        g = int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio)
        b = int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio)
        pygame.draw.line(WIN, (r, g, b), (0, y), (WIDTH, y))
    
    for rect in BUILDING_SHAPES:
        pygame.draw.rect(WIN, BUILDING_COLOR, rect)

def desenhar_quadra():
    pygame.draw.rect(WIN, COURT_COLOR, (0, HEIGHT - 80, WIDTH, 80))
    for i in range(0, WIDTH, 15):
        pygame.draw.line(WIN, (0,0,0,20), (i, HEIGHT - 80), (i, HEIGHT))

def desenhar_cesta(net_sway=0):
    pygame.draw.rect(WIN, BASKET_POLE, (BASKET_X, BASKET_Y, 15, HEIGHT - BASKET_Y - 80))
    board_surface = pygame.Surface((10, 100), pygame.SRCALPHA)
    board_surface.fill(BASKET_BOARD)
    WIN.blit(board_surface, (BASKET_X, BASKET_Y - 20))
    pygame.draw.rect(WIN, (255,255,255), (BASKET_X + 2, BASKET_Y + 20, 6, 40), 2)
    pygame.draw.ellipse(WIN, BASKET_RIM, (BASKET_X - 65, BASKET_Y + 60, 80, 25), 6)
    for i in range(8):
        start_x = BASKET_X - 60 + i * 10
        end_x = start_x + net_sway * (i-4)
        pygame.draw.line(WIN, COURT_LINES, (start_x, BASKET_Y + 72), (end_x, BASKET_Y + 120), 2)

def desenhar_robo(pos_x, ang_braco):
    pygame.draw.rect(WIN, (40,40,40), (pos_x-5, ROBOT_Y-5, 50, 80), border_radius=8)
    pygame.draw.rect(WIN, ROBOT_BODY, (pos_x, ROBOT_Y, 40, 70), border_radius=8)
    pygame.draw.rect(WIN, ROBOT_BODY, (pos_x + 5, ROBOT_Y - 30, 30, 30), border_radius=5)
    pygame.draw.rect(WIN, ROBOT_EYE, (pos_x + 10, ROBOT_Y - 22, 20, 8), border_radius=3)
    arm_surface = pygame.Surface((15, 40), pygame.SRCALPHA)
    arm_surface.fill(ROBOT_ACCENT)
    rotated_arm = pygame.transform.rotate(arm_surface, ang_braco)
    WIN.blit(rotated_arm, (pos_x + 10, ROBOT_Y - 10))

def desenhar_placar(dist, ang, forc, chance):
    panel = pygame.Surface((280, 160), pygame.SRCALPHA)
    panel.fill(SCOREBOARD_BG)
    pygame.draw.rect(panel, SCOREBOARD_HEADER, (0, 0, 280, 35))
    header_text = UI_FONT_HEADER.render("BASKET BOT", True, (10,20,35))
    panel.blit(header_text, (15, 5))
    
    dist_txt = UI_FONT_BODY.render(f"Distancia: {dist:>5.1f}m", True, SCOREBOARD_TEXT)
    ang_txt = UI_FONT_BODY.render(f"Angulo   : {ang:>5.1f}°", True, SCOREBOARD_TEXT)
    forc_txt = UI_FONT_BODY.render(f"Forca    : {forc:>5.1f}", True, SCOREBOARD_TEXT)
    chance_txt = UI_FONT_BODY.render(f"Chance   : {chance:>5.1f}%", True, SCOREBOARD_TEXT)
    
    panel.blit(dist_txt, (15, 50))
    panel.blit(ang_txt, (15, 75))
    panel.blit(forc_txt, (15, 100))
    panel.blit(chance_txt, (15, 125))
    WIN.blit(panel, (15, 15))

def desenhar_bola(x, y):
    shadow_size = int(20 * (1 - (y / (HEIGHT-80)) * 0.5))
    shadow_alpha = int(100 * (1 - (y / (HEIGHT-80)) * 0.5))
    if shadow_size > 0:
        shadow_surface = pygame.Surface((shadow_size*2, shadow_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0,0,0,shadow_alpha), (0,0,shadow_size*2, shadow_size))
        WIN.blit(shadow_surface, (x - shadow_size, HEIGHT-80))
    pygame.draw.circle(WIN, (40,40,40), (int(x), int(y)), 13)
    pygame.draw.circle(WIN, BALL_COLOR, (int(x), int(y)), 12)
    pygame.draw.circle(WIN, BALL_HIGHLIGHT, (int(x-3), int(y-3)), 4)

def exibir_mensagem_resultado(acertou):
    msg, color = ("CESTA!", (137, 214, 131)) if acertou else ("ERROU!", (214, 93, 79))
    texto = RESULT_FONT.render(msg, True, color)
    sombra = RESULT_FONT.render(msg, True, (0,0,0,100))
    rect = texto.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    WIN.blit(sombra, (rect.x + 5, rect.y + 5))
    WIN.blit(texto, rect)
    pygame.display.update(rect)
    pygame.time.delay(1500)

def simular_arremesso(d, a, f):
    simulador_local = ctrl.ControlSystemSimulation(sistema_chance)
    simulador_local.input['distancia'], simulador_local.input['angulo'], simulador_local.input['forca'] = d, a, f
    simulador_local.compute()
    chance_acerto = simulador_local.output.get('chance', 0)
    if chance_acerto < 25: acertou = False
    elif chance_acerto > 90: acertou = True
    else: acertou = random.uniform(0, 100) <= chance_acerto
    return chance_acerto, acertou

def anima_bola(f, a, acertou, info_ui, robot_pos_x):
    vel = 8 + (f * 0.7)
    angulo_rad = math.radians(a)
    x, y = robot_pos_x + 20, ROBOT_Y
    g = 0.3
    trajetoria = []
    cesta_centro_x, cesta_centro_y = BASKET_X - 25, BASKET_Y + 72
    
    if acertou:
        target_x, target_y = cesta_centro_x, cesta_centro_y
        try:
            t_estimado = (target_x - x) / (vel * math.cos(angulo_rad))
            if t_estimado <= 0: t_estimado = 1.5
        except ZeroDivisionError:
            t_estimado = 1.5
        vx = (target_x - x) / t_estimado
        vy = (target_y - y - 0.5 * g * t_estimado**2) / t_estimado
    else:
        vx = vel * math.cos(angulo_rad)
        vy = -vel * math.sin(angulo_rad)
    
    rodando_animacao = True
    net_animation_timer = 0
    while rodando_animacao:
        desenhar_fundo()
        desenhar_quadra()
        
        net_sway = 0
        if net_animation_timer > 0:
            net_sway = math.sin(net_animation_timer * math.pi) * 5
            net_animation_timer -= 0.05
        desenhar_cesta(net_sway)
        
        desenhar_robo(robot_pos_x, a if x < robot_pos_x + 50 else 0)
        desenhar_placar(info_ui['dist'], info_ui['ang'], info_ui['forc'], info_ui['chance'])
        
        vy += g
        x += vx
        y += vy
        trajetoria.append((int(x), int(y)))
        
        if len(trajetoria) > 1:
            pygame.draw.lines(WIN, TRAIL_COLOR, False, trajetoria, 2)

        desenhar_bola(x, y)
        
        pygame.display.update()
        clock.tick(60)
        
        if acertou and net_animation_timer <= 0 and cesta_centro_x - 10 < x < cesta_centro_x + 10 and cesta_centro_y - 10 < y < cesta_centro_y + 10:
            net_animation_timer = 1.0

        if y > HEIGHT - 80 or x > WIDTH + 20 or x < -20:
            rodando_animacao = False

# =============================================================================
# 4. LOOP PRINCIPAL DO JOGO
# =============================================================================

def main():
    rodando = True
    dist_metros, angulo_graus, forca_aplicada, chance_calculada = 8, 45, 15, 50
    gerar_cenario_inicial()

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        robot_x_pixel = BASKET_X - (dist_metros * PIXELS_POR_METRO) - 150
        desenhar_fundo()
        desenhar_quadra()
        desenhar_cesta()
        desenhar_robo(robot_x_pixel, angulo_graus)
        desenhar_placar(dist_metros, angulo_graus, forca_aplicada, chance_calculada)
        pygame.display.update()
        pygame.time.delay(2000)

        dist_metros = random.uniform(1, 22)
        angulo_graus = random.uniform(25, 75)
        forca_aplicada = random.uniform(5, 30)
        robot_x_pixel = BASKET_X - (dist_metros * PIXELS_POR_METRO) - 150

        chance_calculada, acertou = simular_arremesso(dist_metros, angulo_graus, forca_aplicada)
        print(f"D:{dist_metros:.1f}m A:{angulo_graus:.1f}° F:{forca_aplicada:.1f} -> Chance:{chance_calculada:.1f}% -> {'CESTA' if acertou else 'ERROU'}")
        
        info_ui = {'dist': dist_metros, 'ang': angulo_graus, 'forc': forca_aplicada, 'chance': chance_calculada}
        anima_bola(forca_aplicada, angulo_graus, acertou, info_ui, robot_x_pixel)
        exibir_mensagem_resultado(acertou)

    pygame.quit()

if __name__ == "__main__":
    main()