import pygame
from PPlay.sprite import Sprite
from config import (
    CAMINHO_BLUE_FLY_ATTACK,
    CAMINHO_MUSHROOM_CRUSHED,
    CAMINHO_MUSHROOM_RUN,
    CAMINHO_MUSHROOM_WALK,
    CAMINHO_WORM_WALK,
    FRAMES_BLUE_FLY_ATTACK,
    FRAMES_MUSHROOM_CRUSHED,
    FRAMES_MUSHROOM_RUN,
    FRAMES_MUSHROOM_WALK,
    FRAMES_WORM_WALK,
    LARGURA_MUNDO,
    VIDA_BLUE_FLY,
    VIDA_MUSHROOM,
    VIDA_WORM,
)
from enemy_movement import (
    atualizar_movimento_blue_fly,
    atualizar_movimento_mushroom,
    atualizar_movimento_worm,
)


class InimigoBase:
    def __init__(
        self,
        x,
        pos_y_chao,
        cache_render,
        vida_maxima,
        dano_contato=10,
        direcao_direita=True,
        raio_patrulha=220.0,
    ):
        self._cache = cache_render
        self.pos_y_chao = float(pos_y_chao)
        self.vida_maxima = float(vida_maxima)
        self.vida = float(vida_maxima)
        self.vivo = True
        self.dano_contato = int(dano_contato)
        self._ultimo_id_ataque_recebido = None

        self.direcao_direita = bool(direcao_direita)
        self.x_origem = float(x)
        self.raio_patrulha = float(raio_patrulha)
        self.x_min = max(0.0, self.x_origem - self.raio_patrulha)
        self.x_max = min(float(LARGURA_MUNDO), self.x_origem + self.raio_patrulha)

        self.x = float(x)
        self.y = float(pos_y_chao)
        self.atual = None
        self.frames_map = {}
        self.estado = "default"
        self.voa = False
        self.plataforma_atual = None
        self.patrulhar_plataforma_fixa = False
        self._cooldown_colisao_entidade = 0.0

    def definir_limite_mundo(self, largura_mundo):
        self.x_max = min(float(largura_mundo), self.x_origem + self.raio_patrulha)

    @property
    def total_frames_atual(self):
        return max(1, self.frames_map.get(self.estado, 1))

    @property
    def width(self):
        if self.atual is None:
            return 1.0
        return max(1.0, self.atual.image.get_width() / self.total_frames_atual)

    @property
    def height(self):
        if self.atual is None:
            return 1.0
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
        return True

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

        rect_frame = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)
        frame_surf = sheet.subsurface(rect_frame).copy()
        if not self.direcao_direita:
            frame_surf = pygame.transform.flip(frame_surf, True, False)

        janela.screen.blit(frame_surf, (rx, ry))


class Worm(InimigoBase):
    def __init__(
        self,
        x,
        pos_y_chao,
        cache_render,
        vida_maxima=VIDA_WORM,
        direcao_direita=True,
        raio_patrulha=200.0,
        plataforma_inicial=None,
    ):
        super().__init__(
            x,
            pos_y_chao,
            cache_render,
            vida_maxima=vida_maxima,
            dano_contato=10,
            direcao_direita=direcao_direita,
            raio_patrulha=raio_patrulha,
        )
        self.frames_map = {"walk": FRAMES_WORM_WALK}
        self.sprite_walk = Sprite(CAMINHO_WORM_WALK, total_frames=FRAMES_WORM_WALK)
        self.sprite_walk.set_total_duration(700)

        self.estado = "walk"
        self.atual = self.sprite_walk
        self.vel_x = 55.0
        self.plataforma_atual = plataforma_inicial

        if self.plataforma_atual is not None:
            self.y = min(self.pos_y_chao - self.height, self.plataforma_atual.y - self.height)
        else:
            self.y = self.pos_y_chao - self.height

    def update(self, janela, plataformas, jogador=None, outros_inimigos=None):
        if not self.vivo:
            return
        dt = janela.delta_time()
        atualizar_movimento_worm(self, dt, plataformas, outros_inimigos or [])
        self.atual.update()


class Mushroom(InimigoBase):
    def __init__(
        self,
        x,
        pos_y_chao,
        cache_render,
        vida_maxima=VIDA_MUSHROOM,
        direcao_direita=True,
        raio_patrulha=220.0,
        plataforma_inicial=None,
    ):
        super().__init__(
            x,
            pos_y_chao,
            cache_render,
            vida_maxima=vida_maxima,
            dano_contato=12,
            direcao_direita=direcao_direita,
            raio_patrulha=raio_patrulha,
        )
        self.frames_map = {
            "walk": FRAMES_MUSHROOM_WALK,
            "run": FRAMES_MUSHROOM_RUN,
            "crushed": FRAMES_MUSHROOM_CRUSHED,
        }

        self.sprite_walk = Sprite(CAMINHO_MUSHROOM_WALK, total_frames=FRAMES_MUSHROOM_WALK)
        self.sprite_walk.set_total_duration(800)

        self.sprite_run = Sprite(CAMINHO_MUSHROOM_RUN, total_frames=FRAMES_MUSHROOM_RUN)
        self.sprite_run.set_total_duration(600)

        self.sprite_crushed = Sprite(
            CAMINHO_MUSHROOM_CRUSHED, total_frames=FRAMES_MUSHROOM_CRUSHED
        )
        self.sprite_crushed.set_total_duration(500)

        self.sprites_map = {
            "walk": self.sprite_walk,
            "run": self.sprite_run,
            "crushed": self.sprite_crushed,
        }

        self.estado = "walk"
        self.atual = self.sprite_walk
        self.vel_walk = 58.0
        self.vel_run = 105.0
        self.plataforma_atual = plataforma_inicial

        if self.plataforma_atual is not None:
            self.y = min(self.pos_y_chao - self.height, self.plataforma_atual.y - self.height)
        else:
            self.y = self.pos_y_chao - self.height

    def _set_estado(self, novo_estado):
        if self.estado != novo_estado and novo_estado in self.sprites_map:
            self.estado = novo_estado
            self.atual = self.sprites_map[novo_estado]
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(0)

    def update(self, janela, plataformas, jogador=None, outros_inimigos=None):
        if not self.vivo:
            return
        dt = janela.delta_time()
        atualizar_movimento_mushroom(self, dt, plataformas, jogador, outros_inimigos or [])
        self.atual.update()


class BlueFly(InimigoBase):
    def __init__(
        self,
        x,
        y_base,
        cache_render,
        vida_maxima=VIDA_BLUE_FLY,
        direcao_direita=True,
        raio_patrulha=200.0,
    ):
        super().__init__(
            x,
            y_base + 80.0,
            cache_render,
            vida_maxima=vida_maxima,
            dano_contato=10,
            direcao_direita=direcao_direita,
            raio_patrulha=raio_patrulha,
        )
        self.voa = True
        self.frames_map = {"attack": FRAMES_BLUE_FLY_ATTACK}
        self.sprite_attack = Sprite(
            CAMINHO_BLUE_FLY_ATTACK, total_frames=FRAMES_BLUE_FLY_ATTACK
        )
        self.sprite_attack.set_total_duration(420)

        self.estado = "attack"
        self.atual = self.sprite_attack
        self.y_base = float(y_base)
        self.y = float(y_base)
        self.vel_x = 92.0
        self.tempo_voo = 0.0

    def update(self, janela, plataformas, jogador=None, outros_inimigos=None):
        if not self.vivo:
            return
        dt = janela.delta_time()
        atualizar_movimento_blue_fly(self, dt, jogador, outros_inimigos or [])
        self.atual.update()
