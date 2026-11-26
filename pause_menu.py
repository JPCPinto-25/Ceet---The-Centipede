import pygame


class MenuPausa:
    OPCOES = ("continuar", "codes:", "sair")

    # Mapeamento direto de teclas para digitação responsiva (1 toque = 1 caractere)
    MAPA_TECLAS_LETRAS = {
        pygame.K_a: "a",
        pygame.K_b: "b",
        pygame.K_c: "c",
        pygame.K_d: "d",
        pygame.K_e: "e",
        pygame.K_f: "f",
        pygame.K_g: "g",
        pygame.K_h: "h",
        pygame.K_i: "i",
        pygame.K_j: "j",
        pygame.K_k: "k",
        pygame.K_l: "l",
        pygame.K_m: "m",
        pygame.K_n: "n",
        pygame.K_o: "o",
        pygame.K_p: "p",
        pygame.K_q: "q",
        pygame.K_r: "r",
        pygame.K_s: "s",
        pygame.K_t: "t",
        pygame.K_u: "u",
        pygame.K_v: "v",
        pygame.K_w: "w",
        pygame.K_x: "x",
        pygame.K_y: "y",
        pygame.K_z: "z",
        pygame.K_0: "0",
        pygame.K_1: "1",
        pygame.K_2: "2",
        pygame.K_3: "3",
        pygame.K_4: "4",
        pygame.K_5: "5",
        pygame.K_6: "6",
        pygame.K_7: "7",
        pygame.K_8: "8",
        pygame.K_9: "9",
    }

    def __init__(self):
        self.aberto = False
        self.indice_selecionado = 0
        self.digitando_codigo = False
        self._aguardando_soltar_enter = False
        self.codigo_atual = ""
        self.debug_ativo = False
        self.mensagem_codigo = ""

        self.fonte_titulo = pygame.font.SysFont("arial", 26, bold=True)
        self.fonte_opcao = pygame.font.SysFont("arial", 20, bold=True)
        self.fonte_codigo = pygame.font.SysFont("arial", 18, bold=True)

        self._teclas_anteriores = {}
        self._estado_letras_anterior = {}

    def _pressionou_agora(self, teclado, nome_tecla):
        atual = bool(teclado.key_down(nome_tecla))
        anterior = self._teclas_anteriores.get(nome_tecla, False)
        self._teclas_anteriores[nome_tecla] = atual
        return atual and not anterior

    def alternar(self):
        self.aberto = not self.aberto
        if self.aberto:
            self.indice_selecionado = 0
            self.digitando_codigo = False
            self._aguardando_soltar_enter = True
            self.codigo_atual = ""
            self.mensagem_codigo = ""
            self._estado_letras_anterior.clear()

    def _processar_digitacao_codigo(self, keys_pg):
        # BACKSPACE com borda de subida
        bs_atual = bool(keys_pg[pygame.K_BACKSPACE])
        bs_anterior = self._estado_letras_anterior.get(pygame.K_BACKSPACE, False)
        self._estado_letras_anterior[pygame.K_BACKSPACE] = bs_atual
        if bs_atual and not bs_anterior and self.codigo_atual:
            self.codigo_atual = self.codigo_atual[:-1]

        # Letras e números com borda de subida (1 toque = 1 letra imediata)
        for key_code, caractere in self.MAPA_TECLAS_LETRAS.items():
            atual = bool(keys_pg[key_code])
            anterior = self._estado_letras_anterior.get(key_code, False)
            self._estado_letras_anterior[key_code] = atual
            if atual and not anterior:
                if len(self.codigo_atual) < 20:
                    self.codigo_atual += caractere

    def update(self, janela):
        teclado = janela.keyboard
        keys_pg = pygame.key.get_pressed()
        enter_pg = bool(keys_pg[pygame.K_RETURN] or keys_pg[pygame.K_KP_ENTER])

        if self._aguardando_soltar_enter:
            if not enter_pg and not bool(teclado.key_down("ENTER")):
                self._aguardando_soltar_enter = False
            self._teclas_anteriores["ENTER"] = enter_pg
            return None

        if self.digitando_codigo:
            self._processar_digitacao_codigo(keys_pg)

            enter_confirmar = enter_pg and not self._teclas_anteriores.get("ENTER", False)
            self._teclas_anteriores["ENTER"] = enter_pg

            if enter_confirmar:
                codigo_limpo = self.codigo_atual.strip().lower()
                if codigo_limpo == "debug":
                    self.debug_ativo = True
                    self.mensagem_codigo = "MODO DEBUG ATIVADO"
                else:
                    self.mensagem_codigo = "CODIGO INVALIDO"
                self.digitando_codigo = False
                self._aguardando_soltar_enter = True
            return None

        if self._pressionou_agora(teclado, "UP") or self._pressionou_agora(teclado, "W"):
            self.indice_selecionado = (self.indice_selecionado - 1) % len(self.OPCOES)

        if self._pressionou_agora(teclado, "DOWN") or self._pressionou_agora(teclado, "S"):
            self.indice_selecionado = (self.indice_selecionado + 1) % len(self.OPCOES)

        if self._pressionou_agora(teclado, "ENTER"):
            escolha = self.OPCOES[self.indice_selecionado]
            if escolha == "continuar":
                self.aberto = False
                self._aguardando_soltar_enter = True
                return "continuar"
            if escolha == "codes:":
                self.digitando_codigo = True
                self._aguardando_soltar_enter = True
                self.codigo_atual = ""
                self.mensagem_codigo = ""
                self._estado_letras_anterior.clear()
                return None
            if escolha == "sair":
                self.aberto = False
                self._aguardando_soltar_enter = True
                return "sair"

        return None

    def draw(self, janela):
        janela.screen.fill((0, 0, 0))

        titulo_surf = self.fonte_titulo.render("Ceet  - The Centipede", True, (255, 255, 255))
        y_titulo = 52
        janela.screen.blit(titulo_surf, ((janela.largura - titulo_surf.get_width()) // 2, y_titulo))

        y_base = 122
        espacamento = 34

        texto_cont = "> continuar <" if self.indice_selecionado == 0 else "continuar"
        surf_cont = self.fonte_opcao.render(texto_cont, True, (255, 255, 255))
        janela.screen.blit(surf_cont, ((janela.largura - surf_cont.get_width()) // 2, y_base))

        y_codes = y_base + espacamento
        texto_codes = "> codes: <" if self.indice_selecionado == 1 else "codes:"
        surf_codes = self.fonte_opcao.render(texto_codes, True, (255, 255, 255))
        janela.screen.blit(surf_codes, ((janela.largura - surf_codes.get_width()) // 2, y_codes))

        y_sair = y_codes + espacamento
        if self.digitando_codigo:
            campo_txt = self.codigo_atual if self.codigo_atual else "_"
            surf_campo = self.fonte_codigo.render(campo_txt, True, (255, 255, 255))
            janela.screen.blit(
                surf_campo, ((janela.largura - surf_campo.get_width()) // 2, y_codes + 24)
            )
            y_sair = y_codes + 54
        elif self.mensagem_codigo:
            surf_msg = self.fonte_codigo.render(self.mensagem_codigo, True, (255, 255, 255))
            janela.screen.blit(
                surf_msg, ((janela.largura - surf_msg.get_width()) // 2, y_codes + 24)
            )
            y_sair = y_codes + 54

        texto_sair = "> sair <" if self.indice_selecionado == 2 else "sair"
        surf_sair = self.fonte_opcao.render(texto_sair, True, (255, 255, 255))
        janela.screen.blit(surf_sair, ((janela.largura - surf_sair.get_width()) // 2, y_sair))
