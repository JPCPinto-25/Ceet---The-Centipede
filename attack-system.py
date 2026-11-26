import pygame
from PPlay.sprite import Sprite
from config import (
    CAMINHO_ATTACK,
    CAMINHO_ROLL_ATTACK,
    DANO_ATAQUE_PLAYER,
    DANO_ATAQUE_PULANDO,
    FRAMES_ATTACK,
    FRAMES_ROLL_ATTACK,
    LARGURA_MUNDO,
)


class SistemaAtaque:
    def __init__(self, cache_render):
        self._cache = cache_render

        self.sprite_attack = Sprite(CAMINHO_ATTACK, total_frames=FRAMES_ATTACK)
        self.sprite_attack.set_total_duration(320)

        self.sprite_roll_attack = Sprite(
            CAMINHO_ROLL_ATTACK, total_frames=FRAMES_ROLL_ATTACK
        )
        self.sprite_roll_attack.set_total_duration(320)

        self._flipped_attack_esq = self._cache.obter_espelhada_horizontal(
            "attack_esq", getattr(self.sprite_attack, "image", None)
        )
        self._flipped_roll_attack_dir = self._cache.obter_espelhada_horizontal(
            "roll_attack_dir", getattr(self.sprite_roll_attack, "image", None)
        )

        self.dano_chao = DANO_ATAQUE_PLAYER
        self.dano_pulo = DANO_ATAQUE_PULANDO

        self.atacando = False
        self.ataque_no_ar = False
        self.tempo_ataque = 0.0
        self.duracao_ataque = 0.32

        self.intervalo_min_ataque = 1.0
        self.timer_cooldown = 0.0

        self.tempo_sem_atacar = 0.0
        self.limite_tempo_combo = 3.0

        self.combo = 0
        self.max_combo = 10

        self.duracao_descanso = 10.0
        self.timer_descanso = 0.0
        self.sem_habilidade = False

        self.invencivel_timer = 0.0
        self.duracao_invencibilidade = 2.0
        self.distancia_avanco = 10.0
        self.id_ataque_atual = 0

    @property
    def esta_invencivel(self):
        return self.invencivel_timer > 0.0

    @property
    def dano_atual(self):
        return self.dano_pulo if self.ataque_no_ar else self.dano_chao

    def cancelar(self):
        self.atacando = False
        self.ataque_no_ar = False
        self.tempo_ataque = 0.0

    def tentar_iniciar(self, jogador, plataformas):
        if self.atacando or self.sem_habilidade or self.timer_descanso > 0.0:
            return False
        if self.timer_cooldown > 0.0:
            return False

        if self.combo >= self.max_combo:
            self.sem_habilidade = True
            self.timer_descanso = self.duracao_descanso
            return False

        self.combo += 1
        self.tempo_sem_atacar = 0.0
        self.timer_cooldown = self.intervalo_min_ataque

        self.atacando = True
        self.ataque_no_ar = not jogador.no_chao
        self.tempo_ataque = 0.0
        self.id_ataque_atual += 1
        self.invencivel_timer = max(self.invencivel_timer, self.duracao_invencibilidade)

        jogador._set_estado("roll_attack" if self.ataque_no_ar else "attack")

        direcao = 1.0 if jogador.direcao_direita else -1.0
        vel_ataque_x = direcao * jogador.vel_x_base
        jogador.x = max(
            0.0,
            min(
                jogador.x + direcao * self.distancia_avanco,
                LARGURA_MUNDO - jogador.width,
            ),
        )
        jogador._resolver_colisao_lateral(plataformas, vel_ataque_x)
        jogador.x = max(0.0, min(jogador.x, LARGURA_MUNDO - jogador.width))
        return True

    def update(self, dt):
        if self.invencivel_timer > 0.0:
            self.invencivel_timer = max(0.0, self.invencivel_timer - dt)

        if self.timer_cooldown > 0.0:
            self.timer_cooldown = max(0.0, self.timer_cooldown - dt)

        if self.sem_habilidade or self.timer_descanso > 0.0:
            self.timer_descanso = max(0.0, self.timer_descanso - dt)
            if self.timer_descanso <= 0.0:
                self.sem_habilidade = False
                self.combo = 0
                self.tempo_sem_atacar = 0.0
        elif self.combo > 0 and not self.atacando:
            self.tempo_sem_atacar += dt
            if self.tempo_sem_atacar >= self.limite_tempo_combo:
                self.combo = 0
                self.tempo_sem_atacar = 0.0

        if self.atacando:
            self.tempo_ataque += dt
            if self.tempo_ataque >= self.duracao_ataque:
                self.cancelar()

    def get_hitbox(self, jogador):
        if not self.atacando:
            return None

        largura_alcance = max(24.0, jogador.width * (0.9 if self.ataque_no_ar else 0.75))
        altura_alcance = jogador.height * (0.85 if self.ataque_no_ar else 0.7)
        y_hitbox = jogador.y + (jogador.height - altura_alcance) * 0.5
        x_hitbox = (
            (jogador.x + jogador.width - 4.0)
            if jogador.direcao_direita
            else (jogador.x - largura_alcance + 4.0)
        )

        return pygame.Rect(
            int(x_hitbox), int(y_hitbox), int(largura_alcance), int(altura_alcance)
        )

    def obter_imagem_e_rect(self, estado, direcao_direita, total_frames, frame_w, frame_h, frame_idx):
        if estado == "roll_attack":
            if direcao_direita and self._flipped_roll_attack_dir is not None:
                col_flip = (total_frames - 1) - frame_idx
                return (
                    self._flipped_roll_attack_dir,
                    pygame.Rect(col_flip * frame_w, 0, frame_w, frame_h),
                )
            return (
                self.sprite_roll_attack.image,
                pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h),
            )

        if not direcao_direita and self._flipped_attack_esq is not None:
            col_flip = (total_frames - 1) - frame_idx
            return (
                self._flipped_attack_esq,
                pygame.Rect(col_flip * frame_w, 0, frame_w, frame_h),
            )
        return (
            self.sprite_attack.image,
            pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h),
        )
