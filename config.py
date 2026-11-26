import os

LARGURA_JANELA = 576
ALTURA_JANELA = 324
LARGURA_MUNDO = 5000
LARGURA_FASE_2 = 5000
LARGURA_FASE_3 = 5000
LARGURA_FASE_4 = LARGURA_JANELA * 3
ALTURA_MUNDO = 324

PASTA_ASSETS = "Assets"
PASTA_SOUNDTRACK = "Soundtrack"

# Tela inicial e transição
CAMINHO_CAPA = f"{PASTA_ASSETS}/Capa-completa.png"
CAMINHO_INTRO = f"{PASTA_ASSETS}/Animation-1-sheet.png"
FRAMES_INTRO = 8
COR_FUNDO_ANIM_INTRO = (16, 14, 19)

# Cenário e chão por fase
CAMINHO_CHAO_FASE_1 = f"{PASTA_ASSETS}/Floor-cave.png"
CAMINHO_CHAO_FASE_2 = f"{PASTA_ASSETS}/Floor.png"
CAMINHO_CHAO_BOSS = f"{PASTA_ASSETS}/Floor-bank.png"
CAMINHO_CHAO = CAMINHO_CHAO_FASE_2

CAMINHO_FUNDO_FASE_1 = f"{PASTA_ASSETS}/Cave.png"
CAMINHO_FUNDO_FASE_2 = f"{PASTA_ASSETS}/Background.png"
CAMINHO_FUNDO_BOSS = f"{PASTA_ASSETS}/Bank.png"

# Plataformas Fase 1 (Caverna) (+8 px de altura em relação ao padrão)
CAMINHO_TILE_CAVE_1 = f"{PASTA_ASSETS}/Tiles-cave-1.png"
TAM_TILE_CAVE_1 = (150, 40)

CAMINHO_TILE_CAVE_2 = f"{PASTA_ASSETS}/Tiles-cave-2.png"
TAM_TILE_CAVE_2 = (200, 40)

CAMINHO_TILE_CAVE_3 = f"{PASTA_ASSETS}/Tiles-cave-3.png"
TAM_TILE_CAVE_3 = (300, 40)

# Plataformas Fase 2 (Swamp) (+8 px de altura em relação ao padrão)
CAMINHO_TILE_SWAMP_1 = f"{PASTA_ASSETS}/Tiles-swamp-1.png"
TAM_TILE_SWAMP_1 = (150, 40)

CAMINHO_TILE_SWAMP_2 = f"{PASTA_ASSETS}/Tiles-swamp-2.png"
TAM_TILE_SWAMP_2 = (200, 40)

CAMINHO_TILE_SWAMP_3 = f"{PASTA_ASSETS}/Tiles-swamp-3.png"
TAM_TILE_SWAMP_3 = (300, 40)

CAMINHO_MAPA_FASE_1 = "fase1.txt"
CAMINHO_MAPA_FASE_2 = "fase2.txt"

# Acessórios decorativos (intangíveis)
ACESSORIOS_MUSHROOM = [
    f"{PASTA_ASSETS}/Mushroom-1.png",
    f"{PASTA_ASSETS}/Mushroom-2.png",
    f"{PASTA_ASSETS}/Mushroom-3.png",
]

ACESSORIOS_APENAS_CHAO = [
    f"{PASTA_ASSETS}/Tree-1.png",
    f"{PASTA_ASSETS}/Tree-2.png",
    f"{PASTA_ASSETS}/Tree-3.png",
    f"{PASTA_ASSETS}/Ridge.png",
    f"{PASTA_ASSETS}/Ridge-1.png",
    f"{PASTA_ASSETS}/Ridge-2.png",
]

ACESSORIOS_CHAO_E_PLATAFORMA = [
    f"{PASTA_ASSETS}/grass-short.png",
    f"{PASTA_ASSETS}/log-fallen.png",
    f"{PASTA_ASSETS}/Mushroom-1.png",
    f"{PASTA_ASSETS}/Mushroom-2.png",
    f"{PASTA_ASSETS}/Mushroom-3.png",
]

ACESSORIOS_FASE_1 = list(ACESSORIOS_MUSHROOM)
ACESSORIOS_FASE_2_3 = ACESSORIOS_APENAS_CHAO + ACESSORIOS_CHAO_E_PLATAFORMA

# Jogador (Ceet)
VIDA_PLAYER = 100
VEL_PLAYER = 210.0

CAMINHO_IDLE = f"{PASTA_ASSETS}/Ceet-idle.png"
FRAMES_IDLE = 3

CAMINHO_ROLL = f"{PASTA_ASSETS}/Ceet-roll.png"
FRAMES_ROLL = 2

CAMINHO_WALK_RIGHT = f"{PASTA_ASSETS}/Ceet-walking_right.png"
FRAMES_WALK_RIGHT = 5

CAMINHO_WALK_LEFT = f"{PASTA_ASSETS}/Ceet-walking_left.png"
FRAMES_WALK_LEFT = 5

CAMINHO_ATTACK = f"{PASTA_ASSETS}/Ceet-attack.png"
FRAMES_ATTACK = 4
DANO_ATAQUE_PLAYER = 10

CAMINHO_ROLL_ATTACK = f"{PASTA_ASSETS}/Ceet-roll-attack.png"
FRAMES_ROLL_ATTACK = 11
DANO_ATAQUE_PULANDO = 20

# Bônus de combo do player
MULTIPLICADOR_COMBO_DANO = 1.1
COMBO_MAXIMO = 10

# Inimigos, Minibosses e Chefe Final
VIDA_FROG = 300
CAMINHO_FROG_IDLE = f"{PASTA_ASSETS}/Frog-idle.png"
FRAMES_FROG_IDLE = 3

CAMINHO_FROG_JUMPING = f"{PASTA_ASSETS}/Frog-jumping.png"
FRAMES_FROG_JUMPING = 8

CAMINHO_FROG_PREPARING = f"{PASTA_ASSETS}/Frog-preparing.png"
FRAMES_FROG_PREPARING = 6

VIDA_WORM = 20
CAMINHO_WORM_WALK = f"{PASTA_ASSETS}/worm_walk_anim.png"
FRAMES_WORM_WALK = 6

VIDA_MINIBOSS_FLY = 120
CAMINHO_BLUE_FLY_BOSS = f"{PASTA_ASSETS}/blue-fly-boss-attack-anim.png"
FRAMES_BLUE_FLY_BOSS = 3

VIDA_WORM_FASE2_BOSS = 200
CAMINHO_WORM_WALK_BOSS = f"{PASTA_ASSETS}/worm_walk_anim-boss.png"
FRAMES_WORM_WALK_BOSS = 6
CAMINHO_WORM_RISE_BOSS = f"{PASTA_ASSETS}/worm-rise-anim-boss.png"
FRAMES_WORM_RISE_BOSS = 7
CAMINHO_WORM_ATTACK_BOSS = f"{PASTA_ASSETS}/worm-attack-anim-boss.png"
FRAMES_WORM_ATTACK_BOSS = 16

VIDA_MUSHROOM = 40
CAMINHO_MUSHROOM_WALK = f"{PASTA_ASSETS}/mushroom_walk_anim.png"
FRAMES_MUSHROOM_WALK = 8

CAMINHO_MUSHROOM_RUN = f"{PASTA_ASSETS}/Mushroom-Run.png"
FRAMES_MUSHROOM_RUN = 8

CAMINHO_MUSHROOM_CRUSHED = f"{PASTA_ASSETS}/mushroom_crushed_anim.png"
FRAMES_MUSHROOM_CRUSHED = 6

VIDA_BLUE_FLY = 20
CAMINHO_BLUE_FLY_ATTACK = f"{PASTA_ASSETS}/blue_fly_attack_anim.png"
FRAMES_BLUE_FLY_ATTACK = 3

# História e efeito Typewriter
CAMINHO_TYPEWRITER = os.path.join(PASTA_SOUNDTRACK, "Typewriter.wav")
VOLUME_TYPEWRITER = 0.65
INTERVALO_LETRA_HISTORIA = 0.065
INTERVALO_LETRA_FASE_4 = 0.105

CORES_HISTORIA = {
    "branco": (240, 242, 245),
    "cinza": (170, 175, 185),
    "verde": (85, 220, 115),
    "azul": (95, 175, 255),
    "vermelho": (235, 65, 75),
    "amarelo": (255, 225, 85),
}
