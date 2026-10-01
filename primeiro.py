import array
import json
import math
import os
import random
import pygame

# 1. INICIALIZAÇÃO (o áudio é iniciado antes, em mono, para os sons gerados por código)
FREQ_AUDIO = 22050
try:
    pygame.mixer.init(FREQ_AUDIO, -16, 1, 512, allowedchanges=0)
except Exception:
    pass
pygame.init()

# 2. TELA E JANELA
LARGURA, ALTURA = 1000, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Nave vs Inimigo")
relogio = pygame.time.Clock()

# 3. PALETA DE CORES (RGB)
PRETO = (15, 15, 20)
BRANCO = (240, 245, 255)
AZUL_ESCURO = (10, 45, 90)
CIANO = (80, 220, 255)
AZUL_CLARO = (170, 235, 255)
VERMELHO_CONTORNO = (196, 30, 61)
ROXO_INIMIGO = (145, 55, 220)
ROXO_ESCURO = (65, 20, 100)
ROXO_CLARO = (190, 100, 255)
VERDE_ALIEN = (90, 255, 150)
VERDE_ESCURO = (20, 120, 70)
LARANJA_FOGO = (255, 140, 20)
AMARELO_FOGO = (255, 220, 60)
AMARELO_TIRO = (255, 215, 0)
ROSA_TIRO = (255, 70, 110)
CINZA_BARRA = (40, 40, 50)
VERMELHO_ATRASO = (120, 25, 35)

# 4. FONTES
fonte_titulo = pygame.font.SysFont("Arial", 72, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 50)
fonte_media = pygame.font.SysFont("Arial", 40)
fonte = pygame.font.SysFont("Arial", 30)
fonte_pequena = pygame.font.SysFont("Arial", 22)
fonte_mini = pygame.font.SysFont("Arial", 16, bold=True)

# 5. ARQUIVOS DE SALVAMENTO (ficam na mesma pasta do script)
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ_RECORDE = os.path.join(PASTA, "recorde.txt")
ARQ_CONFIG = os.path.join(PASTA, "config.json")


def carregar_recorde():
    try:
        with open(ARQ_RECORDE) as f:
            return int(f.read().strip())
    except Exception:
        return 0


def salvar_recorde(valor):
    try:
        with open(ARQ_RECORDE, "w") as f:
            f.write(str(valor))
    except Exception:
        pass


cfg = {"volume": 7, "dificuldade": 1, "tiro_continuo": True}


def carregar_config():
    try:
        with open(ARQ_CONFIG) as f:
            dados = json.load(f)
        cfg["volume"] = max(0, min(10, int(dados.get("volume", 7))))
        cfg["dificuldade"] = max(0, min(2, int(dados.get("dificuldade", 1))))
        cfg["tiro_continuo"] = bool(dados.get("tiro_continuo", True))
    except Exception:
        pass


def salvar_config():
    try:
        with open(ARQ_CONFIG, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass


carregar_config()

# Dificuldades: (nome, multiplicadores)
DIFICULDADES = [
    ("Fácil",   {"dano": 0.6, "vel": 0.85, "tiro": 0.8, "chefe_hp": 0.8, "drop": 0.18}),
    ("Normal",  {"dano": 1.0, "vel": 1.0,  "tiro": 1.0, "chefe_hp": 1.0, "drop": 0.12}),
    ("Difícil", {"dano": 1.4, "vel": 1.2,  "tiro": 1.3, "chefe_hp": 1.3, "drop": 0.09}),
]


def dif():
    return DIFICULDADES[cfg["dificuldade"]][1]


# 6. FUNDO (imagem ou estrelas com rolagem)
try:
    fundo = pygame.image.load("Galaxie.jpg")
    fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))
    usa_imagem = True
except Exception:
    fundo = pygame.Surface((LARGURA, ALTURA))
    fundo.fill(PRETO)
    usa_imagem = False

estrelas = [
    [random.randint(0, LARGURA), random.randint(0, ALTURA),
     random.uniform(0.5, 3), random.randint(1, 2)]
    for _ in range(90)
]


def desenhar_fundo(animar=True):
    tela.blit(fundo, (0, 0))
    if not usa_imagem:
        for e in estrelas:
            if animar:
                e[1] += e[2]
                if e[1] > ALTURA:
                    e[0], e[1] = random.randint(0, LARGURA), 0
            cor = 90 + int(e[2] * 50)
            pygame.draw.rect(tela, (cor, cor, cor), (e[0], e[1], e[3], e[3]))


# 7. SONS (gerados por código, não precisa de arquivos)
SONS = {}
mudo = False


def gerar_som(f_ini, f_fim, dur, volume=0.3, tipo="quadrada"):
    n = int(FREQ_AUDIO * dur)
    buf = array.array("h")
    fase = 0.0
    for i in range(n):
        t = i / n
        f = f_ini + (f_fim - f_ini) * t
        fase += 2 * math.pi * f / FREQ_AUDIO
        if tipo == "ruido":
            v = random.uniform(-1, 1)
        elif tipo == "quadrada":
            v = 1.0 if math.sin(fase) >= 0 else -1.0
        else:
            v = math.sin(fase)
        buf.append(int(v * ((1 - t) ** 1.5) * volume * 32767))
    return pygame.mixer.Sound(buffer=buf.tobytes())


try:
    SONS["tiro"] = gerar_som(900, 300, 0.08, 0.10)
    SONS["explosao"] = gerar_som(0, 0, 0.30, 0.30, "ruido")
    SONS["dano"] = gerar_som(220, 60, 0.25, 0.30)
    SONS["powerup"] = gerar_som(400, 1100, 0.20, 0.25, "seno")
    SONS["acerto"] = gerar_som(300, 200, 0.05, 0.15)
    SONS["chefe"] = gerar_som(140, 70, 0.70, 0.30)
    SONS["tiro_chefe"] = gerar_som(500, 150, 0.12, 0.12)
    SONS["chefe_morre"] = gerar_som(0, 0, 0.90, 0.40, "ruido")
    SONS["fim"] = gerar_som(300, 50, 0.90, 0.30)
    SONS["menu"] = gerar_som(700, 800, 0.05, 0.15, "seno")
    SONS["selecionar"] = gerar_som(500, 900, 0.10, 0.20, "seno")
except Exception:
    SONS = {}


def tocar(nome):
    vol = cfg["volume"] / 10
    if mudo or vol == 0 or nome not in SONS:
        return
    SONS[nome].set_volume(vol)
    SONS[nome].play()


# 8. CONSTANTES DE JOGO
VIDA_MAX = 100
INVUL_FRAMES = 90          # invulnerabilidade depois de levar dano
COOLDOWN_TIRO = 12         # frames entre tiros ao segurar espaço
DURACAO_TRIPLO = 480       # 8 segundos a 60 fps
DURACAO_ESCUDO = 360       # 6 segundos
CHEFE_A_CADA = 5           # um chefe a cada 5 níveis
NOMES_CHEFE = ["DESTRUIDOR", "VÓRTICE", "CAÇADOR"]
CORES_CHEFE = [ROXO_INIMIGO, (190, 45, 70), (30, 190, 140)]


# 9. CLASSES
class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(AMARELO_TIRO)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.velocidade = -12

    def update(self):
        self.rect.y += self.velocidade
        self.rect.x += self.dx
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()


class TiroInimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, dano=10):
        super().__init__()
        self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, ROSA_TIRO, (0, 0, 8, 16))
        pygame.draw.ellipse(self.image, BRANCO, (2, 3, 4, 8))
        self.rect = self.image.get_rect(center=(x, y))
        self.fx, self.fy = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.dano = dano

    def update(self):
        self.fx += self.vx
        self.fy += self.vy
        self.rect.center = (int(self.fx), int(self.fy))
        if self.rect.top > ALTURA or self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()


class Particula:
    """Pedacinho de explosão."""

    def __init__(self, x, y, cores):
        self.x, self.y = x, y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.vida = random.randint(15, 30)
        self.cor = random.choice(cores)
        self.tam = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    def draw(self):
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.tam, self.tam))


class PowerUp:
    def __init__(self, x, y, tipo):
        self.tipo = tipo  # "vida", "triplo" ou "escudo"
        self.rect = pygame.Rect(0, 0, 26, 26)
        self.rect.center = (x, y)
        self.tempo = 0

    def update(self):
        self.tempo += 1
        self.rect.y += 3

    def draw(self):
        cx, cy = self.rect.center
        raio = int(13 + 2 * math.sin(self.tempo * 0.15))
        if self.tipo == "vida":
            pygame.draw.circle(tela, VERDE_ESCURO, (cx, cy), raio)
            pygame.draw.circle(tela, VERDE_ALIEN, (cx, cy), raio, 2)
            pygame.draw.rect(tela, BRANCO, (cx - 2, cy - 8, 4, 16))
            pygame.draw.rect(tela, BRANCO, (cx - 8, cy - 2, 16, 4))
        elif self.tipo == "triplo":
            pygame.draw.circle(tela, (110, 80, 10), (cx, cy), raio)
            pygame.draw.circle(tela, AMARELO_FOGO, (cx, cy), raio, 2)
            for dx in (-6, 0, 6):
                pygame.draw.rect(tela, AMARELO_FOGO, (cx + dx - 1, cy - 7, 3, 14))
        else:
            pygame.draw.circle(tela, (10, 70, 100), (cx, cy), raio)
            pygame.draw.circle(tela, CIANO, (cx, cy), raio, 2)
            escudo_pts = [(cx - 7, cy - 7), (cx + 7, cy - 7), (cx + 7, cy + 1),
                          (cx, cy + 9), (cx - 7, cy + 1)]
            pygame.draw.polygon(tela, BRANCO, escudo_pts, 2)


class Inimigo:
    def __init__(self, nivel):
        self.rect = pygame.Rect(0, 0, 60, 30)
        self.reiniciar(nivel)

    def reiniciar(self, nivel):
        self.rect.x = random.randint(0, LARGURA - 60)
        self.y = -30.0
        self.rect.y = int(self.y)
        self.vel = min(random.uniform(3, 4.5) + nivel * 0.4, 11) * dif()["vel"]
        self.zigzag = nivel >= 3 and random.random() < 0.4
        self.dir = random.choice([-1, 1])
        self.timer = random.randint(60, 160)

    def update(self, nivel):
        """Move o inimigo. Retorna True quando ele quer atirar."""
        self.y += self.vel
        self.rect.y = int(self.y)
        if self.zigzag:
            self.rect.x += self.dir * 3
            if self.rect.left <= 0 or self.rect.right >= LARGURA:
                self.dir *= -1
        self.timer -= 1
        if self.timer <= 0:
            self.timer = max(40, int((random.randint(80, 190) - nivel * 6) / dif()["tiro"]))
            return nivel >= 2 and 0 < self.rect.y < ALTURA - 250
        return False

    def draw(self):
        a = self.rect
        corpo = [(a.centerx, a.y), (a.x + 10, a.y + 8), (a.x + 10, a.bottom),
                 (a.right - 10, a.bottom), (a.right - 10, a.y + 8)]
        pygame.draw.polygon(tela, ROXO_INIMIGO, corpo)
        pygame.draw.polygon(tela, ROXO_ESCURO, corpo, width=2)
        pygame.draw.rect(tela, ROXO_CLARO, (a.x + 15, a.y + 7, 30, 18))
        pygame.draw.rect(tela, PRETO, (a.x + 15, a.y + 7, 30, 18), width=2)
        pygame.draw.rect(tela, VERDE_ALIEN, (a.x + 21, a.y + 12, 18, 8))
        pygame.draw.rect(tela, VERDE_ESCURO, (a.x + 21, a.y + 12, 18, 2))
        pygame.draw.rect(tela, VERDE_ALIEN, (a.x + 14, a.y, 6, 5))
        pygame.draw.rect(tela, VERDE_ALIEN, (a.right - 20, a.y, 6, 5))
        pygame.draw.rect(tela, VERDE_ESCURO, (a.x + 14, a.bottom - 4, 5, 5))
        pygame.draw.rect(tela, VERDE_ESCURO, (a.right - 19, a.bottom - 4, 5, 5))


class Chefe:
    """Três tipos: 0 = Destruidor (leque), 1 = Vórtice (varredura), 2 = Caçador (mira em você)."""

    TAMANHOS = [(180, 80), (140, 100), (150, 70)]

    def __init__(self, nivel, tipo):
        self.tipo = tipo
        self.nome = NOMES_CHEFE[tipo]
        w, h = self.TAMANHOS[tipo]
        self.rect = pygame.Rect(LARGURA // 2 - w // 2, -h - 20, w, h)
        self.vida_max = int((30 + nivel * 6) * dif()["chefe_hp"])
        self.vida = self.vida_max
        self.dir = 1
        self.timer = 90
        self.t = 0
        self.entrando = True
        self.flash = 0
        self.olhar = 0

    def fase2(self):
        return self.vida <= self.vida_max // 2

    def update(self, alvo):
        """Move o chefe e devolve a lista de tiros que ele disparou neste frame."""
        self.flash = max(0, self.flash - 1)
        r = self.rect
        if self.entrando:
            r.y += 2
            if r.y >= 60:
                self.entrando = False
            return []

        self.t += 1
        f2 = self.fase2()
        tiros = []

        if self.tipo == 0:  # DESTRUIDOR: vai e volta e solta um leque de tiros
            r.x += self.dir * (4 if f2 else 3)
            if r.left <= 0 or r.right >= LARGURA:
                self.dir *= -1
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 45 if f2 else 70
                n = 7 if f2 else 5
                for i in range(n):
                    vx = (i - (n - 1) / 2) * 1.5
                    tiros.append(TiroInimigo(r.centerx, r.bottom, vx, 6, 15))

        elif self.tipo == 1:  # VÓRTICE: balança pela tela e varre o chão com rajadas
            r.centerx = int(LARGURA / 2 + 330 * math.sin(self.t * 0.012))
            ciclo = self.t % (130 if f2 else 150)
            if ciclo < 80 and ciclo % (5 if f2 else 7) == 0:
                ang = math.pi / 2 + 1.1 * math.sin(self.t * 0.12)
                tiros.append(TiroInimigo(r.centerx, r.bottom,
                                         math.cos(ang) * 5, math.sin(ang) * 5, 10))
                if f2:
                    tiros.append(TiroInimigo(r.centerx, r.bottom,
                                             -math.cos(ang) * 5, math.sin(ang) * 5, 10))

        else:  # CAÇADOR: persegue sua posição e atira mirando em você
            passo = 5 if f2 else 3
            dx = alvo.centerx - r.centerx
            r.x += max(-passo, min(passo, dx))
            r.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))
            self.olhar = max(-14, min(14, dx // 10))
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 55 if f2 else 80
                base = math.atan2(alvo.centery - r.bottom, alvo.centerx - r.centerx)
                for off in (-0.2, 0, 0.2):
                    a = base + off
                    tiros.append(TiroInimigo(r.centerx, r.bottom,
                                             math.cos(a) * 7, math.sin(a) * 7, 12))
        return tiros

    def draw(self):
        r = self.rect
        f = self.flash > 0

        if self.tipo == 0:
            cor = ROXO_CLARO if f else ROXO_INIMIGO
            casco = [(r.centerx, r.y), (r.x + 30, r.y + 15), (r.x, r.y + 40), (r.x + 25, r.bottom),
                     (r.right - 25, r.bottom), (r.right, r.y + 40), (r.right - 30, r.y + 15)]
            pygame.draw.polygon(tela, cor, casco)
            pygame.draw.polygon(tela, ROXO_ESCURO, casco, width=3)
            pygame.draw.rect(tela, ROXO_CLARO, (r.centerx - 40, r.y + 18, 80, 36))
            pygame.draw.rect(tela, PRETO, (r.centerx - 40, r.y + 18, 80, 36), width=2)
            for ox in (-30, 8):
                pygame.draw.rect(tela, VERDE_ALIEN, (r.centerx + ox, r.y + 28, 22, 12))
                pygame.draw.rect(tela, VERDE_ESCURO, (r.centerx + ox, r.y + 28, 22, 3))
            for cx in (r.x + 20, r.centerx - 5, r.right - 30):
                pygame.draw.rect(tela, VERDE_ALIEN, (cx, r.bottom - 6, 10, 10))
                pygame.draw.rect(tela, VERDE_ESCURO, (cx, r.bottom - 6, 10, 10), width=2)

        elif self.tipo == 1:
            cor = (255, 120, 100) if f else (190, 45, 70)
            casco = [(r.x + 35, r.y), (r.right - 35, r.y), (r.right, r.y + 35), (r.right, r.bottom - 25),
                     (r.right - 30, r.bottom), (r.x + 30, r.bottom), (r.x, r.bottom - 25), (r.x, r.y + 35)]
            pygame.draw.polygon(tela, cor, casco)
            pygame.draw.polygon(tela, (90, 15, 30), casco, width=3)
            cx, cy = r.center
            pygame.draw.circle(tela, AMARELO_FOGO, (cx, cy), 26)
            pygame.draw.circle(tela, PRETO, (cx, cy), 26, 2)
            pygame.draw.circle(tela, PRETO, (cx, cy), 10)
            for i in range(8):  # anel girando em volta do olho
                a = self.t * 0.08 + i * math.pi / 4
                pygame.draw.circle(tela, AMARELO_FOGO,
                                   (int(cx + math.cos(a) * 38), int(cy + math.sin(a) * 38)), 4)
            pygame.draw.rect(tela, LARANJA_FOGO, (cx - 8, r.bottom - 8, 16, 14))

        else:
            cor = (150, 255, 220) if f else (30, 150, 110)
            casco = [(r.x, r.y + 10), (r.right, r.y + 10), (r.right - 15, r.y + 45),
                     (r.centerx + 20, r.bottom), (r.centerx - 20, r.bottom), (r.x + 15, r.y + 45)]
            pygame.draw.polygon(tela, cor, casco)
            pygame.draw.polygon(tela, (10, 60, 40), casco, width=3)
            cx = r.centerx
            pygame.draw.ellipse(tela, BRANCO, (cx - 25, r.y + 18, 50, 24))
            pygame.draw.ellipse(tela, PRETO, (cx - 25, r.y + 18, 50, 24), 2)
            pygame.draw.circle(tela, (230, 40, 60), (cx + self.olhar // 2, r.y + 30), 8)
            for ox in (r.x + 10, r.right - 20):
                pygame.draw.rect(tela, VERDE_ALIEN, (ox, r.y + 2, 10, 12))


# 10. FUNÇÕES AUXILIARES
def desenhar_nave(j, triplo_ativo=False):
    corpo = [(j.centerx, j.top), (j.centerx - 10, j.top + 10), (j.left + 5, j.bottom - 3),
             (j.centerx - 5, j.bottom - 8), (j.centerx, j.bottom), (j.centerx + 5, j.bottom - 8),
             (j.right - 5, j.bottom - 3), (j.centerx + 10, j.top + 10)]
    pygame.draw.polygon(tela, AZUL_ESCURO, corpo)
    pygame.draw.polygon(tela, VERMELHO_CONTORNO, corpo, width=2)

    asa_e = [(j.centerx - 8, j.top + 14), (j.left, j.bottom - 2), (j.centerx - 5, j.bottom - 7)]
    asa_d = [(j.centerx + 8, j.top + 14), (j.right, j.bottom - 2), (j.centerx + 5, j.bottom - 7)]
    for asa in (asa_e, asa_d):
        pygame.draw.polygon(tela, CIANO, asa)
        pygame.draw.polygon(tela, VERMELHO_CONTORNO, asa, width=2)

    cabine = [(j.centerx, j.top + 7), (j.centerx - 5, j.top + 17), (j.centerx + 5, j.top + 17)]
    pygame.draw.polygon(tela, AZUL_CLARO, cabine)
    pygame.draw.polygon(tela, PRETO, cabine, width=1)

    # Fogo do motor com leve tremulação
    t = random.randint(8, 13)
    fogo = [(j.centerx - 6, j.bottom - 5), (j.centerx, j.bottom + t), (j.centerx + 6, j.bottom - 5)]
    pygame.draw.polygon(tela, LARANJA_FOGO, fogo)
    interno = [(j.centerx - 3, j.bottom - 4), (j.centerx, j.bottom + t // 2), (j.centerx + 3, j.bottom - 4)]
    pygame.draw.polygon(tela, AMARELO_FOGO, interno)

    # Pontinhos amarelos nas asas quando o tiro triplo está ativo
    if triplo_ativo:
        pygame.draw.circle(tela, AMARELO_FOGO, (j.left + 2, j.bottom - 6), 3)
        pygame.draw.circle(tela, AMARELO_FOGO, (j.right - 2, j.bottom - 6), 3)


def desenhar_escudo():
    # Pisca nos últimos 1,5 segundo para avisar que está acabando
    if escudo > 90 or (escudo // 6) % 2 == 0:
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80, 220, 255, 55), (50, 50), 46)
        pygame.draw.circle(surf, (170, 235, 255, 210), (50, 50), 46, 3)
        tela.blit(surf, surf.get_rect(center=(jogador.centerx, jogador.centery + 4)))


def desenhar_escalado(func, tamanho, escala, centro):
    """Desenha func() numa superfície pequena e amplia (usado nos enfeites do menu)."""
    global tela
    original = tela
    tela = pygame.Surface(tamanho, pygame.SRCALPHA)
    try:
        func()
        pequena = tela
    finally:
        tela = original
    grande = pygame.transform.scale(pequena, (int(tamanho[0] * escala), int(tamanho[1] * escala)))
    tela.blit(grande, grande.get_rect(center=centro))


def explodir(x, y, cores, qtd=25):
    for _ in range(qtd):
        particulas.append(Particula(x, y, cores))


def texto_centro(txt, fnt, cor, y):
    surf = fnt.render(txt, True, cor)
    tela.blit(surf, surf.get_rect(center=(LARGURA // 2, y)))


def cor_da_vida(frac):
    if frac > 0.6:
        return VERDE_ALIEN
    if frac > 0.3:
        return AMARELO_FOGO
    return (255, 70, 70)


def desenhar_barra_jogador():
    x, y, w, h = LARGURA - 250, 14, 230, 24
    frac = max(0, vida) / VIDA_MAX
    frac_atraso = max(0, vida_exibida) / VIDA_MAX
    pygame.draw.rect(tela, CINZA_BARRA, (x, y, w, h))
    pygame.draw.rect(tela, VERMELHO_ATRASO, (x, y, int(w * frac_atraso), h))   # parte "perdida"
    pygame.draw.rect(tela, cor_da_vida(frac), (x, y, int(w * frac), h))
    pygame.draw.rect(tela, BRANCO, (x, y, w, h), 2)
    txt = fonte_mini.render(f"HP {int(vida)}/{VIDA_MAX}", True, PRETO if frac > 0.3 else BRANCO)
    tela.blit(txt, txt.get_rect(center=(x + w // 2, y + h // 2)))

    linha = 0
    for nome, restante, total, cor in (("TIRO TRIPLO", triplo, DURACAO_TRIPLO, AMARELO_FOGO),
                                       ("ESCUDO", escudo, DURACAO_ESCUDO, CIANO)):
        if restante > 0:
            yy = 46 + linha * 30
            pygame.draw.rect(tela, CINZA_BARRA, (x, yy, w, 8))
            pygame.draw.rect(tela, cor, (x, yy, int(w * restante / total), 8))
            pygame.draw.rect(tela, BRANCO, (x, yy, w, 8), 1)
            tela.blit(fonte_mini.render(nome, True, cor), (x, yy + 9))
            linha += 1


def desenhar_barra_chefe():
    w, h = 300, 18
    x, y = LARGURA // 2 - w // 2, 14
    frac = max(0, chefe.vida) / chefe.vida_max
    pygame.draw.rect(tela, CINZA_BARRA, (x, y, w, h))
    pygame.draw.rect(tela, CORES_CHEFE[chefe.tipo], (x, y, int(w * frac), h))
    pygame.draw.rect(tela, BRANCO, (x, y, w, h), 2)
    t = fonte_mini.render(chefe.nome, True, BRANCO)
    tela.blit(t, t.get_rect(center=(LARGURA // 2, y + h + 12)))


def levar_dano(qtd, invulneravel=True):
    global vida, invul, shake
    if invul > 0 or escudo > 0:
        return
    vida -= max(1, int(qtd * dif()["dano"]))
    shake = 12
    tocar("dano")
    if invulneravel:
        invul = INVUL_FRAMES
        explodir(*jogador.center, [CIANO, LARANJA_FOGO, AMARELO_FOGO], 20)


def soltar_powerup(x, y, chance=None, tipo=None):
    if chance is None:
        chance = dif()["drop"]
    if random.random() < chance:
        powerups.append(PowerUp(x, y, tipo or random.choice(["vida", "triplo", "escudo"])))


def disparar(cd):
    global cooldown
    if triplo > 0:
        for dx in (-3, 0, 3):
            grupo_tiros.add(Tiro(jogador.centerx, jogador.top, dx))
    else:
        grupo_tiros.add(Tiro(jogador.centerx, jogador.top))
    cooldown = cd
    tocar("tiro")


# 11. ESTADO DO JOGO
recorde = carregar_recorde()


def novo_jogo():
    global jogador, velocidade, pontos, vida, vida_exibida, nivel, invul, cooldown
    global grupo_tiros, grupo_tiros_inimigos, inimigos, particulas, powerups
    global pausado, shake, triplo, escudo, chefe, chefes_derrotados
    jogador = pygame.Rect(LARGURA // 2 - 25, ALTURA - 120, 50, 30)
    velocidade = 8
    pontos, nivel = 0, 1
    vida = vida_exibida = VIDA_MAX
    invul, cooldown, shake, triplo, escudo = 0, 0, 0, 0, 0
    grupo_tiros = pygame.sprite.Group()
    grupo_tiros_inimigos = pygame.sprite.Group()
    inimigos = [Inimigo(nivel)]
    particulas = []
    powerups = []
    chefe = None
    chefes_derrotados = set()
    pausado = False


novo_jogo()

# Enfeites do menu
deco_inimigo = Inimigo(1)
deco_inimigo.rect = pygame.Rect(30, 20, 60, 30)

# Telas de menu
estado = "menu"        # "menu", "config" ou "jogando"
sel_menu = 0
sel_config = 0
msg_config = ""
msg_timer = 0
ITENS_MENU = ["Jogar", "Configurações", "Sair"]
N_CONFIG = 5           # volume, dificuldade, tiro contínuo, zerar recorde, voltar


def ajustar_config(d):
    """Muda a opção selecionada na tela de configurações (d = -1 ou +1)."""
    if sel_config == 0:
        cfg["volume"] = max(0, min(10, cfg["volume"] + d))
        salvar_config()
        tocar("selecionar")
    elif sel_config == 1:
        cfg["dificuldade"] = (cfg["dificuldade"] + d) % 3
        salvar_config()
        tocar("selecionar")
    elif sel_config == 2:
        cfg["tiro_continuo"] = not cfg["tiro_continuo"]
        salvar_config()
        tocar("selecionar")


def desenhar_menu():
    desenhar_fundo()
    t = pygame.time.get_ticks()
    cx = LARGURA // 2
    sombra = fonte_titulo.render("NAVE vs INIMIGO", True, ROXO_ESCURO)
    titulo = fonte_titulo.render("NAVE vs INIMIGO", True, CIANO)
    tela.blit(sombra, sombra.get_rect(center=(cx + 4, 114)))
    tela.blit(titulo, titulo.get_rect(center=(cx, 110)))

    # Nave e inimigos flutuando
    bob = int(8 * math.sin(t * 0.003))
    desenhar_escalado(lambda: desenhar_nave(pygame.Rect(35, 20, 50, 30)), (120, 80), 3, (cx, 280 + bob))
    for lado in (-1, 1):
        desenhar_escalado(deco_inimigo.draw, (120, 70), 2, (cx + lado * 290, 280 - bob))

    texto_centro(f"Recorde: {recorde}", fonte_pequena, AMARELO_FOGO, 395)

    for i, item in enumerate(ITENS_MENU):
        sel = i == sel_menu
        y = 480 + i * 70
        surf = fonte_media.render(item, True, AMARELO_FOGO if sel else BRANCO)
        rect = surf.get_rect(center=(cx, y))
        tela.blit(surf, rect)
        if sel:
            for lado, x in ((-1, rect.left - 30), (1, rect.right + 30)):
                pygame.draw.polygon(tela, AMARELO_FOGO,
                                    [(x + lado * 10, y), (x - lado * 8, y - 11), (x - lado * 8, y + 11)])

    texto_centro("Mover: setas ou WASD   |   Atirar: ESPAÇO   |   Pausar: P   |   Som: M",
                 fonte_pequena, AZUL_CLARO, ALTURA - 60)
    texto_centro("Cima/Baixo: escolher   Enter: selecionar   ESC: sair", fonte_pequena, AZUL_CLARO, ALTURA - 30)


def desenhar_config():
    desenhar_fundo()
    cx = LARGURA // 2
    texto_centro("CONFIGURAÇÕES", fonte_grande, CIANO, 110)

    painel = pygame.Surface((660, 420), pygame.SRCALPHA)
    painel.fill((10, 20, 45, 200))
    tela.blit(painel, (170, 190))
    pygame.draw.rect(tela, BRANCO, (170, 190, 660, 420), 2)

    rotulos = ["Volume", "Dificuldade", "Tiro contínuo", "Zerar recorde", "Voltar"]
    for i, rot in enumerate(rotulos):
        y = 240 + i * 75
        sel = i == sel_config
        if sel:
            destaque = pygame.Surface((620, 56), pygame.SRCALPHA)
            destaque.fill((60, 90, 160, 120))
            tela.blit(destaque, (190, y - 28))
        cor = AMARELO_FOGO if sel else BRANCO

        if i < 3:
            tela.blit(fonte.render(rot, True, cor), (220, y - 18))
        else:
            texto_centro(rot + (f" (atual: {recorde})" if i == 3 else ""), fonte, cor, y)

        if i == 0:
            for k in range(10):
                cor_seg = cor if k < cfg["volume"] else CINZA_BARRA
                pygame.draw.rect(tela, cor_seg, (520 + k * 24, y - 12, 18, 24))
            tela.blit(fonte_pequena.render(str(cfg["volume"]), True, cor), (775, y - 12))
        elif i == 1:
            v = fonte.render(f"<  {DIFICULDADES[cfg['dificuldade']][0]}  >", True, cor)
            tela.blit(v, v.get_rect(center=(670, y)))
        elif i == 2:
            v = fonte.render("<  " + ("Sim" if cfg["tiro_continuo"] else "Não") + "  >", True, cor)
            tela.blit(v, v.get_rect(center=(670, y)))

    if msg_timer > 0:
        texto_centro(msg_config, fonte_pequena, VERDE_ALIEN, 640)
    texto_centro("Cima/Baixo: escolher   Esq/Dir: alterar   ESC: voltar", fonte_pequena, AZUL_CLARO, ALTURA - 40)


# =============================================================================
# 12. LOOP PRINCIPAL
# =============================================================================
rodando = True
while rodando:

    # --- A. EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        elif event.type == pygame.KEYDOWN:
            k = event.key
            confirmar = k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
            cima = k in (pygame.K_UP, pygame.K_w)
            baixo = k in (pygame.K_DOWN, pygame.K_s)
            esq = k in (pygame.K_LEFT, pygame.K_a)
            dire = k in (pygame.K_RIGHT, pygame.K_d)

            if estado == "menu":
                if cima:
                    sel_menu = (sel_menu - 1) % len(ITENS_MENU)
                    tocar("menu")
                elif baixo:
                    sel_menu = (sel_menu + 1) % len(ITENS_MENU)
                    tocar("menu")
                elif confirmar:
                    tocar("selecionar")
                    if sel_menu == 0:
                        novo_jogo()
                        estado = "jogando"
                    elif sel_menu == 1:
                        estado = "config"
                        sel_config = 0
                    else:
                        rodando = False
                elif k == pygame.K_ESCAPE:
                    rodando = False

            elif estado == "config":
                if cima:
                    sel_config = (sel_config - 1) % N_CONFIG
                    tocar("menu")
                elif baixo:
                    sel_config = (sel_config + 1) % N_CONFIG
                    tocar("menu")
                elif esq:
                    ajustar_config(-1)
                elif dire:
                    ajustar_config(1)
                elif confirmar:
                    if sel_config in (1, 2):
                        ajustar_config(1)
                    elif sel_config == 3:
                        recorde = 0
                        salvar_recorde(0)
                        msg_config, msg_timer = "Recorde zerado!", 120
                        tocar("selecionar")
                    elif sel_config == 4:
                        tocar("selecionar")
                        estado = "menu"
                elif k == pygame.K_ESCAPE:
                    estado = "menu"

            else:  # jogando
                if k == pygame.K_ESCAPE:
                    if pausado or vida <= 0:
                        estado = "menu"
                    else:
                        pausado = True
                elif k == pygame.K_p and vida > 0:
                    pausado = not pausado
                elif k == pygame.K_m:
                    mudo = not mudo
                elif k == pygame.K_r and vida <= 0:
                    novo_jogo()
                elif (k == pygame.K_SPACE and vida > 0 and not pausado
                      and not cfg["tiro_continuo"] and cooldown == 0):
                    disparar(6)

    # --- B/C. TELAS DE MENU ---
    if estado == "menu":
        desenhar_menu()

    elif estado == "config":
        msg_timer = max(0, msg_timer - 1)
        desenhar_config()

    # --- D. JOGO ---
    else:
        # --- LÓGICA ---
        if vida > 0 and not pausado:
            teclas = pygame.key.get_pressed()
            if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and jogador.left > 0:
                jogador.x -= velocidade
            if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and jogador.right < LARGURA:
                jogador.x += velocidade
            if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and jogador.top > 0:
                jogador.y -= velocidade
            if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and jogador.bottom < ALTURA - 15:
                jogador.y += velocidade

            cooldown = max(0, cooldown - 1)
            if cfg["tiro_continuo"] and teclas[pygame.K_SPACE] and cooldown == 0:
                disparar(COOLDOWN_TIRO)

            invul = max(0, invul - 1)
            shake = max(0, shake - 1)
            triplo = max(0, triplo - 1)
            escudo = max(0, escudo - 1)
            grupo_tiros.update()
            grupo_tiros_inimigos.update()

            # Barra de vida: a parte "perdida" desce devagar
            if vida_exibida > vida:
                vida_exibida = max(vida, vida_exibida - 0.5)
            else:
                vida_exibida = vida

            # Nível sobe a cada 10 pontos
            nivel = pontos // 10 + 1

            # Chefe aparece a cada CHEFE_A_CADA níveis (o tipo gira entre os 3)
            if nivel % CHEFE_A_CADA == 0 and chefe is None and nivel not in chefes_derrotados:
                tipo_chefe = (nivel // CHEFE_A_CADA - 1) % 3
                chefe = Chefe(nivel, tipo_chefe)
                inimigos.clear()
                tocar("chefe")

            # Inimigos comuns (nenhum enquanto o chefe estiver na tela)
            if chefe is None:
                qtd_desejada = min(1 + (nivel - 1) // 2, 5)
                while len(inimigos) < qtd_desejada:
                    inimigos.append(Inimigo(nivel))

            for inimigo in inimigos:
                if inimigo.update(nivel):
                    vel_y = 6 + min(nivel * 0.3, 3)
                    grupo_tiros_inimigos.add(
                        TiroInimigo(inimigo.rect.centerx, inimigo.rect.bottom, 0, vel_y))

                # Tiro acertou o inimigo
                for tiro in grupo_tiros:
                    if tiro.rect.colliderect(inimigo.rect):
                        pontos += 1
                        tiro.kill()
                        tocar("explosao")
                        explodir(*inimigo.rect.center, [ROXO_CLARO, VERDE_ALIEN, AMARELO_FOGO])
                        soltar_powerup(*inimigo.rect.center)
                        inimigo.reiniciar(nivel)
                        break

                # Nave encostou no inimigo (com escudo, o inimigo é destruído sem dano)
                if jogador.colliderect(inimigo.rect) and (invul == 0 or escudo > 0):
                    if escudo > 0:
                        pontos += 1
                        tocar("explosao")
                        explodir(*inimigo.rect.center, [CIANO, ROXO_CLARO, BRANCO])
                        soltar_powerup(*inimigo.rect.center)
                    else:
                        levar_dano(25)
                        explodir(*inimigo.rect.center, [ROXO_CLARO, VERDE_ALIEN], 15)
                    inimigo.reiniciar(nivel)

                # Inimigo passou direto
                elif inimigo.rect.top > ALTURA:
                    levar_dano(10, invulneravel=False)
                    inimigo.reiniciar(nivel)

            # --- Chefe ---
            if chefe is not None:
                tiros_chefe = chefe.update(jogador)
                for b in tiros_chefe:
                    grupo_tiros_inimigos.add(b)
                if tiros_chefe and (chefe.tipo != 1 or chefe.t % 14 == 0):
                    tocar("tiro_chefe")

                if not chefe.entrando:
                    for tiro in grupo_tiros:
                        if tiro.rect.colliderect(chefe.rect):
                            tiro.kill()
                            chefe.vida -= 1
                            chefe.flash = 3
                            tocar("acerto")
                            explodir(tiro.rect.centerx, tiro.rect.top, [ROXO_CLARO, BRANCO], 3)

                if jogador.colliderect(chefe.rect):
                    levar_dano(40)

                if chefe.vida <= 0:
                    tocar("chefe_morre")
                    explodir(*chefe.rect.center,
                             [CORES_CHEFE[chefe.tipo], AMARELO_FOGO, VERDE_ALIEN, BRANCO], 120)
                    soltar_powerup(chefe.rect.centerx - 30, chefe.rect.centery, 1, "vida")
                    soltar_powerup(chefe.rect.centerx + 30, chefe.rect.centery, 1,
                                   random.choice(["triplo", "escudo"]))
                    pontos += 10
                    chefes_derrotados.add(nivel)
                    chefe = None

            # --- Tiros inimigos acertando a nave ---
            for bala in grupo_tiros_inimigos:
                if bala.rect.colliderect(jogador):
                    bala.kill()
                    if escudo > 0:
                        explodir(*bala.rect.center, [CIANO, BRANCO], 4)
                        tocar("acerto")
                    elif invul == 0:
                        levar_dano(bala.dano)

            # --- Power-ups ---
            for p in powerups:
                p.update()
                if p.rect.colliderect(jogador):
                    tocar("powerup")
                    if p.tipo == "vida":
                        vida = min(VIDA_MAX, vida + 25)
                    elif p.tipo == "triplo":
                        triplo = DURACAO_TRIPLO
                    else:
                        escudo = DURACAO_ESCUDO
                    explodir(*p.rect.center, [AMARELO_FOGO, BRANCO, VERDE_ALIEN], 12)
                    p.rect.top = ALTURA + 100  # marca para remoção
            powerups = [p for p in powerups if p.rect.top < ALTURA]

            for p in particulas:
                p.update()
            particulas = [p for p in particulas if p.vida > 0]

            # --- Fim de jogo ---
            if vida <= 0:
                vida = 0
                tocar("fim")
                explodir(*jogador.center, [CIANO, LARANJA_FOGO, AMARELO_FOGO, BRANCO], 80)
                if pontos > recorde:
                    recorde = pontos
                    salvar_recorde(recorde)

        elif vida <= 0:
            # Mantém as partículas da explosão animando na tela de Game Over
            for p in particulas:
                p.update()
            particulas = [p for p in particulas if p.vida > 0]

        # --- DESENHO ---
        desenhar_fundo(animar=(vida > 0 and not pausado))

        if vida > 0:
            for inimigo in inimigos:
                inimigo.draw()
            if chefe is not None:
                chefe.draw()
            for p in powerups:
                p.draw()
            grupo_tiros.draw(tela)
            grupo_tiros_inimigos.draw(tela)

            # Pisca enquanto está invulnerável
            if invul == 0 or (invul // 5) % 2 == 0:
                desenhar_nave(jogador, triplo > 0)
            if escudo > 0:
                desenhar_escudo()

            for p in particulas:
                p.draw()

            # HUD
            tela.blit(fonte.render(f"Pontos: {pontos}", True, BRANCO), (10, 10))
            tela.blit(fonte_pequena.render(
                f"Nível {nivel}   Recorde: {recorde}   {DIFICULDADES[cfg['dificuldade']][0]}",
                True, AMARELO_FOGO), (10, 48))
            desenhar_barra_jogador()
            if chefe is not None:
                desenhar_barra_chefe()
            if mudo:
                tela.blit(fonte_mini.render("MUDO (M)", True, BRANCO), (10, ALTURA - 24))

            if pausado:
                texto_centro("PAUSADO", fonte_grande, BRANCO, ALTURA // 2)
                texto_centro("P = continuar   ESC = menu", fonte_pequena, BRANCO, ALTURA // 2 + 45)
        else:
            for p in particulas:
                p.draw()
            caixa = pygame.Rect(LARGURA // 2 - 200, ALTURA // 2 - 100, 400, 200)
            pygame.draw.rect(tela, AZUL_ESCURO, caixa)
            pygame.draw.rect(tela, BRANCO, caixa, width=3)
            texto_centro("FIM DE JOGO", fonte_grande, BRANCO, ALTURA // 2 - 50)
            texto_centro(f"Pontos: {pontos}   Recorde: {recorde}", fonte, AMARELO_FOGO, ALTURA // 2 + 10)
            texto_centro("R = jogar de novo   ESC = menu", fonte_pequena, BRANCO, ALTURA // 2 + 60)

        # Tremida de tela ao levar dano
        if shake > 0 and vida > 0:
            copia = tela.copy()
            tela.fill(PRETO)
            tela.blit(copia, (random.randint(-5, 5), random.randint(-5, 5)))

    # --- E. ATUALIZA ---
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()