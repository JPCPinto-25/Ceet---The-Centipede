import math
import pygame


class CacheRenderizacao:
    def __init__(self, tamanho_fonte=16):
        self._flip_cache = {}
        self.fonte = pygame.font.SysFont("arial", tamanho_fonte, bold=True)
        self._texto_cache = {}

    def obter_espelhada_horizontal(self, chave, surface):
        if surface is None:
            return None
        if chave not in self._flip_cache:
            self._flip_cache[chave] = pygame.transform.flip(surface, True, False)
        return self._flip_cache[chave]

    def obter_texto_com_sombra(self, chave_slot, texto, cor):
        registro = self._texto_cache.get(chave_slot)
        if registro is not None and registro[0] == texto and registro[1] == cor:
            return registro[2], registro[3]

        sombra = self.fonte.render(texto, True, (0, 0, 0))
        principal = self.fonte.render(texto, True, cor)
        self._texto_cache[chave_slot] = (texto, cor, sombra, principal)
        return sombra, principal

    def desenhar_hud(self, janela, jogador, tempo_total):
        x_hud = 10
        y_tempo = 10
        y_combo = y_tempo + self.fonte.get_linesize() + 10
        y_vida = y_combo + self.fonte.get_linesize() + 10

        # 1. TEMPO
        segundos_int = int(tempo_total)
        minutos, segs = divmod(segundos_int, 60)
        texto_tempo = f"TEMPO: {minutos:02d}:{segs:02d}"
        sombra_t, surf_t = self.obter_texto_com_sombra("tempo", texto_tempo, (255, 255, 255))
        janela.screen.blit(sombra_t, (x_hud + 1, y_tempo + 1))
        janela.screen.blit(surf_t, (x_hud, y_tempo))

        # 2. COMBO / CONTAGEM REGRESSIVA DE DESCANSO
        if jogador.sem_habilidade_ataque or jogador.timer_descanso > 0.0:
            contagem = max(1, int(math.ceil(jogador.timer_descanso)))
            texto_combo = f"COMBO: {contagem}s"
            cor_combo = (255, 90, 90)
        else:
            texto_combo = f"COMBO: {jogador.combo}"
            cor_combo = (255, 230, 100)

        sombra_c, surf_c = self.obter_texto_com_sombra("combo", texto_combo, cor_combo)
        janela.screen.blit(sombra_c, (x_hud + 1, y_combo + 1))
        janela.screen.blit(surf_c, (x_hud, y_combo))

        # 3. VIDA DO PLAYER
        vida_atual = int(math.ceil(jogador.vida))
        vida_max = int(jogador.vida_maxima)
        texto_vida = f"VIDA: {vida_atual}/{vida_max}"
        if vida_atual <= 25:
            cor_vida = (255, 75, 75)
        elif vida_atual <= 60:
            cor_vida = (255, 190, 75)
        else:
            cor_vida = (110, 240, 130)

        sombra_v, surf_v = self.obter_texto_com_sombra("vida", texto_vida, cor_vida)
        janela.screen.blit(sombra_v, (x_hud + 1, y_vida + 1))
        janela.screen.blit(surf_v, (x_hud, y_vida))

        # Mini barra visual de vida ao lado do texto
        barra_x = x_hud + surf_v.get_width() + 10
        barra_y = y_vida + (surf_v.get_height() - 10) // 2
        barra_w = 80
        barra_h = 10
        proporcao = max(0.0, min(1.0, jogador.vida / max(1.0, jogador.vida_maxima)))

        pygame.draw.rect(janela.screen, (30, 30, 35), (barra_x, barra_y, barra_w, barra_h))
        pygame.draw.rect(janela.screen, cor_vida, (barra_x, barra_y, int(barra_w * proporcao), barra_h))
        pygame.draw.rect(janela.screen, (220, 220, 230), (barra_x, barra_y, barra_w, barra_h), width=1)

    def desenhar_barra_chefe(self, janela, chefe):
        if chefe is None or not chefe.vivo:
            return

        largura_barra = 260
        altura_barra = 12
        bx = (janela.largura - largura_barra) // 2
        by = janela.altura - 24
        proporcao = max(0.0, min(1.0, chefe.vida / max(1.0, chefe.vida_maxima)))

        sombra_b, surf_b = self.obter_texto_com_sombra(
            "chefe", f"CHEFE FROG: {int(math.ceil(chefe.vida))}/{int(chefe.vida_maxima)}", (255, 110, 110)
        )
        tx = (janela.largura - surf_b.get_width()) // 2
        ty = by - surf_b.get_height() - 3

        janela.screen.blit(sombra_b, (tx + 1, ty + 1))
        janela.screen.blit(surf_b, (tx, ty))

        pygame.draw.rect(janela.screen, (35, 20, 25), (bx, by, largura_barra, altura_barra))
        pygame.draw.rect(
            janela.screen,
            (225, 45, 65),
            (bx, by, int(largura_barra * proporcao), altura_barra),
        )
        pygame.draw.rect(janela.screen, (240, 210, 215), (bx, by, largura_barra, altura_barra), width=1)
