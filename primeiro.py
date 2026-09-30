import random
import pygame

# 1. INICIALIZAÇÃO
pygame.init()

# 2. TELA E JANELA
LARGURA, ALTURA = 1000, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Nave vs Inimigo")

# 3. PALETA DE CORES (RGB)
PRETO = (15, 15, 20)
BRANCO = (240, 245, 255)
# Jogador
AZUL_NAVE = (30, 144, 255)
AZUL_ESCURO = (10, 45, 90)
CIANO = (80, 220, 255)
AZUL_CLARO = (170, 235, 255)
VERMELHO_CONTORNO = (196, 30, 61)
# Inimigo
ROXO_INIMIGO = (145, 55, 220)
ROXO_ESCURO = (65, 20, 100)
ROXO_CLARO = (190, 100, 255)
VERDE_ALIEN = (90, 255, 150)
VERDE_ESCURO = (20, 120, 70)
# Fogo do motor
LARANJA_FOGO = (255, 140, 20)
AMARELO_FOGO = (255, 220, 60)

# 4. FONTES DE TEXTO
fonte = pygame.font.SysFont("Arial", 30)
fonte_grande = pygame.font.SysFont("Arial", 50)

# Imagem de fundo
try:
    fundo = pygame.image.load("Galaxie.jpg")
    fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))
except Exception:
    fundo = pygame.Surface((LARGURA, ALTURA))
    fundo.fill(PRETO)

# 5. CLASSE DO TIRO
class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill((255, 215, 0))  # Cor amarela
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = -10

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.bottom < 0:
            self.kill()

# 6. ENTIDADES E FÍSICA
jogador = pygame.Rect(375, 520, 50, 30)
velocidade = 10

alvo = pygame.Rect(random.randint(0, LARGURA - 60), 0, 60, 30)
velocidade_alvo = 4

# 7. ESTADO DO JOGO E GRUPOS
pontos = 0
vidas = 5
relogio = pygame.time.Clock()
grupo_tiros = pygame.sprite.Group()

# =============================================================================
# 8. LOOP PRINCIPAL DO JOGO (GAME LOOP)
# =============================================================================
rodando = True
while rodando:

    # --- A. CAPTURA DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and vidas > 0:
                novo_tiro = Tiro(jogador.centerx, jogador.top)
                grupo_tiros.add(novo_tiro)

    # --- B. LÓGICA DO JOGO ---
    if vidas > 0:
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and jogador.left > 0:
            jogador.x -= velocidade
        if teclas[pygame.K_RIGHT] and jogador.right < LARGURA:
            jogador.x += velocidade
        if teclas[pygame.K_UP] and jogador.y > 0:
            jogador.y -= velocidade
        if teclas[pygame.K_DOWN] and jogador.y < ALTURA:
            jogador.y += velocidade

        grupo_tiros.update()
        alvo.y += velocidade_alvo

        # Colisão: Tiro acertou o Alvo
        for tiro in grupo_tiros:
            if tiro.rect.colliderect(alvo):
                pontos += 1
                tiro.kill()
                alvo.x = random.randint(0, LARGURA - 60)
                alvo.y = 0

        # Colisão: Nave encostou no Alvo
        if jogador.colliderect(alvo):
            vidas -= 1
            alvo.x = random.randint(0, LARGURA - 60)
            alvo.y = 0

        # Penalidade: Alvo passou direto
        if alvo.top > ALTURA:
            vidas -= 1
            alvo.x = random.randint(0, LARGURA - 60)
            alvo.y = 0

    # --- C. RENDERIZAÇÃO E DESENHO ---
    tela.blit(fundo, (0, 0))

    if vidas > 0:
        # --- DESENHO DO INIMIGO ---
        # Corpo principal
        corpo_inimigo = [ (alvo.centerx, alvo.y), (alvo.x + 10, alvo.y + 8), (alvo.x + 10, alvo.bottom), (alvo.right - 10, alvo.bottom), (alvo.right - 10, alvo.y + 8) ]
        pygame.draw.polygon(tela, ROXO_INIMIGO, corpo_inimigo)
        pygame.draw.polygon(tela, ROXO_ESCURO, corpo_inimigo, width=2)
        pygame.draw.rect( tela, ROXO_CLARO, (alvo.x + 15, alvo.y + 7, 30, 18) )
        pygame.draw.rect( tela, PRETO, (alvo.x + 15, alvo.y + 7, 30, 18), width=2 )
        pygame.draw.rect( tela, VERDE_ALIEN, (alvo.x + 21, alvo.y + 12, 18, 8) )
        pygame.draw.rect( tela, VERDE_ESCURO, (alvo.x + 21, alvo.y + 12, 18, 2) )
        pygame.draw.rect( tela, VERDE_ALIEN, (alvo.x + 14, alvo.y, 6, 5) )
        pygame.draw.rect( tela, VERDE_ALIEN, (alvo.right - 20, alvo.y, 6, 5) )
        pygame.draw.rect( tela, VERDE_ESCURO, (alvo.x + 14, alvo.bottom - 4, 5, 5) )
        pygame.draw.rect( tela, VERDE_ESCURO, (alvo.right - 19, alvo.bottom - 4, 5, 5) )

        # Desenha os Tiros
        grupo_tiros.draw(tela)

        # --- DESENHO DA NAVE DO JOGADOR ---
        corpo_nave = [ (jogador.centerx, jogador.top), (jogador.centerx - 10, jogador.top + 10), (jogador.left + 5, jogador.bottom - 3), (jogador.centerx - 5, jogador.bottom - 8), (jogador.centerx, jogador.bottom), (jogador.centerx + 5, jogador.bottom - 8), (jogador.right - 5, jogador.bottom - 3), (jogador.centerx + 10, jogador.top + 10) ]
        pygame.draw.polygon( tela, AZUL_ESCURO, corpo_nave )
        pygame.draw.polygon( tela, VERMELHO_CONTORNO, corpo_nave, width=2 )

        asa_esquerda = [ (jogador.centerx - 8, jogador.top + 14), (jogador.left, jogador.bottom - 2), (jogador.centerx - 5, jogador.bottom - 7) ]
        asa_direita = [ (jogador.centerx + 8, jogador.top + 14), (jogador.right, jogador.bottom - 2), (jogador.centerx + 5, jogador.bottom - 7) ]

        pygame.draw.polygon( tela, CIANO, asa_esquerda )
        pygame.draw.polygon( tela, CIANO, asa_direita )
        pygame.draw.polygon( tela, VERMELHO_CONTORNO, asa_esquerda, width=2 )
        pygame.draw.polygon( tela, VERMELHO_CONTORNO, asa_direita, width=2 )

        cabine = [ (jogador.centerx, jogador.top + 7), (jogador.centerx - 5, jogador.top + 17), (jogador.centerx + 5, jogador.top + 17) ]
        pygame.draw.polygon( tela, AZUL_CLARO, cabine )
        pygame.draw.polygon( tela, PRETO, cabine, width=1 )

        # --- FOGO DO MOTOR ---
        fogo_motor = [ (jogador.centerx - 6, jogador.bottom - 5), (jogador.centerx, jogador.bottom + 10), (jogador.centerx + 6, jogador.bottom - 5) ]
        pygame.draw.polygon( tela, LARANJA_FOGO, fogo_motor )
        fogo_interno = [ (jogador.centerx - 3, jogador.bottom - 4), (jogador.centerx, jogador.bottom + 5), (jogador.centerx + 3, jogador.bottom - 4) ]
        pygame.draw.polygon( tela, AMARELO_FOGO, fogo_interno )

        # Renderiza HUD
        texto = fonte.render("Pontos: " + str(pontos), True, BRANCO)
        tela.blit(texto, (10, 10))

        texto_vidas = fonte.render("Vidas: " + str(vidas), True, VERDE_ALIEN)
        tela.blit(texto_vidas, (LARGURA - 130, 10))
    else:
        # Tela de Game Over (Texto em BRANCO com fundo destacado)
        caixa_fim = pygame.Rect(LARGURA // 2 - 160, ALTURA // 2 - 40, 320, 80)
        pygame.draw.rect(tela, AZUL_ESCURO, caixa_fim)
        pygame.draw.rect(tela, BRANCO, caixa_fim, width=3)

        texto_fim = fonte_grande.render("FIM DE JOGO", True, BRANCO)
        rect_fim = texto_fim.get_rect(center=(LARGURA // 2, ALTURA // 2))
        tela.blit(texto_fim, rect_fim)

    # --- D. ATUALIZAÇÃO DA TELA ---
    pygame.display.flip()
    relogio.tick(60)

pygame.quit()