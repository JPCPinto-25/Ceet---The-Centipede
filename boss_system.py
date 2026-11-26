import math
import pygame
from PPlay.sprite import Sprite
from config import (
    CAMINHO_FROG_IDLE,
    CAMINHO_FROG_JUMPING,
    CAMINHO_FROG_PREPARING,
    FRAMES_FROG_IDLE,
    FRAMES_FROG_JUMPING,
    FRAMES_FROG_PREPARING,
    LARGURA_FASE_4,
    LARGURA_JANELA,
    VIDA_FROG,
)


class BossFinalFrog:
    def __init__(self, pos_y_chao, cache_render, largura_fase=LARGURA_FASE_4):
        self._cache = cache_render
        self.pos_y_chao = float(pos_y_chao)
        self.largura_fase = float(largura_fase)

        self.arena_inicio = max(0.0, self.largura_fase - (2.0 * float(LARGURA_JANELA)))
        self.arena_fim = max(
            self.arena_inicio + float(LARGURA_JANELA),
            self.largura_fase - float(LARGURA_JANELA),
        )

        self.vida_maxima = float(VIDA_FROG)
        self.vida = float(VIDA_FROG)
        self.vivo = True
        self.arena_ativa = False
        self.venceu_por_tempo = False
        self._ultimo_id_ataque_recebido = None

        self.frames_map = {
            "idle": FRAMES_FROG_IDLE,
            "preparing": FRAMES_FROG_PREPARING,
            "jumping": FRAMES_FROG_JUMPING,
        }

        self.sprite_idle = Sprite(CAMINHO_FROG_IDLE, total_frames=FRAMES_FROG_IDLE)
        self.sprite_idle.set_total_duration(800)

        # Preparo mais calmo antes de saltar
        self.duracao_preparo = 1.15
        self.sprite_preparing = Sprite(
            CAMINHO_FROG_PREPARING, total_frames=FRAMES_FROG_PREPARING
        )
        self.sprite_preparing.set_total_duration(int(self.duracao_preparo * 1000))

        # Mais tempo no ar durante o pulo
        self.duracao_pulo = 1.55
        self.sprite_jumping = Sprite(
            CAMINHO_FROG_JUMPING, total_frames=FRAMES_FROG_JUMPING
        )
        self.sprite_jumping.set_total_duration(int(self.duracao_pulo * 1000))

        self.sprites_map = {
            "idle": self.sprite_idle,
            "preparing": self.sprite_preparing,
            "jumping": self.sprite_jumping,
        }

        self.estado = "idle"
        self.atual = self.sprite_idle

        self.x = self.arena_inicio + ((self.arena_fim - self.arena_inicio) * 0.65)
        self.y = self.pos_y_chao - self.height
        self.direcao_direita = False

        self.tempo_estado = 0.0
        self.x_inicio_pulo = self.x
        self.y_inicio_pulo = self.y
        self.x_alvo_pulo = self.x
        self.tempo_pulo = 0.0
        self.y_pico_desejado = 34.0
        self.pulou_neste_salto = False

    @property
    def enraivecido(self):
        return self.vida <= 100.0

    @property
    def tempo_idle_pos_pouso(self):
        # Pausas maiores para reduzir a agressividade
        return 1.25 if self.enraivecido else 1.65

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
    def dano_contato(self):
        return 20 if self.pulou_neste_salto else 15

    def get_hitbox(self):
        return pygame.Rect(
            int(self.x), int(self.y), max(1, int(self.width)), max(1, int(self.height))
        )

    def _set_estado(self, novo_estado):
        if self.estado != novo_estado and novo_estado in self.sprites_map:
            self.estado = novo_estado
            self.atual = self.sprites_map[novo_estado]
        if hasattr(self.atual, "set_curr_frame"):
            self.atual.set_curr_frame(0)
        self.tempo_estado = 0.0

    def receber_dano(self, quantidade, id_ataque=None):
        if not self.vivo or quantidade <= 0:
            return False
        if id_ataque is not None and id_ataque == self._ultimo_id_ataque_recebido:
            return False

        self._ultimo_id_ataque_recebido = id_ataque
        self.vida = max(0.0, self.vida - quantidade)
        if self.vida <= 0.0:
            self.vivo = False
            self.arena_ativa = False
        return True

    def restringir_jogador_na_arena(self, jogador, camera):
        if not self.vivo:
            return

        if (jogador.x + jogador.width) >= self.arena_inicio:
            self.arena_ativa = True

        if self.arena_ativa:
            camera.x = self.arena_inicio
            jogador.x = max(
                self.arena_inicio,
                min(jogador.x, self.arena_fim - jogador.width),
            )

    def _iniciar_pulo_mirando_jogador(self, jogador):
        self._set_estado("jumping")
        self.tempo_pulo = 0.0
        self.pulou_neste_salto = True
        self.x_inicio_pulo = self.x
        self.y_inicio_pulo = self.pos_y_chao - self.height

        if jogador is not None:
            alvo_centro = jogador.x + (jogador.width * 0.5)
            self.x_alvo_pulo = max(
                self.arena_inicio,
                min(self.arena_fim - self.width, alvo_centro - (self.width * 0.5)),
            )
            self.direcao_direita = (self.x_alvo_pulo + self.width * 0.5) >= (
                self.x + self.width * 0.5
            )
        else:
            self.direcao_direita = not self.direcao_direita
            self.x_alvo_pulo = (
                self.arena_fim - self.width - 20.0
                if self.direcao_direita
                else self.arena_inicio + 20.0
            )

    def _calcular_y_parabolico_no_ar(self, t_norm):
        y_chao = self.pos_y_chao - self.height
        y_inicio = min(self.y_inicio_pulo, y_chao)
        y_pico = min(self.y_pico_desejado, y_chao - 14.0)

        # Curva mais ampla no alto para estender o tempo suspenso no ar
        if t_norm <= 0.52:
            fase_t = t_norm / 0.52
            return y_inicio - (y_inicio - y_pico) * (fase_t ** 0.65)
        else:
            desc_t = (t_norm - 0.52) / 0.48
            return y_pico + (y_chao - y_pico) * (desc_t ** 1.45)

    def _atualizar_direcao_alvo(self, jogador):
        if jogador is not None:
            self.direcao_direita = (jogador.x + jogador.width * 0.5) >= (
                self.x + self.width * 0.5
            )

    def update(self, janela, jogador):
        if not self.vivo:
            return

        dt = janela.delta_time()

        if jogador is not None and (jogador.x + jogador.width) >= self.arena_inicio:
            self.arena_ativa = True

        if not self.arena_ativa:
            self._set_estado("idle")
            self.y = self.pos_y_chao - self.height
            self._atualizar_direcao_alvo(jogador)
            self.atual.update()
            return

        self.tempo_estado += dt

        if self.estado == "idle":
            self.y = self.pos_y_chao - self.height
            self.pulou_neste_salto = False
            self._atualizar_direcao_alvo(jogador)
            if self.tempo_estado >= self.tempo_idle_pos_pouso:
                self._set_estado("preparing")
            self.atual.update()

        elif self.estado == "preparing":
            self.y = self.pos_y_chao - self.height
            self._atualizar_direcao_alvo(jogador)

            progresso = min(0.999, self.tempo_estado / max(0.01, self.duracao_preparo))
            frame_idx = int(progresso * FRAMES_FROG_PREPARING)
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(frame_idx)

            if self.tempo_estado >= self.duracao_preparo:
                self._iniciar_pulo_mirando_jogador(jogador)

        elif self.estado == "jumping":
            self.tempo_pulo += dt
            t_norm = min(1.0, self.tempo_pulo / self.duracao_pulo)

            self.x = self.x_inicio_pulo + (self.x_alvo_pulo - self.x_inicio_pulo) * t_norm
            self.y = self._calcular_y_parabolico_no_ar(t_norm)
            self.direcao_direita = (self.x_alvo_pulo + self.width * 0.5) >= (
                self.x + self.width * 0.5
            )

            if self.x <= self.arena_inicio:
                self.x = self.arena_inicio
            elif self.x >= (self.arena_fim - self.width):
                self.x = self.arena_fim - self.width

            progresso_pulo = min(0.999, t_norm)
            frame_pulo = int(progresso_pulo * FRAMES_FROG_JUMPING)
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(frame_pulo)

            if self.tempo_pulo >= self.duracao_pulo:
                self.y = self.pos_y_chao - self.height
                self.pulou_neste_salto = False
                self._set_estado("idle")

    def draw(self, janela, camera):
        if not self.vivo or self.atual is None:
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

        rect_quadro = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)
        quadro_unico = sheet.subsurface(rect_quadro).copy()

        if self.direcao_direita:
            quadro_unico = pygame.transform.flip(quadro_unico, True, False)

        janela.screen.blit(quadro_unico, (rx, ry))

    def draw_barra_topo(self, janela):
        if not self.vivo:
            return

        largura_barra = 260
        altura_barra = 12
        by = 10
        bx = (janela.largura - largura_barra) // 2
        proporcao = max(0.0, min(1.0, self.vida / max(1.0, self.vida_maxima)))

        pygame.draw.rect(janela.screen, (30, 18, 22), (bx, by, largura_barra, altura_barra))
        pygame.draw.rect(
            janela.screen,
            (225, 45, 65),
            (bx, by, int(largura_barra * proporcao), altura_barra),
        )
        pygame.draw.rect(
            janela.screen, (245, 220, 225), (bx, by, largura_barra, altura_barra), width=1
        )

        texto_hp = f"BOSS FROG: {int(math.ceil(self.vida))}/{int(self.vida_maxima)}"
        sombra, surf = self._cache.obter_texto_com_sombra(
            "boss_hp", texto_hp, (255, 235, 235)
        )
        tx = (janela.largura - surf.get_width()) // 2
        ty = by + altura_barra + 3
        janela.screen.blit(sombra, (tx + 1, ty + 1))
        janela.screen.blit(surf, (tx, ty))
