import os
import pygame
from PPlay.gameimage import GameImage
from PPlay.gameobject import GameObject
from PPlay.parallax import ParallaxSystem
from boss_system import BossFinalFrog
from config import (
    CAMINHO_CHAO_BOSS,
    CAMINHO_CHAO_FASE_1,
    CAMINHO_CHAO_FASE_2,
    CAMINHO_FUNDO_BOSS,
    CAMINHO_FUNDO_FASE_1,
    CAMINHO_FUNDO_FASE_2,
    CAMINHO_MAPA_FASE_1,
    CAMINHO_MAPA_FASE_2,
    CAMINHO_TILE_CAVE_1,
    CAMINHO_TILE_CAVE_2,
    CAMINHO_TILE_CAVE_3,
    CAMINHO_TILE_SWAMP_1,
    CAMINHO_TILE_SWAMP_2,
    CAMINHO_TILE_SWAMP_3,
    CAMINHO_WORM_WALK_BOSS,
    LARGURA_FASE_2,
    LARGURA_FASE_3,
    LARGURA_FASE_4,
    LARGURA_MUNDO,
    TAM_TILE_CAVE_1,
    TAM_TILE_CAVE_2,
    TAM_TILE_CAVE_3,
    TAM_TILE_SWAMP_1,
    TAM_TILE_SWAMP_2,
    TAM_TILE_SWAMP_3,
    VIDA_BLUE_FLY,
    VIDA_MUSHROOM,
    VIDA_WORM,
)
from enemies import BlueFly, Mushroom, Worm
from miniboss import MinibossFly
from worm_boss_fase2 import MinibossWormFase2


class AcessorioDecorativo:
    def __init__(self, x, base_y, surface, em_frente_plataforma=False):
        self.image = surface
        self.width = float(surface.get_width()) if surface is not None else 0.0
        self.height = float(surface.get_height()) if surface is not None else 0.0
        self.x = float(x)
        self.y = float(base_y) - self.height
        self.em_frente_plataforma = em_frente_plataforma

    def draw(self, janela, camera):
        if self.image is None:
            return
        janela.screen.blit(
            self.image,
            (camera.transform_x(self.x), camera.transform_y(self.y)),
        )


class Plataforma(GameObject):
    def __init__(self, x, y, width, height, caminho_imagem, eh_chao_base=False):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.eh_chao_base = eh_chao_base

        img_original = GameImage(caminho_imagem)
        src = getattr(img_original, "image", None)
        if not eh_chao_base and src is not None:
            w_alvo = max(1, int(width))
            h_alvo = max(1, int(height))
            if src.get_width() == w_alvo and src.get_height() == h_alvo:
                self.image = src
            else:
                self.image = pygame.transform.smoothscale(src, (w_alvo, h_alvo))
        else:
            self.image = src

    def draw(self, janela, camera):
        if self.image is None:
            return
        janela.screen.blit(self.image, (camera.transform_x(self.x), camera.transform_y(self.y)))


class GatilhoFase:
    def __init__(self, x, y, width, height, fase_destino):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fase_destino = fase_destino

    def jogador_ativou(self, jogador):
        return (
            (jogador.x + jogador.width > self.x)
            and (jogador.x < self.x + self.width)
            and (jogador.y + jogador.height > self.y)
            and (jogador.y < self.y + self.height)
        )

    def draw(self, janela, camera):
        rect = pygame.Rect(
            int(camera.transform_x(self.x)),
            int(camera.transform_y(self.y)),
            int(self.width),
            int(self.height),
        )
        pygame.draw.rect(janela.screen, (255, 215, 0), rect, width=2)


class FaseManager:
    def __init__(self, pos_y_chao, altura_chao, cache_render):
        self.pos_y_chao = pos_y_chao
        self.altura_chao = altura_chao
        self._cache = cache_render

        img_walk_boss = pygame.image.load(CAMINHO_WORM_WALK_BOSS)
        self.altura_worm_walk_boss = float(img_walk_boss.get_height())

        self._sprites_acessorios = self._carregar_sprites_acessorios()

        self.tiles_por_fase = {
            1: {
                "1": (TAM_TILE_CAVE_1, CAMINHO_TILE_CAVE_1),
                "2": (TAM_TILE_CAVE_2, CAMINHO_TILE_CAVE_2),
                "3": (TAM_TILE_CAVE_3, CAMINHO_TILE_CAVE_3),
            },
            2: {
                "1": (TAM_TILE_SWAMP_1, CAMINHO_TILE_SWAMP_1),
                "2": (TAM_TILE_SWAMP_2, CAMINHO_TILE_SWAMP_2),
                "3": (TAM_TILE_SWAMP_3, CAMINHO_TILE_SWAMP_3),
            },
            3: {
                "1": (TAM_TILE_SWAMP_1, CAMINHO_TILE_SWAMP_1),
                "2": (TAM_TILE_SWAMP_2, CAMINHO_TILE_SWAMP_2),
                "3": (TAM_TILE_SWAMP_3, CAMINHO_TILE_SWAMP_3),
            },
            4: {
                "1": (TAM_TILE_SWAMP_1, CAMINHO_TILE_SWAMP_1),
                "2": (TAM_TILE_SWAMP_2, CAMINHO_TILE_SWAMP_2),
                "3": (TAM_TILE_SWAMP_3, CAMINHO_TILE_SWAMP_3),
            },
        }

        self.fases = {
            1: {
                "nome": "Fase 1 - Caverna",
                "largura_mundo": LARGURA_MUNDO,
                "fundo": CAMINHO_FUNDO_FASE_1,
                "chao": CAMINHO_CHAO_FASE_1,
                "mapa": CAMINHO_MAPA_FASE_1,
                "fator_parallax": 0.5,
                "proximo": 2,
            },
            2: {
                "nome": "Fase 2 - Pântano",
                "largura_mundo": LARGURA_FASE_2,
                "fundo": CAMINHO_FUNDO_FASE_2,
                "chao": CAMINHO_CHAO_FASE_2,
                "mapa": CAMINHO_MAPA_FASE_2,
                "fator_parallax": 0.5,
                "proximo": 3,
            },
            3: {
                "nome": "Fase 3 - Trilha Alta",
                "largura_mundo": LARGURA_FASE_3,
                "fundo": CAMINHO_FUNDO_FASE_2,
                "chao": CAMINHO_CHAO_FASE_2,
                "mapa": None,
                "fator_parallax": 0.5,
                "proximo": 4,
            },
            4: {
                "nome": "Fase 4 - Arena do Boss",
                "largura_mundo": LARGURA_FASE_4,
                "fundo": CAMINHO_FUNDO_BOSS,
                "chao": CAMINHO_CHAO_BOSS,
                "mapa": None,
                "fator_parallax": 0.5,
                "proximo": None,
            },
        }
        self.fase_atual = 1
        self.largura_mundo_atual = LARGURA_MUNDO
        self.parallax = None
        self.img_chao = None
        self.dados_mapa = []
        self.plataformas = []
        self.acessorios = []
        self.inimigos = []
        self.miniboss = None
        self.worm_boss_f2 = None
        self.boss_final = None
        self.gatilho = None
        self._plat_saida = None
        self._primeira_plat = None
        self.carregar_fase(1)

    def _carregar_sprites_acessorios(self):
        pasta_base = os.path.dirname(os.path.abspath(__file__))
        nomes = [
            "grass-short.png",
            "log-fallen.png",
            "Mushroom-1.png",
            "Mushroom-2.png",
            "Mushroom-3.png",
            "Ridge.png",
            "Ridge-1.png",
            "Ridge-2.png",
            "Tree-1.png",
            "Tree-2.png",
            "Tree-3.png",
        ]
        mapa = {}
        for nome in nomes:
            candidatos = [
                os.path.join(pasta_base, "Assets", nome),
                os.path.join(pasta_base, "Assests", nome),
                os.path.join(pasta_base, nome),
            ]
            surf = None
            for caminho in candidatos:
                if os.path.exists(caminho):
                    try:
                        surf = pygame.image.load(caminho).convert_alpha()
                        break
                    except pygame.error:
                        try:
                            surf = pygame.image.load(caminho)
                            break
                        except pygame.error:
                            surf = None
            mapa[nome] = surf
        return mapa

    def _montar_acessorios_fase(self, numero_fase, largura_mundo):
        lista = []
        if numero_fase == 4:
            return lista

        mushrooms = [
            self._sprites_acessorios.get("Mushroom-1.png"),
            self._sprites_acessorios.get("Mushroom-2.png"),
            self._sprites_acessorios.get("Mushroom-3.png"),
        ]
        mushrooms = [m for m in mushrooms if m is not None]

        if numero_fase == 1:
            if not mushrooms:
                return lista

            # Cogumelos espalhados no chão (no mínimo na altura do chão)
            x_chao = 140.0
            idx = 0
            while x_chao < largura_mundo - 180.0:
                surf = mushrooms[idx % len(mushrooms)]
                lista.append(AcessorioDecorativo(x_chao, self.pos_y_chao, surf))
                x_chao += 250.0 + (idx % 3) * 45.0
                idx += 1

            # Cogumelos sobre e em frente às plataformas da Fase 1
            for p_idx, plat in enumerate(self.plataformas):
                if plat.eh_chao_base:
                    continue
                surf_sobre = mushrooms[p_idx % len(mushrooms)]
                if plat.width >= surf_sobre.get_width() + 8:
                    x_sobre = plat.x + (plat.width - surf_sobre.get_width()) * 0.35
                    lista.append(AcessorioDecorativo(x_sobre, plat.y, surf_sobre))

                surf_frente = mushrooms[(p_idx + 1) % len(mushrooms)]
                x_frente = plat.x + plat.width * 0.55
                lista.append(
                    AcessorioDecorativo(
                        x_frente, self.pos_y_chao, surf_frente, em_frente_plataforma=True
                    )
                )
            return lista

        # Fases 2 e 3: todos os acessórios variados
        apenas_chao = [
            self._sprites_acessorios.get("Tree-1.png"),
            self._sprites_acessorios.get("Tree-2.png"),
            self._sprites_acessorios.get("Tree-3.png"),
            self._sprites_acessorios.get("Ridge.png"),
            self._sprites_acessorios.get("Ridge-1.png"),
            self._sprites_acessorios.get("Ridge-2.png"),
        ]
        apenas_chao = [s for s in apenas_chao if s is not None]

        chao_e_plataforma = [
            self._sprites_acessorios.get("grass-short.png"),
            self._sprites_acessorios.get("log-fallen.png"),
        ] + mushrooms
        chao_e_plataforma = [s for s in chao_e_plataforma if s is not None]

        todos_chao = apenas_chao + chao_e_plataforma
        if todos_chao:
            x_c = 130.0
            i_c = 0
            while x_c < largura_mundo - 220.0:
                surf = todos_chao[i_c % len(todos_chao)]
                lista.append(AcessorioDecorativo(x_c, self.pos_y_chao, surf))
                x_c += 210.0 + (i_c % 4) * 40.0
                i_c += 1

        if chao_e_plataforma:
            for p_idx, plat in enumerate(self.plataformas):
                if plat.eh_chao_base:
                    continue
                surf_topo = chao_e_plataforma[p_idx % len(chao_e_plataforma)]
                if plat.width >= surf_topo.get_width() + 6:
                    x_topo = plat.x + (plat.width - surf_topo.get_width()) * 0.45
                    lista.append(AcessorioDecorativo(x_topo, plat.y, surf_topo))

                surf_frente = chao_e_plataforma[(p_idx + 2) % len(chao_e_plataforma)]
                x_frente = plat.x + plat.width * 0.25
                lista.append(
                    AcessorioDecorativo(
                        x_frente, self.pos_y_chao, surf_frente, em_frente_plataforma=True
                    )
                )

        return lista

    def _carregar_linhas_mapa(self, caminho_mapa):
        if not caminho_mapa or not os.path.exists(caminho_mapa):
            return []
        with open(caminho_mapa, "r", encoding="utf-8") as arquivo:
            return [linha.rstrip("\r\n") for linha in arquivo]

    def _montar_plataformas_fase(
        self, numero_fase, linhas_mapa, caminho_chao, largura_mundo, passo_x=40, passo_y=32
    ):
        lista = [
            Plataforma(
                0,
                self.pos_y_chao,
                largura_mundo,
                self.altura_chao,
                caminho_chao,
                eh_chao_base=True,
            )
        ]

        mapa_tiles = self.tiles_por_fase.get(numero_fase, self.tiles_por_fase[1])
        y_min_seguro = 44.0
        self._plat_saida = None
        self._primeira_plat = None

        (w1, h1), tile1 = mapa_tiles["1"]
        (w2, h2), tile2 = mapa_tiles["2"]
        (w3, h3), tile3 = mapa_tiles["3"]

        if numero_fase == 1:
            plat_inicial_1 = Plataforma(
                420.0,
                max(y_min_seguro, self.pos_y_chao - h3 - 56.0),
                w3,
                h3,
                tile3,
                eh_chao_base=False,
            )
            lista.append(plat_inicial_1)
            self._primeira_plat = plat_inicial_1

            plats_f1 = [
                (920.0, max(y_min_seguro, self.pos_y_chao - h1 - 56.0), w1, h1, tile1),
                (1480.0, max(y_min_seguro, self.pos_y_chao - h3 - 105.0), w3, h3, tile3),
                (2060.0, max(y_min_seguro, self.pos_y_chao - h2 - 64.0), w2, h2, tile2),
                (2680.0, max(y_min_seguro, self.pos_y_chao - h2 - 98.0), w2, h2, tile2),
                (3280.0, max(y_min_seguro, self.pos_y_chao - h3 - 62.0), w3, h3, tile3),
                (3820.0, max(y_min_seguro, self.pos_y_chao - h1 - 74.0), w1, h1, tile1),
            ]
            for px, py, pw, ph, c_tile in plats_f1:
                if px + pw <= largura_mundo - 20:
                    lista.append(Plataforma(px, py, pw, ph, c_tile, eh_chao_base=False))

            plat_precisao = Plataforma(
                4290.0,
                max(y_min_seguro, self.pos_y_chao - h1 - 58.0),
                w1,
                h1,
                tile1,
                eh_chao_base=False,
            )
            plat_passagem = Plataforma(
                4540.0,
                max(y_min_seguro, self.pos_y_chao - h2 - 86.0),
                w2,
                h2,
                tile2,
                eh_chao_base=False,
            )
            lista.append(plat_precisao)
            lista.append(plat_passagem)
            self._plat_saida = plat_passagem

        elif numero_fase == 2:
            metade_f2 = largura_mundo * 0.5
            plat_inicial_2 = Plataforma(
                420.0,
                max(y_min_seguro, self.pos_y_chao - h3 - 56.0),
                w3,
                h3,
                tile3,
                eh_chao_base=False,
            )
            lista.append(plat_inicial_2)
            self._primeira_plat = plat_inicial_2

            plats_primeira_metade = [
                (960.0, max(y_min_seguro, self.pos_y_chao - h2 - 64.0), w2, h2, tile2),
                (1520.0, max(y_min_seguro, self.pos_y_chao - h3 - 96.0), w3, h3, tile3),
                (2040.0, max(y_min_seguro, self.pos_y_chao - h1 - 58.0), w1, h1, tile1),
            ]
            for px, py, pw, ph, c_tile in plats_primeira_metade:
                if px + pw < metade_f2 - 60:
                    lista.append(Plataforma(px, py, pw, ph, c_tile, eh_chao_base=False))

            x_w2 = metade_f2 + 120.0
            passo_idx = 0
            while x_w2 < largura_mundo - 380.0:
                if passo_idx % 2 == 0:
                    py_w2 = max(
                        y_min_seguro, self.pos_y_chao - self.altura_worm_walk_boss - 26.0
                    )
                    lista.append(Plataforma(x_w2, py_w2, w1, h1, tile1, eh_chao_base=False))
                else:
                    py_w2 = max(
                        y_min_seguro, self.pos_y_chao - self.altura_worm_walk_boss - 62.0
                    )
                    lista.append(Plataforma(x_w2, py_w2, w2, h2, tile2, eh_chao_base=False))
                x_w2 += 340.0
                passo_idx += 1

            plat_saida_2 = Plataforma(
                largura_mundo - 340.0,
                max(y_min_seguro, self.pos_y_chao - self.altura_worm_walk_boss - 34.0),
                w2,
                h2,
                tile2,
                eh_chao_base=False,
            )
            lista.append(plat_saida_2)
            self._plat_saida = plat_saida_2

        elif numero_fase == 3:
            x_seq = 380.0
            nivel = 0
            while x_seq < 4360.0:
                if nivel % 3 == 0:
                    py_seq = max(y_min_seguro, self.pos_y_chao - h3 - 64.0)
                    lista.append(Plataforma(x_seq, py_seq, w3, h3, tile3, eh_chao_base=False))
                elif nivel % 3 == 1:
                    py_seq = max(y_min_seguro, self.pos_y_chao - h2 - 96.0)
                    lista.append(Plataforma(x_seq, py_seq, w2, h2, tile2, eh_chao_base=False))
                else:
                    py_seq = max(y_min_seguro, self.pos_y_chao - h1 - 128.0)
                    lista.append(Plataforma(x_seq, py_seq, w1, h1, tile1, eh_chao_base=False))
                x_seq += 400.0
                nivel += 1

            plat_saida_3 = Plataforma(
                4560.0,
                max(y_min_seguro, self.pos_y_chao - h2 - 84.0),
                w2,
                h2,
                tile2,
                eh_chao_base=False,
            )
            lista.append(plat_saida_3)
            self._plat_saida = plat_saida_3

        elif numero_fase == 4:
            self._plat_saida = None

        return lista

    def _montar_inimigos_fase(self, numero_fase, largura_mundo):
        inimigos = []
        self.miniboss = None
        self.worm_boss_f2 = None
        self.boss_final = None

        if numero_fase == 1:
            if self._primeira_plat is not None:
                worm_plat_1 = Worm(
                    self._primeira_plat.x + 20.0,
                    self.pos_y_chao,
                    self._cache,
                    vida_maxima=VIDA_WORM,
                    direcao_direita=True,
                    raio_patrulha=self._primeira_plat.width * 0.5,
                    plataforma_inicial=self._primeira_plat,
                )
                worm_plat_1.patrulhar_plataforma_fixa = True
                inimigos.append(worm_plat_1)

            x_atual = 760.0
            limite_spawn = 4050.0
            idx = 0
            while x_atual <= limite_spawn:
                if idx % 3 == 2:
                    inimigos.append(
                        BlueFly(
                            x_atual,
                            self.pos_y_chao - 95.0,
                            self._cache,
                            vida_maxima=VIDA_BLUE_FLY,
                            direcao_direita=(idx % 2 == 0),
                            raio_patrulha=180.0,
                        )
                    )
                else:
                    inimigos.append(
                        Worm(
                            x_atual,
                            self.pos_y_chao,
                            self._cache,
                            vida_maxima=VIDA_WORM,
                            direcao_direita=(idx % 2 == 0),
                            raio_patrulha=150.0,
                        )
                    )
                x_atual += 420.0
                idx += 1

            self.miniboss = MinibossFly(
                x_centro=4360.0,
                pos_y_chao=self.pos_y_chao,
                cache_render=self._cache,
                largura_area=520.0,
            )
            inimigos.append(self.miniboss)

        elif numero_fase == 2:
            if self._primeira_plat is not None:
                mush_plat_2 = Mushroom(
                    self._primeira_plat.x + 20.0,
                    self.pos_y_chao,
                    self._cache,
                    vida_maxima=VIDA_MUSHROOM,
                    direcao_direita=True,
                    raio_patrulha=self._primeira_plat.width * 0.5,
                    plataforma_inicial=self._primeira_plat,
                )
                mush_plat_2.patrulhar_plataforma_fixa = True
                inimigos.append(mush_plat_2)

            metade_f2 = largura_mundo * 0.5
            x_bloco = 740.0
            slot = 0
            while x_bloco + 260.0 < metade_f2 - 120.0:
                inimigos.append(
                    Mushroom(
                        x_bloco,
                        self.pos_y_chao,
                        self._cache,
                        vida_maxima=VIDA_MUSHROOM,
                        direcao_direita=(slot % 2 == 0),
                        raio_patrulha=150.0,
                    )
                )
                inimigos.append(
                    BlueFly(
                        x_bloco + 260.0,
                        self.pos_y_chao - 105.0,
                        self._cache,
                        vida_maxima=VIDA_BLUE_FLY,
                        direcao_direita=(slot % 2 == 1),
                        raio_patrulha=185.0,
                    )
                )
                x_bloco += 560.0
                slot += 1

            self.worm_boss_f2 = MinibossWormFase2(
                x_inicio_metade=metade_f2,
                largura_fase_2=largura_mundo,
                pos_y_chao=self.pos_y_chao,
                cache_render=self._cache,
            )
            inimigos.append(self.worm_boss_f2)

        elif numero_fase == 3:
            x_f3 = 380.0
            idx_f3 = 0
            while x_f3 < 4420.0:
                if idx_f3 % 2 == 0:
                    inimigos.append(
                        Mushroom(
                            x_f3,
                            self.pos_y_chao,
                            self._cache,
                            vida_maxima=VIDA_MUSHROOM,
                            direcao_direita=(idx_f3 % 4 == 0),
                            raio_patrulha=150.0,
                        )
                    )
                else:
                    inimigos.append(
                        Worm(
                            x_f3,
                            self.pos_y_chao,
                            self._cache,
                            vida_maxima=VIDA_WORM,
                            direcao_direita=(idx_f3 % 4 == 1),
                            raio_patrulha=150.0,
                        )
                    )
                inimigos.append(
                    BlueFly(
                        x_f3 + 220.0,
                        self.pos_y_chao - 115.0,
                        self._cache,
                        vida_maxima=VIDA_BLUE_FLY,
                        direcao_direita=(idx_f3 % 2 == 1),
                        raio_patrulha=200.0,
                    )
                )
                x_f3 += 520.0
                idx_f3 += 1

        elif numero_fase == 4:
            self.boss_final = BossFinalFrog(
                pos_y_chao=self.pos_y_chao,
                cache_render=self._cache,
                largura_fase=largura_mundo,
            )
            inimigos.append(self.boss_final)

        for inim in inimigos:
            if hasattr(inim, "definir_limite_mundo"):
                inim.definir_limite_mundo(largura_mundo)

        return inimigos

    def _criar_gatilho_fim_de_plataforma(self, numero_fase, fase_destino):
        if fase_destino is None or self._plat_saida is None:
            return None

        plat_final = self._plat_saida
        gatilho_w = 28.0
        gatilho_h = 34.0
        gx = (plat_final.x + plat_final.width) - gatilho_w - 4.0
        gy = plat_final.y - gatilho_h
        return GatilhoFase(gx, gy, gatilho_w, gatilho_h, fase_destino)

    def carregar_fase(self, numero_fase):
        if numero_fase not in self.fases:
            return False

        self.fase_atual = numero_fase
        info = self.fases[numero_fase]
        self.largura_mundo_atual = info["largura_mundo"]

        self.parallax = ParallaxSystem()
        self.parallax.add_layer(info["fundo"], fator_velocidade=info["fator_parallax"])
        self.img_chao = GameImage(info["chao"])

        self.dados_mapa = self._carregar_linhas_mapa(info["mapa"])
        self.plataformas = self._montar_plataformas_fase(
            numero_fase, self.dados_mapa, info["chao"], self.largura_mundo_atual
        )
        self.acessorios = self._montar_acessorios_fase(numero_fase, self.largura_mundo_atual)
        self.inimigos = self._montar_inimigos_fase(numero_fase, self.largura_mundo_atual)
        self.gatilho = self._criar_gatilho_fim_de_plataforma(
            numero_fase, fase_destino=info["proximo"]
        )
        return True

    def verificar_gatilho(self, jogador, camera):
        if self.gatilho is not None and self.gatilho.jogador_ativou(jogador):
            destino = self.gatilho.fase_destino
            self.carregar_fase(destino)
            camera.set_world_bounds(self.largura_mundo_atual, self.pos_y_chao + self.altura_chao)
            jogador.x = 50.0
            jogador.y = self.pos_y_chao - jogador.height
            jogador.vel_y = 0.0
            jogador.no_chao = True
            camera.x = 0.0
            return destino
        return None

    def draw_acessorios_fundo(self, janela, camera):
        cam_x = camera.x
        cam_dir = cam_x + janela.largura
        for acc in self.acessorios:
            if acc.em_frente_plataforma:
                continue
            if (acc.x + acc.width) >= cam_x - 60 and acc.x <= cam_dir + 60:
                acc.draw(janela, camera)

    def draw_acessorios_frente(self, janela, camera):
        cam_x = camera.x
        cam_dir = cam_x + janela.largura
        for acc in self.acessorios:
            if not acc.em_frente_plataforma:
                continue
            if (acc.x + acc.width) >= cam_x - 60 and acc.x <= cam_dir + 60:
                acc.draw(janela, camera)

    def draw_plataformas(self, janela, camera):
        cam_x = camera.x
        cam_dir = cam_x + janela.largura
        for plat in self.plataformas:
            if plat.eh_chao_base:
                continue
            if (plat.x + plat.width) >= cam_x and plat.x <= cam_dir:
                plat.draw(janela, camera)

    def draw_inimigos(self, janela, camera):
        cam_x = camera.x
        cam_dir = cam_x + janela.largura
        for inimigo in self.inimigos:
            if not inimigo.vivo:
                continue
            if (inimigo.x + inimigo.width) >= cam_x - 240 and inimigo.x <= cam_dir + 240:
                inimigo.draw(janela, camera)

    def draw_gatilho(self, janela, camera):
        if self.gatilho is not None:
            self.gatilho.draw(janela, camera)
