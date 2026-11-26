import os
import pygame


class SoundtrackManager:
    def __init__(self, pasta_base=None):
        if pasta_base is None:
            pasta_base = os.path.dirname(os.path.abspath(__file__))
        self.pasta_soundtrack = os.path.join(pasta_base, "Soundtrack")

        self.arquivos = {
            "menu_pause_boss_fase": os.path.join(
                self.pasta_soundtrack, "Palm_Tree_Shade.wav"
            ),
            "fase_1": os.path.join(self.pasta_soundtrack, "A_Fool's_Affair.wav"),
            "fase_2_3": os.path.join(
                self.pasta_soundtrack, "Boundless_Slumber.wav"
            ),
            "boss": os.path.join(self.pasta_soundtrack, "Crisis.wav"),
        }

        self.audio_disponivel = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            self.audio_disponivel = True
        except pygame.error:
            self.audio_disponivel = False

        self.canal_fase = pygame.mixer.Channel(1) if self.audio_disponivel else None
        self.canal_boss = pygame.mixer.Channel(2) if self.audio_disponivel else None

        self._sons = {}
        if self.audio_disponivel:
            for chave, caminho in self.arquivos.items():
                if os.path.exists(caminho):
                    try:
                        self._sons[chave] = pygame.mixer.Sound(caminho)
                    except pygame.error:
                        self._sons[chave] = None
                else:
                    self._sons[chave] = None

        self._som_fase_atual = None
        self._vol_fase_atual = 0.70
        self._vol_boss_atual = 0.0

    def _tocar_em_canal(self, canal, som, volume):
        if not self.audio_disponivel or canal is None or som is None:
            return
        canal.set_volume(max(0.0, min(1.0, volume)))
        if canal.get_sound() is not som or not canal.get_busy():
            canal.play(som, loops=-1)

    def _parar_canal(self, canal):
        if self.audio_disponivel and canal is not None and canal.get_busy():
            canal.stop()

    def parar_tudo(self):
        self._parar_canal(self.canal_fase)
        self._parar_canal(self.canal_boss)
        self._som_fase_atual = None
        self._vol_boss_atual = 0.0

    def tocar_menu_ou_pausa(self):
        self._parar_canal(self.canal_boss)
        self._vol_boss_atual = 0.0
        self._vol_fase_atual = 0.70
        som = self._sons.get("menu_pause_boss_fase")
        self._som_fase_atual = som
        self._tocar_em_canal(self.canal_fase, som, self._vol_fase_atual)

    def atualizar_jogo(
        self, fase_atual, boss_em_tela, pausado=False, em_dialogo=False, dt=0.016
    ):
        if not self.audio_disponivel:
            return

        if em_dialogo:
            self.parar_tudo()
            return

        if pausado:
            self.tocar_menu_ou_pausa()
            return

        if fase_atual == 1:
            som_fase = self._sons.get("fase_1")
        elif fase_atual in (2, 3):
            som_fase = self._sons.get("fase_2_3")
        else:
            som_fase = self._sons.get("menu_pause_boss_fase")

        if som_fase is not self._som_fase_atual:
            self._parar_canal(self.canal_fase)
            self._som_fase_atual = som_fase
            self._vol_fase_atual = 0.70
            self._tocar_em_canal(self.canal_fase, som_fase, self._vol_fase_atual)

        som_boss = self._sons.get("boss")
        taxa_entrada = max(0.002, dt) * 0.11
        taxa_saida = max(0.005, dt) * 0.22

        if boss_em_tela and som_boss is not None:
            alvo_fase = 0.16
            alvo_boss = 0.72

            if self._vol_fase_atual > alvo_fase:
                self._vol_fase_atual = max(alvo_fase, self._vol_fase_atual - taxa_entrada)
            else:
                self._vol_fase_atual = min(alvo_fase, self._vol_fase_atual + taxa_entrada)

            if self._vol_boss_atual < alvo_boss:
                self._vol_boss_atual = min(alvo_boss, self._vol_boss_atual + taxa_entrada)

            self._tocar_em_canal(self.canal_fase, som_fase, self._vol_fase_atual)
            self._tocar_em_canal(self.canal_boss, som_boss, self._vol_boss_atual)
        else:
            alvo_fase = 0.70
            if self._vol_fase_atual < alvo_fase:
                self._vol_fase_atual = min(alvo_fase, self._vol_fase_atual + taxa_saida)
            self._tocar_em_canal(self.canal_fase, som_fase, self._vol_fase_atual)

            if self._vol_boss_atual > 0.0:
                self._vol_boss_atual = max(0.0, self._vol_boss_atual - taxa_saida)
                if self.canal_boss is not None and self.canal_boss.get_busy():
                    self.canal_boss.set_volume(self._vol_boss_atual)
                    if self._vol_boss_atual <= 0.003:
                        self._parar_canal(self.canal_boss)
            else:
                self._parar_canal(self.canal_boss)
