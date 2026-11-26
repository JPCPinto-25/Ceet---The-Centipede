import math
import pygame
from PPlay.sprite import Sprite
from config import (
    CAMINHO_BLUE_FLY_BOSS,
    FRAMES_BLUE_FLY_BOSS,
    VIDA_MINIBOSS_FLY,
)


class MinibossFly:
    def __init__(self, x_centro, pos_y_chao, cache_render, largura_area=540.0):
        self._cache = cache_render
        self.pos_y_chao = float(pos_y_chao)
        self.vida_maxima = float(VIDA_MINIBOSS_FLY)
        self.vida = float(VIDA_MINIBOSS_FLY)
        self.vivo = True
        self.dano_contato = 15
        self.eh_chefe = True
        self.voa = True
        self._ultimo_id_ataque_recebido = None

        self.sprite_anim = Sprite(CAMINHO_BLUE_FLY_BOSS, total_frames=FRAMES_BLUE_FLY_BOSS)
        self.sprite_anim.set_total_duration(360)
        self.atual = self.sprite_anim

        metade_area = max(220.0, float(largura_area) * 0.5)
        self.arena_inicio = max(300.0, float(x_centro) - metade_area)
        self.arena_fim = float(x_centro) + metade_area
        self.arena_ativa = False

        self.x = float(x_centro)
        self.y_base = self.pos_y_chao - 95.0
        self.y = self.y_base
        self.tempo_voo = 0.0
        self.direcao_direita = False
        self.vel_x = 125.0

    @property
    def width(self):
        return max(1.0, self.atual.image.get_width() / max(1, FRAMES_BLUE_FLY_BOSS))

    @property
    def height(self):
        return max(1.0, self.atual.image.get_height())

    def get_hitbox(self):
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
            self.arena_ativa = False
        return True

    def update(self, janela, plataformas, jogador=None):
        if not self.vivo:
            return

        dt = janela.delta_time()
        if jogador is not None and (jogador.x + jogador.width) >= self.arena_inicio:
            self.arena_ativa = True

        self.tempo_voo += dt
        limite_esq = self.arena_inicio
        limite_dir = max(limite_esq + 40.0, self.arena_fim - self.width)

        direcao = 1.0 if self.direcao_direita else -1.0
        self.x += direcao * self.vel_x * dt

        if self.x <= limite_esq:
            self.x = limite_esq
            self.direcao_direita = True
        elif self.x >= limite_dir:
            self.x = limite_dir
            self.direcao_direita = False

        self.y = max(44.0, self.y_base + math.sin(self.tempo_voo * 4.5) * 16.0)
        self.atual.update()

    def draw(self, janela, camera):
        if not self.vivo or self.atual is None:
            return

        rx = camera.transform_x(self.x)
        ry = camera.transform_y(self.y)

        total_frames = max(1, FRAMES_BLUE_FLY_BOSS)
        frame_w = max(1, self.atual.image.get_width() // total_frames)
        frame_h = max(1, self.atual.image.get_height())
        frame_idx = int(
            getattr(self.atual, "curr_frame", getattr(self.atual, "frame_atual", 0))
        )
        frame_idx = max(0, min(frame_idx, total_frames - 1))

        rect_frame = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)
        frame_surf = self.atual.image.subsurface(rect_frame).copy()
        if not self.direcao_direita:
            frame_surf = pygame.transform.flip(frame_surf, True, False)

        janela.screen.blit(frame_surf, (rx, ry))

    def draw_barra_topo(self, janela):
        if not self.vivo or not self.arena_ativa:
            return

        largura_barra = 220
        altura_barra = 10
        by = 10
        bx = (janela.largura - largura_barra) // 2
        proporcao = max(0.0, min(1.0, self.vida / max(1.0, self.vida_maxima)))

        pygame.draw.rect(janela.screen, (20, 24, 34), (bx, by, largura_barra, altura_barra))
        pygame.draw.rect(
            janela.screen,
            (70, 165, 245),
            (bx, by, int(largura_barra * proporcao), altura_barra),
        )
        pygame.draw.rect(
            janela.screen, (215, 235, 255), (bx, by, largura_barra, altura_barra), width=1
        )

        texto_hp = f"FLY BOSS: {int(math.ceil(self.vida))}/{int(self.vida_maxima)}"
        sombra, surf = self._cache.obter_texto_com_sombra(
            "miniboss_hp", texto_hp, (220, 240, 255)
        )
        tx = (janela.largura - surf.get_width()) // 2
        ty = by + altura_barra + 3
        janela.screen.blit(sombra, (tx + 1, ty + 1))
        janela.screen.blit(surf, (tx, ty))
