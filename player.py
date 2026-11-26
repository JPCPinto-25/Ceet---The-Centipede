import pygame
from PPlay.sprite import Sprite
from attack_system import SistemaAtaque
from config import *


class Player:
    def __init__(self, pos_y_chao, cache_render):
        self._cache = cache_render
        self.combate = SistemaAtaque(cache_render)

        self.frames_map = {
            "idle": FRAMES_IDLE,
            "roll": FRAMES_ROLL,
            "walk_right": FRAMES_WALK_RIGHT,
            "walk_left": FRAMES_WALK_LEFT,
            "attack": FRAMES_ATTACK,
            "roll_attack": FRAMES_ROLL_ATTACK,
        }

        self.sprite_idle = Sprite(CAMINHO_IDLE, total_frames=FRAMES_IDLE)
        self.sprite_idle.set_total_duration(1000)

        self.sprite_roll = Sprite(CAMINHO_ROLL, total_frames=FRAMES_ROLL)
        self.sprite_roll.set_total_duration(250)

        self.sprite_walk_right = Sprite(CAMINHO_WALK_RIGHT, total_frames=FRAMES_WALK_RIGHT)
        self.sprite_walk_right.set_total_duration(500)

        self.sprite_walk_left = Sprite(CAMINHO_WALK_LEFT, total_frames=FRAMES_WALK_LEFT)
        self.sprite_walk_left.set_total_duration(500)

        self.sprites_map = {
            "idle": self.sprite_idle,
            "roll": self.sprite_roll,
            "walk_right": self.sprite_walk_right,
            "walk_left": self.sprite_walk_left,
            "attack": self.combate.sprite_attack,
            "roll_attack": self.combate.sprite_roll_attack,
        }

        self._flipped_idle_esq = self._cache.obter_espelhada_horizontal(
            "idle_esq", getattr(self.sprite_idle, "image", None)
        )

        self.vida_maxima = VIDA_PLAYER
        self.vida = VIDA_PLAYER
        self.defesa = 0
        self.invencivel_dano_timer = 0.0

        self.estado = "idle"
        self.atual = self.sprite_idle

        self.x = 50.0
        self.pos_y_chao = pos_y_chao
        self.y = self.pos_y_chao - self.height

        h_pulo = 5 * self.height
        self.gravidade = (2 * h_pulo) / 1.0
        self.v_pulo = (2 * self.gravidade * h_pulo) ** 0.5

        self.vel_x_base = 200.0
        self.vel_knockback_x = 0.0
        self.desaceleracao_knockback = 650.0
        self.fator_pulo_parede = 0.85

        self.vel_y = 0.0
        self.no_chao = True
        self.no_topo = False
        self.tempo_topo = 0.0
        self.duracao_pausa_topo = 0.05

        self.direcao_direita = True
        self.combo_maximo = 10

    @property
    def esta_invencivel(self):
        return self.combate.esta_invencivel or self.invencivel_dano_timer > 0.0

    @property
    def dano_ataque(self):
        dano_base = self.combate.dano_atual
        combo_ativo = max(0, min(int(self.combo), self.combo_maximo))
        if combo_ativo > 0:
            return int(round(dano_base * (1.1 ** combo_ativo)))
        return dano_base

    @property
    def id_ataque_atual(self):
        return self.combate.id_ataque_atual

    @property
    def combo(self):
        return self.combate.combo

    @property
    def sem_habilidade_ataque(self):
        return self.combate.sem_habilidade

    @property
    def timer_descanso(self):
        return self.combate.timer_descanso

    @property
    def total_frames_atual(self):
        return max(1, self.frames_map.get(self.estado, 1))

    @property
    def width(self):
        return self.atual.image.get_width() / self.total_frames_atual

    @property
    def height(self):
        return self.atual.image.get_height()

    def get_hitbox(self):
        return pygame.Rect(
            int(self.x), int(self.y), max(1, int(self.width)), max(1, int(self.height))
        )

    def aplicar_dano_com_defesa(self, dano_bruto):
        dano_final = max(0, int(dano_bruto) - int(self.defesa))
        self.vida = max(0, self.vida - dano_final)
        return dano_final

    def sofrer_colisao_inimigo(self, inimigo, plataformas):
        """Aplica dano/repulsão diagonal ao colidir com inimigo sem ocupar o mesmo espaço."""
        if not inimigo.vivo or self.vida <= 0:
            return False

        hitbox_inimigo = inimigo.get_hitbox()
        centro_j = self.x + self.width * 0.5
        centro_i = hitbox_inimigo.centerx
        direcao_oposta = 1.0 if centro_j >= centro_i else -1.0

        if direcao_oposta > 0:
            self.x = min(float(LARGURA_MUNDO - self.width), float(hitbox_inimigo.right + 2))
        else:
            self.x = max(0.0, float(hitbox_inimigo.left - self.width - 2))

        if self.esta_invencivel:
            return False

        self.aplicar_dano_com_defesa(getattr(inimigo, "dano_contato", 10))
        self.invencivel_dano_timer = 0.85
        self.combate.cancelar()

        altura_diag = 28.0
        vel_subida = (2.0 * self.gravidade * altura_diag) ** 0.5
        self.vel_y = -vel_subida
        self.vel_knockback_x = direcao_oposta * (self.vel_x_base * 1.5)
        self.no_chao = False
        self.no_topo = False
        self.direcao_direita = direcao_oposta > 0
        self._set_estado("roll")

        self._resolver_colisao_lateral(plataformas, self.vel_knockback_x)
        return True

    def get_hitbox_ataque(self):
        return self.combate.get_hitbox(self)

    def _set_estado(self, novo_estado):
        if self.estado != novo_estado and novo_estado in self.sprites_map:
            self.estado = novo_estado
            self.atual = self.sprites_map[novo_estado]
            if hasattr(self.atual, "set_curr_frame"):
                self.atual.set_curr_frame(0)

    def _sobrepoe_x(self, plat):
        return (self.x + self.width - 4.0 > plat.x) and (self.x + 4.0 < plat.x + plat.width)

    def _sobrepoe_lateral_y(self, plat):
        return (self.y + self.height - 6.0 > plat.y + 6.0) and (
            self.y + 6.0 < plat.y + plat.height - 6.0
        )

    def _aplicar_pulo_diagonal_lateral(self, direcao_oposta, vel_x_antes):
        largura_anterior = self.width
        x_antigo = self.x
        y_antigo = self.y

        velocidade_base = abs(vel_x_antes) if abs(vel_x_antes) >= 50.0 else self.vel_x_base
        self.vel_knockback_x = direcao_oposta * (velocidade_base * 1.5)
        self.vel_y = -(self.v_pulo * self.fator_pulo_parede)
        self.no_chao = False
        self.no_topo = False
        self.combate.cancelar()
        self.direcao_direita = direcao_oposta > 0

        self._set_estado("roll")
        self.x = max(0.0, min(x_antigo + largura_anterior - self.width, LARGURA_MUNDO - self.width))
        self.y = y_antigo

    def _resolver_colisao_lateral(self, plataformas, vel_x_antes):
        for p in plataformas:
            if p.eh_chao_base or not self._sobrepoe_lateral_y(p):
                continue
            if not ((self.x + self.width > p.x) and (self.x < p.x + p.width)):
                continue

            if vel_x_antes > 0 and (self.x + self.width) >= p.x and self.x < p.x:
                self.x = p.x - self.width
                self._aplicar_pulo_diagonal_lateral(-1, vel_x_antes)
                self.x = min(self.x, p.x - self.width - 1.0)
                return True

            borda_dir = p.x + p.width
            if vel_x_antes < 0 and self.x <= borda_dir and (self.x + self.width) > borda_dir:
                self.x = borda_dir
                self._aplicar_pulo_diagonal_lateral(1, vel_x_antes)
                self.x = max(self.x, borda_dir + 1.0)
                return True

        return False

    def encontrar_chao(self, plataformas):
        chao_mais_proximo = None
        pe_jogador = self.y + self.height

        for p in plataformas:
            if self._sobrepoe_x(p) and p.y >= pe_jogador - 6.0:
                if chao_mais_proximo is None or p.y < chao_mais_proximo.y:
                    chao_mais_proximo = p
        return chao_mais_proximo

    def distancia_ate_o_chao(self, chao):
        return None if chao is None else chao.y - (self.y + self.height)

    def _colidiu_por_baixo(self, plataformas, y_anterior):
        if self.vel_y >= 0:
            return None

        for p in plataformas:
            if p.eh_chao_base or not self._sobrepoe_x(p):
                continue
            base_plat = p.y + p.height
            if y_anterior >= base_plat - 4.0 and self.y <= base_plat:
                return p
        return None

    def update(self, janela, plataformas):
        dt = janela.delta_time()
        teclado = janela.keyboard

        if self.invencivel_dano_timer > 0.0:
            self.invencivel_dano_timer = max(0.0, self.invencivel_dano_timer - dt)

        self.combate.update(dt)

        if self.combo > self.combo_maximo and hasattr(self.combate, "combo"):
            self.combate.combo = 0

        indo_esq = teclado.key_pressed("LEFT") or teclado.key_pressed("A")
        indo_dir = teclado.key_pressed("RIGHT") or teclado.key_pressed("D")

        movendo = False
        vel_input_x = 0.0

        if abs(self.vel_knockback_x) < 10.0:
            if indo_esq and not indo_dir:
                vel_input_x = -self.vel_x_base
                movendo = True
                if not self.combate.atacando:
                    self.direcao_direita = False
            elif indo_dir and not indo_esq:
                vel_input_x = self.vel_x_base
                movendo = True
                if not self.combate.atacando:
                    self.direcao_direita = True

        if not self.combate.atacando:
            if indo_esq and not indo_dir:
                self.direcao_direita = False
            elif indo_dir and not indo_esq:
                self.direcao_direita = True

        if teclado.key_pressed("J") or teclado.key_pressed("Z") or teclado.key_pressed("X"):
            self.combate.tentar_iniciar(self, plataformas)

        vel_x_antes = self.vel_knockback_x if abs(self.vel_knockback_x) >= 1.0 else vel_input_x

        if abs(self.vel_knockback_x) > 0.0:
            self.x += self.vel_knockback_x * dt
            passo_kb = self.desaceleracao_knockback * dt
            if self.vel_knockback_x > 0:
                self.vel_knockback_x = max(0.0, self.vel_knockback_x - passo_kb)
            else:
                self.vel_knockback_x = min(0.0, self.vel_knockback_x + passo_kb)
        elif vel_input_x != 0.0:
            self.x += vel_input_x * dt

        self.x = max(0.0, min(self.x, LARGURA_MUNDO - self.width))
        self._resolver_colisao_lateral(plataformas, vel_x_antes)
        self.x = max(0.0, min(self.x, LARGURA_MUNDO - self.width))

        chao = self.encontrar_chao(plataformas)

        if self.no_chao:
            dist_atual = self.distancia_ate_o_chao(chao)
            if chao is None or (dist_atual is not None and dist_atual > 4.0):
                self.no_chao = False
                self.vel_y = 0.0
                if not self.combate.atacando:
                    largura_antes_queda = self.width
                    x_antes_queda = self.x
                    y_antes_queda = self.y
                    self._set_estado("roll")
                    self.x = max(
                        0.0,
                        min(x_antes_queda + largura_antes_queda - self.width, LARGURA_MUNDO - self.width),
                    )
                    self.y = y_antes_queda

        # --- INÍCIO DO PULO ---
        if (
            teclado.key_down("SPACE") or teclado.key_down("UP") or teclado.key_down("W")
        ) and self.no_chao:
            player_largura = self.width
            x_antigo = self.x
            y_antigo = self.y

            self.vel_y = -self.v_pulo
            self.no_chao = False
            self.no_topo = False
            self.combate.cancelar()

            self._set_estado("roll")
            roll_largura = self.width
            self.x = max(
                0.0,
                min(x_antigo + player_largura - roll_largura, LARGURA_MUNDO - roll_largura),
            )
            self.y = y_antigo

        # --- FÍSICA VERTICAL ---
        if not self.no_chao:
            if self.combate.atacando:
                self._set_estado("roll_attack" if self.combate.ataque_no_ar else "attack")
            else:
                self._set_estado("roll")

            if self.no_topo:
                self.tempo_topo += dt
                if self.tempo_topo >= self.duracao_pausa_topo:
                    self.no_topo = False
                    self.vel_y = 0.0
            else:
                y_anterior = self.y
                self.vel_y += self.gravidade * dt
                self.y += self.vel_y * dt

                plat_teto = self._colidiu_por_baixo(plataformas, y_anterior)
                if plat_teto is not None:
                    self.y = plat_teto.y + plat_teto.height
                    self.vel_y = 50.0
                    self.no_topo = False
                elif -30.0 <= self.vel_y < 0.0:
                    self.no_topo = True
                    self.tempo_topo = 0.0
                    self.vel_y = 0.0

                chao = self.encontrar_chao(plataformas)
                dist_chao = self.distancia_ate_o_chao(chao)

                if self.vel_y >= 0.0 and dist_chao is not None and dist_chao <= 0.0:
                    largura_pulo = self.width
                    x_no_ar = self.x
                    topo_chao = chao.y if chao is not None else self.pos_y_chao

                    if self.combate.atacando:
                        self._set_estado(
                            "roll_attack" if self.combate.ataque_no_ar else "attack"
                        )
                    elif not movendo:
                        self._set_estado("idle")
                    else:
                        self._set_estado("walk_right" if self.direcao_direita else "walk_left")

                    direcao = 1.0 if self.direcao_direita else -1.0
                    deslocamento = direcao * ((largura_pulo * 0.5) + (self.width / 6.0))
                    self.x = max(
                        0.0,
                        min((x_no_ar + largura_pulo - self.width) + deslocamento, LARGURA_MUNDO - self.width),
                    )
                    self.y = topo_chao - self.height
                    self.vel_y = 0.0
                    self.no_chao = True

                if self.y < 0.0:
                    self.y = 0.0
                    self.vel_y = 0.0

                if self.y > janela.altura:
                    self.x = 50.0
                    self.combate.cancelar()
                    self._set_estado("idle")
                    self.y = self.pos_y_chao - self.height
                    self.vel_y = 0.0
                    self.no_chao = True

        # --- SELEÇÃO DE SPRITE NO CHÃO ---
        if self.no_chao:
            if self.combate.atacando:
                self._set_estado("roll_attack" if self.combate.ataque_no_ar else "attack")
            elif movendo or abs(self.vel_knockback_x) >= 1.0:
                self._set_estado("walk_right" if self.direcao_direita else "walk_left")
            else:
                self._set_estado("idle")

            topo_chao = chao.y if chao is not None else self.pos_y_chao
            self.y = topo_chao - self.height

        self.atual.update()

    def draw(self, janela, camera):
        rx = camera.transform_x(self.x)
        ry = camera.transform_y(self.y)

        total_frames = self.total_frames_atual
        frame_w = max(1, int(self.width))
        frame_h = max(1, int(self.height))
        frame_idx = int(getattr(self.atual, "curr_frame", getattr(self.atual, "frame_atual", 0)))
        frame_idx = max(0, min(frame_idx, total_frames - 1))

        if self.estado in ("attack", "roll_attack"):
            img, area = self.combate.obter_imagem_e_rect(
                self.estado,
                self.direcao_direita,
                total_frames,
                frame_w,
                frame_h,
                frame_idx,
            )
        elif self.estado == "idle" and not self.direcao_direita and self._flipped_idle_esq is not None:
            img = self._flipped_idle_esq
            col_flip = (total_frames - 1) - frame_idx
            area = pygame.Rect(col_flip * frame_w, 0, frame_w, frame_h)
        else:
            img = self.atual.image
            area = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)

        janela.screen.blit(img, (rx, ry), area=area)
