import math
import pygame
from PPlay.sprite import Sprite
from config import (
    CAMINHO_WORM_ATTACK_BOSS,
    CAMINHO_WORM_RISE_BOSS,
    CAMINHO_WORM_WALK_BOSS,
    FRAMES_WORM_ATTACK_BOSS,
    FRAMES_WORM_RISE_BOSS,
    FRAMES_WORM_WALK_BOSS,
    LARGURA_JANELA,
    VEL_PLAYER,
    VIDA_WORM_FASE2_BOSS,
)


class MinibossWormFase2:
    def __init__(self, x_inicio_metade, largura_fase_2, pos_y_chao, cache_render):
        self._cache = cache_render
        self.pos_y_chao = float(pos_y_chao)
        self.x_inicio_metade = float(x_inicio_metade)
        self.x_inicio_cacada = 2500.0
        self.largura_fase_2 = float(largura_fase_2)

        largura_area_worm = float(LARGURA_JANELA) * 2.0
        centro_area = max(
            self.x_inicio_cacada + largura_area_worm * 0.5,
            self.largura_fase_2 - largura_area_worm * 0.5 - 220.0,
        )
        self.arena_inicio = max(self.x_inicio_cacada, centro_area - largura_area_worm * 0.5)
        self.arena_fim = min(self.largura_fase_2 - 80.0, self.arena_inicio + largura_area_worm)

        self.vida_maxima = float(VIDA_WORM_FASE2_BOSS)
        self.vida = float(VIDA_WORM_FASE2_BOSS)
        self.vivo = True
        self.dano_contato = 20
        self.eh_chefe = True
        self.voa = False
        self._ultimo_id_ataque_recebido = None

        self.vel_cacada = max(40.0, float(VEL_PLAYER) - 5.0)

        self.sprite_walk = Sprite(CAMINHO_WORM_WALK_BOSS, total_frames=FRAMES_WORM_WALK_BOSS)
        self.sprite_walk.set_total_duration(420)

        self.sprite_rise = Sprite(CAMINHO_WORM_RISE_BOSS, total_frames=FRAMES_WORM_RISE_BOSS)
        self.sprite_rise.set_total_duration(240)

        self.sprite_attack = Sprite(
            CAMINHO_WORM_ATTACK_BOSS, total_frames=FRAMES_WORM_ATTACK_BOSS
        )
        self.sprite_attack.set_total_duration(720)

        self.frames_map = {
            "rising": FRAMES_WORM_RISE_BOSS,
            "chasing": FRAMES_WORM_WALK_BOSS,
            "burrowing": FRAMES_WORM_ATTACK_BOSS,
        }
        self.sprites_map = {
            "rising": self.sprite_rise,
            "chasing": self.sprite_walk,
            "burrowing": self.sprite_attack,
        }

        self.estado = "rising"
        self.atual = self.sprite_rise
        self.tempo_estado = 0.0
        self.duracao_rise = 0.20
        self.duracao_burrow = 0.72

        self.x = self.arena_inicio + 120.0
        self.y = self.pos_y_chao - self.height
        self.x_alvo = self.x
        self._dir_movimento = 1.0
        self.direcao_direita = True
        self._ciclo_iniciado = False
        self._transicao_concluida = False

    @property
    def ativo_na_fase(self):
        return self.vivo

    @property
    def total_frames_atual(self):
        return max(1, self.frames_map.get(self.estado, 1))

    @property
    def width(self):
        return max(1.0, self.atual.image.get_width() / self.total_frames_atual)

    @property
    def height(self):
        return max(1.0, self.atual.image.get_height())

    @property
    def altura_walk_sprite(self):
        return max(1.0, self.sprite_walk.image.get_height())

    def get_hitbox(self):
        if not self._ciclo_iniciado:
            return pygame.Rect(0, 0, 0, 0)
        if self.estado == "burrowing" and self.tempo_estado > self.duracao_burrow * 0.8:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(
            int(self.x), int(self.y), max(1, int(self.width)), max(1, int(self.height))
        )

    def receber_dano(self, quantidade, id_ataque=None):
        if not self.vivo or quantidade <= 0:
            return False
        if id_ataque is not None and id_ataque == self._ultimo_id_ataque_recebido:
            return False
        self._ultimo_id_ataque_recebido = id_ataque
        self.vida = max(0.0, self.vida - quantidade)
        if self.vida <= 0.0:
            self.vivo = False
        return True

    def _mudar_estado(self, novo_estado):
        self.estado = novo_estado
        self.atual = self.sprites_map[novo_estado]
        if hasattr(self.atual, "set_curr_frame"):
            self.atual.set_curr_frame(0)
        self.tempo_estado = 0.0
        self._transicao_concluida = False

    def _iniciar_surgimento_perto_do_player(self, jogador):
        ponto_player_x = jogador.x if jogador is not None else self.x
        ponto_player_x = max(
            self.arena_inicio, min(self.arena_fim - self.width, ponto_player_x)
        )

        lado_dir = ponto_player_x + 200.0
        lado_esq = ponto_player_x - 200.0
        if lado_dir <= (self.arena_fim - self.width):
            pos_spawn = lado_dir
        elif lado_esq >= self.arena_inicio:
            pos_spawn = lado_esq
        else:
            pos_spawn = max(
                self.arena_inicio,
                min(
                    self.arena_fim - self.width,
                    ponto_player_x - math.copysign(200.0, ponto_player_x - self.x),
                ),
            )

        self.x = pos_spawn
        self.x_alvo = ponto_player_x
        diff_inicial = self.x_alvo - self.x
        self._dir_movimento = 1.0 if diff_inicial >= 0.0 else -1.0
        self.direcao_direita = self._dir_movimento >= 0.0
        self._mudar_estado("rising")

    def update(self, janela, jogador):
        if not self.vivo:
            return

        dt = janela.delta_time()

        if jogador is not None and (jogador.x + jogador.width) < self.x_inicio_cacada:
            self.y = self.pos_y_chao - self.height
            return

        if not self._ciclo_iniciado:
            self._ciclo_iniciado = True
            self._iniciar_surgimento_perto_do_player(jogador)

        self.tempo_estado += dt
        self.y = self.pos_y_chao - self.height

        if self.estado == "rising":
            total_f = FRAMES_WORM_RISE_BOSS
            progresso = min(1.0, self.tempo_estado / max(0.01, self.duracao_rise))
            frame_idx = min(total_f - 1, int(progresso * total_f))
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(frame_idx)
            if progresso >= 1.0 and not self._transicao_concluida:
                self._transicao_concluida = True
                self._mudar_estado("chasing")

        elif self.estado == "chasing":
            if not self._transicao_concluida:
                dist_restante = (self.x_alvo - self.x) * self._dir_movimento
                passo = self._dir_movimento * self.vel_cacada * dt

                if dist_restante <= 2.0 or abs(passo) >= dist_restante:
                    self.x = self.x_alvo
                    self._transicao_concluida = True
                    self._mudar_estado("burrowing")
                else:
                    novo_x = max(
                        self.arena_inicio, min(self.arena_fim - self.width, self.x + passo)
                    )
                    bateu_borda = (
                        novo_x == self.arena_inicio or novo_x == self.arena_fim - self.width
                    ) and abs(novo_x - self.x) < 0.01
                    self.x = novo_x
                    if bateu_borda:
                        self._transicao_concluida = True
                        self._mudar_estado("burrowing")
                self.atual.update()

        elif self.estado == "burrowing":
            total_f = FRAMES_WORM_ATTACK_BOSS
            progresso = min(1.0, self.tempo_estado / max(0.01, self.duracao_burrow))
            frame_idx = min(total_f - 1, int(progresso * total_f))
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(frame_idx)
            if progresso >= 1.0 and not self._transicao_concluida:
                self._transicao_concluida = True
                self._iniciar_surgimento_perto_do_player(jogador)

    def draw(self, janela, camera):
        if not self.vivo or not self._ciclo_iniciado or self.atual is None:
            return

        rx = camera.transform_x(self.x)
        ry = camera.transform_y(self.y)

        total_frames = self.total_frames_atual
        sheet = self.atual.image
        frame_w = max(1, sheet.get_width() // total_frames)
        frame_h = max(1, sheet.get_height())

        frame_idx = int(
            getattr(self.atual, "curr_frame", getattr(self.atual, "frame_atual", 0))
        )
        frame_idx = max(0, min(frame_idx, total_frames - 1))

        rect_frame = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)
        frame_surf = sheet.subsurface(rect_frame).copy()
        if not self.direcao_direita:
            frame_surf = pygame.transform.flip(frame_surf, True, False)

        janela.screen.blit(frame_surf, (rx, ry))

    def draw_barra_topo(self, janela):
        if not self.vivo or not self._ciclo_iniciado:
            return

        largura_barra = 240
        altura_barra = 11
        by = 10
        bx = (janela.largura - largura_barra) // 2
        proporcao = max(0.0, min(1.0, self.vida / max(1.0, self.vida_maxima)))

        pygame.draw.rect(janela.screen, (34, 18, 16), (bx, by, largura_barra, altura_barra))
        pygame.draw.rect(
            janela.screen,
            (215, 75, 45),
            (bx, by, int(largura_barra * proporcao), altura_barra),
        )
        pygame.draw.rect(
            janela.screen, (250, 220, 210), (bx, by, largura_barra, altura_barra), width=1
        )

        texto_hp = f"WORM HUNTER: {int(math.ceil(self.vida))}/{int(self.vida_maxima)}"
        sombra, surf = self._cache.obter_texto_com_sombra(
            "worm_f2_hp", texto_hp, (255, 225, 215)
        )
        tx = (janela.largura - surf.get_width()) // 2
        ty = by + altura_barra + 3
        janela.screen.blit(sombra, (tx + 1, ty + 1))
        janela.screen.blit(surf, (tx, ty))
