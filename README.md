# Nave vs Inimigo 🚀👾

Um jogo 2D no estilo *Space Shooter* desenvolvido em **Python** utilizando a biblioteca **Pygame**. Controle sua nave espacial, destrua as ameaças inimigas e pontue o máximo possível enquanto gerencia suas vidas.

---

## 🎮 Sobre o Jogo

Em **Nave vs Inimigo**, você assume o controle de uma nave espacial em um campo de batalha estelar. O objetivo é disparar contra as naves inimigas que surgem no topo da tela antes que elas colidam com você ou passem direto pela sua defesa.

---

## 🌟 Funcionalidades

* **Movimentação Livre:** Controle total de direção (360° em grade 2D).
* **Sistema de Disparos:** Mecânica de tiro rápido utilizando gerenciamento de sprites (`pygame.sprite.Group`).
* **Geração Aleatória:** Inimigos surgem em posições variadas e reaparecem ao serem destruídos ou ultrapassarem a tela.
* **HUD em Tempo Real:** Exibição contínua de pontuação e contador de vidas.
* **Gráficos Vetoriais Customizados:** Desenho geométrico detalhado da nave, inimigo e animação do fogo do motor.
* **Fallback de Textura:** Tratamento automático de erro caso a imagem de fundo (`Galaxie.jpg`) não esteja presente na pasta.

---

## 🛠️ Tecnologias Utilizadas

* [**Python 3.x**](https://www.python.org/)
* [**Pygame**](https://www.pygame.org/)

---

## 🕹️ Controles

| Ação | Comando |
| :--- | :--- |
| **Mover para Esquerda** | Seta Esquerda (`←`) |
| **Mover para Direita** | Seta Direita (`→`) |
| **Mover para Cima** | Seta para Cima (`↑`) |
| **Mover para Baixo** | Seta para Baixo (`↓`) |
| **Atirar** | Barra de Espaço (`Espaço`) |

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

Certifique-se de ter o **Python** instalado em sua máquina. Em seguida, instale a biblioteca **Pygame**:

```bash
pip install pygame
```

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. *(Opcional)* **Adicione a imagem de fundo:**
   * Adicione uma imagem chamada `Galaxie.jpg` na raiz do projeto para personalizar o plano de fundo. Caso contrário, o jogo iniciará automaticamente com fundo preto.

3. **Execute o jogo:**
   ```bash
   python main.py
   ```

---

## 📁 Estrutura do Repositório

```text
├── Galaxie.jpg     # Imagem de fundo (opcional)
├── main.py         # Código-fonte principal do jogo
└── README.md       # Documentação do projeto
```

---

## 📝 Regras do Jogo

* **+1 Ponto:** Cada tiro acertado no inimigo.
* **-1 Vida:** Se a nave inimiga colidir com a sua nave.
* **-1 Vida:** Se a nave inimiga ultrapassar a parte inferior da tela.
* **Game Over:** O jogo encerra quando o contador de vidas chega a zero.
