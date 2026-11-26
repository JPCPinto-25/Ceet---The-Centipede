import os
import pygame
from config import CAMINHO_CAPA, CAMINHO_FUNDO_BOSS, PASTA_SOUNDTRACK

CORES_TEXTO = {
    "branco": (240, 242, 245),
    "cinza": (170, 175, 185),
    "verde": (85, 220, 115),
    "azul": (95, 175, 255),
    "vermelho": (235, 65, 75),
    "amarelo": (255, 225, 85),
}

INTERVALO_LETRA_PADRAO = 0.095
INTERVALO_LETRA_FASE_4 = 0.145

CENAS_HISTORIA = {
    "inicio_fase_1": [
        [[("1 - Introdução", "branco")]],
    ],
    "fim_fase_1": [
        [[("Você viu pela primeira vez...", "branco")]],
        [[("Você se sente só...", "branco")]],
        [[("Você vê outros...", "branco")]],
        [[("Eles não são como você...", "branco")]],
        [[("Você vê violência...", "branco")]],
        [[("Você não entende...", "branco")]],
        [[("Você lembra do silêncio...", "branco")]],
        [[("Você lembra da escuridão...", "branco")]],
        [[("Mas no fim, você vê LUZ", "branco")]],
        [[("E VOCÊ APREENDE", "cinza")]],
    ],
    "inicio_fase_2": [
        [[("2 - Compreensão", "branco")]],
    ],
    "fim_fase_2": [
        [
            [("Você sente a luz...", "branco")],
            [("Você sente seu calor...", "branco")],
        ],
        [
            [("Você sente a grama...", "branco")],
            [("Você sente a terra...", "branco")],
        ],
        [
            [("Você sente o chão...", "branco")],
            [("Você sente muitas coisas...", "branco")],
            [("Boas e ruins...", "branco")],
        ],
        [[("Mas no fim, você sente o calor da VIDA", "branco")]],
        [[("E VOCÊ COMPREENDE", "verde")]],
    ],
    "inicio_fase_3": [
        [[("3 - Aceitação", "branco")]],
    ],
    "fim_fase_3": [
        [
            [("Você viu e sentiu muito...", "branco")],
            [("Você viu a tristeza da vida..", "branco")],
            [("Você sentiu a felicidade da vida...", "branco")],
        ],
        [
            [("Você viu a feiura da vida...", "branco")],
            [("Você viu a beleza da vida...", "branco")],
        ],
        [
            [("Você aprendeu...", "branco")],
            [("Você compreendeu...", "branco")],
        ],
        [[("E VOCÊ ACEITA", "azul")]],
    ],
    "inicio_fase_4": [
        [[("4 - Escolha", "branco")]],
        [
            [("Você sente uma presença familiar...", "branco")],
            [("Algo que você conhece...", "branco")],
        ],
        [[("Mas nunca viu...", "branco")]],
        [[("Mas sentiu...", "branco")]],
        [[("Algo que você entende...", "branco")]],
        [[("Algo que te ", "branco"), ("FERIU", "vermelho"), ("...", "branco")]],
        [[("Poderia ser esta...", "branco")]],
        [[("A razão de não haver outros...", "branco")]],
        [[("Como você...", "branco")]],
        [[("É hora de escolher...", "branco")]],
    ],
    "rota_pacifista": [
        [
            [("Você aprendeu...", "branco")],
            [("Você compreendeu...", "branco")],
            [("Você aceitou...", "branco")],
            [("E VOCÊ ESCOLHEU", "branco")],
        ],
        [[("VOCÊ", "amarelo")]],
    ],
    "rota_vingativa": [
        [
            [("Você aprendeu...", "branco")],
            [("Você compreendeu...", "branco")],
            [("Você aceitou...", "branco")],
            [("E VOCÊ ESCOLHEU", "branco")],
        ],
        [[("VIDA", "vermelho")]],
    ],
    "derrota": [
        [[("VOCÊ NÃO SUPORTÔU A VIDA", "vermelho")]],
    ],
}

LINHAS_CREDITOS = [
    "Ceet - The Centipede",
    "",
    "Créditos",
    "",
    "Tudo:",
    "João Pedro Conceição Pinto",
    "Pedro Gomes do Nascimento",
    "",
    "Feito usando a engine PPLAY",
    "",
    "Os direitos dos assets que foram",
    "usados emprestados pertencem aos",
    "seus respectivos autores",
    "",
    "Agradecemos muito por disponibilizarem!",
    "",
    "Feito pensando naqueles que",
    "não possuem muita habilidade motora",
    "como um dos criadores",
    "",
    "Sempre jogue para relaxar e aproveitar",
    "Que jogos sempre sejam uma felicidade para nós",
    "E nunca uma tortura",
    "",
    "TRABALHO FINAL",
    "",
    "LAB. DE JOGOS",
    "TURMA: BA",
    "Professor: Esteban Walter Gonzalez Clua",
    "",
    "UFF - Universidade Federal Fluminense",
    "",
    "Obrigado por jogar!!!",
]


def _resolver_caminho_projeto(caminho):
    pasta_base = os.path.dirname(os.path.abspath(__file__))
    if os.path.isabs(caminho):
        return caminho
    return os.path.join(pasta_base, caminho)


def _carregar_som_typewriter(intervalo_letra):
    pasta_base = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(pasta_base, PASTA_SOUNDTRACK, "Typewriter.wav"),
        os.path.join(pasta_base, "Soundtrack", "Typewriter.wav"),
        os.path.join(pasta_base, "soundtrack", "Typewriter.wav"),
    ]
    caminho = next((c for c in candidatos if os.path.exists(c)), None)
    duracao_extra = max(0.06, float(intervalo_letra) + 0.10)
    if caminho is None:
        return None, None, duracao_extra

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        if pygame.mixer.get_num_channels() < 8:
            pygame.mixer.set_num_channels(8)
        canal = pygame.mixer.Channel(4)
        som = pygame.mixer.Sound(caminho)
        som.set_volume(0.85)
        return canal, som, duracao_extra
    except pygame.error:
        return None, None, duracao_extra


def _tocar_tecla_typewriter(canal, som):
    if canal is None or som is None:
        return
    if canal.get_busy():
        canal.stop()
    canal.set_volume(0.85)
    canal.play(som)


def _encerrar_tecla_typewriter(canal, usar_fade=True):
    if canal is not None and canal.get_busy():
        if usar_fade:
            canal.fadeout(70)
        else:
            canal.stop()


def _fade_tela(janela, escurecer=True, duracao=0.45):
    overlay = pygame.Surface((janela.largura, janela.altura))
    overlay.fill((0, 0, 0))
    fundo_snapshot = janela.screen.copy()
    tempo = 0.0
    while tempo < duracao:
        dt = janela.delta_time()
        tempo += dt
        progresso = min(1.0, tempo / max(0.01, duracao))
        alpha = int(255 * (progresso if escurecer else (1.0 - progresso)))
        janela.screen.blit(fundo_snapshot, (0, 0))
        overlay.set_alpha(alpha)
        janela.screen.blit(overlay, (0, 0))
        janela.update()


def rodar_tela_inicial(janela):
    caminho_capa = _resolver_caminho_projeto(CAMINHO_CAPA)

    img_inicio = None
    if os.path.exists(caminho_capa):
        try:
            raw = pygame.image.load(caminho_capa).convert()
            img_inicio = pygame.transform.smoothscale(
                raw, (janela.largura, janela.altura)
            )
        except pygame.error:
            img_inicio = None

    fonte_aviso = pygame.font.SysFont("arial", 15, bold=True)
    piscar = 0.0
    enter_ant = True

    while True:
        dt = janela.delta_time()
        piscar += dt
        teclado = janela.keyboard
        keys_pg = pygame.key.get_pressed()

        enter_atual = bool(
            teclado.key_down("ENTER")
            or keys_pg[pygame.K_RETURN]
            or keys_pg[pygame.K_SPACE]
        )
        if enter_atual and not enter_ant:
            _fade_tela(janela, escurecer=True, duracao=0.4)
            return
        enter_ant = enter_atual

        if img_inicio is not None:
            janela.screen.blit(img_inicio, (0, 0))
        else:
            janela.screen.fill((12, 14, 18))

        if int(piscar * 2.2) % 2 == 0:
            txt = fonte_aviso.render("PRESSIONE ENTER PARA INICIAR", True, (245, 240, 210))
            janela.screen.blit(
                txt,
                ((janela.largura - txt.get_width()) // 2, janela.altura - 28),
            )

        janela.update()


def rodar_cena_historia(
    janela, chave_cena, intervalo_letra=INTERVALO_LETRA_PADRAO, aguardar_confirmacao=False
):
    telas = CENAS_HISTORIA.get(chave_cena, [])
    if not telas:
        return

    canal_tw, som_tw, duracao_som_tw = _carregar_som_typewriter(intervalo_letra)
    fonte = pygame.font.SysFont("arial", 20, bold=True)
    fonte_aviso = pygame.font.SysFont("arial", 13, bold=True)
    espaco_linhas = 32
    enter_ant = True

    for bloco_linhas in telas:
        total_chars = sum(
            len(texto) for linha in bloco_linhas for (texto, _) in linha
        )
        chars_visiveis = 0
        acumulador_tempo = 0.0
        tempo_desde_ultima_letra = 0.0
        som_letra_ativo = False
        tempo_pos_completo = 0.0
        pausa_automatica = 1.65 if intervalo_letra >= 0.13 else 1.25

        while True:
            dt = janela.delta_time()
            teclado = janela.keyboard
            keys_pg = pygame.key.get_pressed()

            avancar_atual = bool(
                teclado.key_down("ENTER")
                or keys_pg[pygame.K_RETURN]
                or keys_pg[pygame.K_SPACE]
            )
            avancar_borda = avancar_atual and not enter_ant
            enter_ant = avancar_atual

            if chars_visiveis < total_chars:
                if avancar_borda:
                    chars_visiveis = total_chars
                    _encerrar_tecla_typewriter(canal_tw, usar_fade=False)
                    som_letra_ativo = False
                else:
                    acumulador_tempo += dt
                    if som_letra_ativo:
                        tempo_desde_ultima_letra += dt
                        if tempo_desde_ultima_letra >= duracao_som_tw:
                            _encerrar_tecla_typewriter(canal_tw, usar_fade=True)
                            som_letra_ativo = False

                    while acumulador_tempo >= intervalo_letra and chars_visiveis < total_chars:
                        acumulador_tempo -= intervalo_letra
                        chars_visiveis += 1

                        idx_busca = chars_visiveis - 1
                        char_atual = " "
                        contador = 0
                        for linha in bloco_linhas:
                            for texto, _ in linha:
                                if contador + len(texto) > idx_busca:
                                    char_atual = texto[idx_busca - contador]
                                    break
                                contador += len(texto)
                            else:
                                continue
                            break

                        if not char_atual.isspace():
                            _tocar_tecla_typewriter(canal_tw, som_tw)
                            tempo_desde_ultima_letra = 0.0
                            som_letra_ativo = True
                        else:
                            _encerrar_tecla_typewriter(canal_tw, usar_fade=False)
                            som_letra_ativo = False
            else:
                if som_letra_ativo:
                    tempo_desde_ultima_letra += dt
                    if tempo_desde_ultima_letra >= duracao_som_tw:
                        _encerrar_tecla_typewriter(canal_tw, usar_fade=True)
                        som_letra_ativo = False

                tempo_pos_completo += dt
                if avancar_borda or (
                    not aguardar_confirmacao and tempo_pos_completo >= pausa_automatica
                ):
                    _encerrar_tecla_typewriter(canal_tw, usar_fade=False)
                    break

            janela.screen.fill((0, 0, 0))

            altura_bloco = len(bloco_linhas) * espaco_linhas
            y_inicial = (janela.altura - altura_bloco) // 2

            chars_restantes = chars_visiveis
            for idx_linha, linha in enumerate(bloco_linhas):
                largura_total_linha = sum(
                    fonte.size(texto)[0] for (texto, _) in linha
                )
                x_cursor = (janela.largura - largura_total_linha) // 2
                y_linha = y_inicial + idx_linha * espaco_linhas

                for texto, nome_cor in linha:
                    if chars_restantes <= 0:
                        break
                    trecho = texto[:chars_restantes]
                    chars_restantes -= len(trecho)
                    cor_rgb = CORES_TEXTO.get(nome_cor, CORES_TEXTO["branco"])
                    surf = fonte.render(trecho, True, cor_rgb)
                    janela.screen.blit(surf, (x_cursor, y_linha))
                    x_cursor += surf.get_width()

            if aguardar_confirmacao and chars_visiveis >= total_chars:
                aviso = fonte_aviso.render(
                    "PRESSIONE ENTER PARA REINICIAR", True, (180, 120, 120)
                )
                janela.screen.blit(
                    aviso,
                    ((janela.largura - aviso.get_width()) // 2, janela.altura - 26),
                )

            janela.update()

        _encerrar_tecla_typewriter(canal_tw, usar_fade=False)
        _fade_tela(janela, escurecer=True, duracao=0.35)


def rodar_creditos(janela):
    caminho_bank = _resolver_caminho_projeto(CAMINHO_FUNDO_BOSS)
    fundo_bank = None
    if os.path.exists(caminho_bank):
        try:
            raw_bank = pygame.image.load(caminho_bank).convert()
            fundo_bank = pygame.transform.smoothscale(
                raw_bank, (janela.largura, janela.altura)
            )
        except pygame.error:
            fundo_bank = None

    veio_escuro = pygame.Surface((janela.largura, janela.altura))
    veio_escuro.fill((0, 0, 0))
    veio_escuro.set_alpha(135)

    fonte = pygame.font.SysFont("arial", 16, bold=True)
    espacamento_y = 26
    velocidade_rolagem = 17.0  # px/s: rolagem lenta para leitura confortável

    # Começa fora da tela na parte inferior e sobe até sair completamente no topo
    offset_y = float(janela.altura)
    altura_total_bloco = len(LINHAS_CREDITOS) * espacamento_y
    offset_final = -float(altura_total_bloco + 24)

    while offset_y > offset_final:
        dt = janela.delta_time()
        offset_y -= velocidade_rolagem * dt

        if fundo_bank is not None:
            janela.screen.blit(fundo_bank, (0, 0))
            janela.screen.blit(veio_escuro, (0, 0))
        else:
            janela.screen.fill((10, 12, 16))

        for idx, texto in enumerate(LINHAS_CREDITOS):
            if not texto:
                continue

            y_linha = offset_y + (idx * espacamento_y)
            # Revela progressivamente conforme a linha entra pela base da tela
            if y_linha >= janela.altura:
                continue

            visibilidade = max(0.0, min(1.0, (janela.altura - y_linha) / 38.0))
            qtd_chars = max(1, int(round(len(texto) * visibilidade)))
            trecho = texto[:qtd_chars]

            # Mantém a linha centralizada horizontalmente durante a revelação
            surf = fonte.render(trecho, True, (255, 255, 255))
            x_linha = (janela.largura - surf.get_width()) // 2
            janela.screen.blit(surf, (x_linha, int(y_linha)))

        janela.update()

    _fade_tela(janela, escurecer=True, duracao=0.55)


def rodar_transicao_historia(janela):
    rodar_cena_historia(janela, "inicio_fase_1", intervalo_letra=INTERVALO_LETRA_PADRAO)
