import pygame
from PPlay.window import Window
from PPlay.camera import Camera
from config import ALTURA_JANELA, ALTURA_MUNDO, LARGURA_JANELA, LARGURA_MUNDO, VIDA_PLAYER
from fase_manager import FaseManager
from menu_intro import (
    INTERVALO_LETRA_FASE_4,
    INTERVALO_LETRA_PADRAO,
    rodar_cena_historia,
    rodar_creditos,
    rodar_tela_inicial,
    rodar_transicao_historia,
)
from pause_menu import MenuPausa
from player import Player
from render_cache import CacheRenderizacao
from soundtrack import SoundtrackManager

# --- 1. INICIALIZAÇÃO ---
janela = Window(LARGURA_JANELA, ALTURA_JANELA)
janela.set_title("Ceet - The Centipede")

cache_render = CacheRenderizacao(tamanho_fonte=16)
menu_pausa = MenuPausa()
soundtrack = SoundtrackManager()
fonte_x_player = pygame.font.SysFont("arial", 15, bold=True)

LIMITE_TEMPO_BOSS = 60.0


def iniciar_nova_sessao(pular_intro=False):
    if not pular_intro:
        soundtrack.tocar_menu_ou_pausa()
        rodar_tela_inicial(janela)
        soundtrack.parar_tudo()
        rodar_transicao_historia(janela)

    cam = Camera(janela.largura, janela.altura)
    cam.set_world_bounds(LARGURA_MUNDO, ALTURA_MUNDO)

    alt_chao = 32
    y_chao = ALTURA_JANELA - alt_chao

    gerenciador = FaseManager(
        pos_y_chao=y_chao, altura_chao=alt_chao, cache_render=cache_render
    )
    ply = Player(y_chao, cache_render=cache_render)
    return {
        "camera": cam,
        "alt_chao": alt_chao,
        "y_chao": y_chao,
        "gerenciador": gerenciador,
        "jogador": ply,
        "tempo_jogo": 0.0,
        "kills_oculto": 0,
        "kills_fase_atual": 0,
        "entrou_na_fase_boss": False,
        "rota_ao_entrar_boss": None,
        "tempo_na_fase_boss": 0.0,
        "creditos_exibidos": False,
    }


estado = iniciar_nova_sessao(pular_intro=False)
enter_anterior = False
alt_anterior = False


def processar_combate(jogador, inimigos, plataformas, debug_ativo, estado_sessao):
    hitbox_ataque = jogador.get_hitbox_ataque()
    hitbox_jogador = jogador.get_hitbox()
    dano_golpe = jogador.dano_ataque
    id_golpe = jogador.id_ataque_atual

    for inimigo in inimigos:
        if not inimigo.vivo:
            continue

        hitbox_inimigo = inimigo.get_hitbox()

        if (
            hitbox_ataque is not None
            and hitbox_inimigo.width > 0
            and hitbox_ataque.colliderect(hitbox_inimigo)
        ):
            acertou_agora = inimigo.receber_dano(dano_golpe, id_golpe)
            if acertou_agora:
                jogador.combate.combo += 1
                jogador.combate.combo_timer = 2.5
                if not inimigo.vivo and not getattr(inimigo, "eh_chefe", False):
                    estado_sessao["kills_oculto"] += 1
                    estado_sessao["kills_fase_atual"] += 1

        if (
            not debug_ativo
            and inimigo.vivo
            and hitbox_inimigo.width > 0
            and hitbox_jogador.colliderect(hitbox_inimigo)
        ):
            jogador.sofrer_colisao_inimigo(inimigo, plataformas)


def desenhar_x_player(janela, jogador, fase_atual):
    texto = f"X: {int(jogador.x)} | FASE: {fase_atual}"
    sombra = fonte_x_player.render(texto, True, (0, 0, 0))
    surf = fonte_x_player.render(texto, True, (255, 255, 120))
    x_pos = janela.largura - surf.get_width() - 12
    y_pos = 10
    janela.screen.blit(sombra, (x_pos + 1, y_pos + 1))
    janela.screen.blit(surf, (x_pos, y_pos))


def _boss_em_tela(gerenciador_fases, camera, janela):
    cam_esq = camera.x
    cam_dir = cam_esq + janela.largura

    for boss_obj in (
        gerenciador_fases.miniboss,
        gerenciador_fases.worm_boss_f2,
        gerenciador_fases.boss_final,
    ):
        if boss_obj is not None and getattr(boss_obj, "vivo", False):
            if boss_obj is gerenciador_fases.worm_boss_f2 and not getattr(
                boss_obj, "_ciclo_iniciado", False
            ):
                continue
            b_esq = getattr(boss_obj, "x", 0.0)
            b_dir = b_esq + getattr(boss_obj, "width", 0.0)
            if b_dir >= cam_esq - 40 and b_esq <= cam_dir + 40:
                return True
    return False


def _executar_historia_e_creditos(janela, rota_pacifista):
    soundtrack.parar_tudo()
    if rota_pacifista:
        rodar_cena_historia(
            janela, "rota_pacifista", intervalo_letra=INTERVALO_LETRA_FASE_4
        )
    else:
        rodar_cena_historia(
            janela, "rota_vingativa", intervalo_letra=INTERVALO_LETRA_FASE_4
        )
    soundtrack.tocar_menu_ou_pausa()
    rodar_creditos(janela)


# --- 2. GAME LOOP PRINCIPAL ---
while True:
    dt = janela.delta_time()
    teclado = janela.keyboard
    keys_pg = pygame.key.get_pressed()

    enter_pressionado = bool(teclado.key_down("ENTER"))
    if enter_pressionado and not enter_anterior and not menu_pausa.aberto:
        menu_pausa.alternar()
    enter_anterior = enter_pressionado

    alt_pressionado = bool(keys_pg[pygame.K_LALT] or keys_pg[pygame.K_RALT])
    alt_borda = alt_pressionado and not alt_anterior
    alt_anterior = alt_pressionado

    if menu_pausa.aberto:
        soundtrack.atualizar_jogo(
            estado["gerenciador"].fase_atual,
            boss_em_tela=False,
            pausado=True,
            em_dialogo=False,
            dt=dt,
        )
        acao = menu_pausa.update(janela)
        menu_pausa.draw(janela)
        janela.update()
        enter_anterior = bool(teclado.key_down("ENTER"))
        if acao == "sair":
            estado = iniciar_nova_sessao(pular_intro=False)
        continue

    camera = estado["camera"]
    pos_y_chao = estado["y_chao"]
    gerenciador_fases = estado["gerenciador"]
    jogador = estado["jogador"]
    estado["tempo_jogo"] += dt

    if menu_pausa.debug_ativo:
        jogador.vida = jogador.vida_maxima
        jogador.invencivel_dano_timer = 0.0
        if alt_borda:
            if gerenciador_fases.fase_atual != 4:
                gerenciador_fases.carregar_fase(4)
                camera.set_world_bounds(gerenciador_fases.largura_mundo_atual, ALTURA_MUNDO)
                estado["tempo_jogo"] = 0.0
                estado["kills_fase_atual"] = 0
                jogador.vida = jogador.vida_maxima
                soundtrack.parar_tudo()
                rodar_cena_historia(
                    janela, "inicio_fase_4", intervalo_letra=INTERVALO_LETRA_FASE_4
                )
            boss_alvo = gerenciador_fases.boss_final
            if boss_alvo is not None:
                jogador.x = boss_alvo.arena_inicio + 30.0
                jogador.y = pos_y_chao - jogador.height
                jogador.vel_y = 0.0
                jogador.no_chao = True
                boss_alvo.arena_ativa = True
                camera.x = boss_alvo.arena_inicio

    if gerenciador_fases.fase_atual == 2 and gerenciador_fases.worm_boss_f2 is not None:
        if (jogador.x + jogador.width) >= gerenciador_fases.worm_boss_f2.x_inicio_cacada:
            gerenciador_fases.inimigos = [
                inim
                for inim in gerenciador_fases.inimigos
                if inim is gerenciador_fases.worm_boss_f2
            ]

    jogador.update(janela, gerenciador_fases.plataformas)
    jogador.x = max(0.0, min(jogador.x, gerenciador_fases.largura_mundo_atual - jogador.width))
    if jogador.y > pos_y_chao - jogador.height:
        jogador.y = pos_y_chao - jogador.height

    if not menu_pausa.debug_ativo and jogador.vida <= 0:
        soundtrack.parar_tudo()
        rodar_cena_historia(
            janela,
            "derrota",
            intervalo_letra=INTERVALO_LETRA_PADRAO,
            aguardar_confirmacao=True,
        )
        estado = iniciar_nova_sessao(pular_intro=True)
        enter_anterior = True
        continue

    boss = gerenciador_fases.boss_final
    miniboss = gerenciador_fases.miniboss
    worm_boss_f2 = gerenciador_fases.worm_boss_f2
    outros_inimigos = gerenciador_fases.inimigos

    if gerenciador_fases.fase_atual == 4 and not estado["entrou_na_fase_boss"]:
        estado["entrou_na_fase_boss"] = True
        estado["rota_ao_entrar_boss"] = (
            "pacifista" if estado["kills_oculto"] == 0 else "vingativa"
        )
        estado["tempo_na_fase_boss"] = 0.0

    for inimigo in outros_inimigos:
        if not inimigo.vivo:
            continue
        if inimigo is boss:
            inimigo.update(janela, jogador)
            if inimigo.y > pos_y_chao - inimigo.height:
                inimigo.y = pos_y_chao - inimigo.height
        elif inimigo is miniboss:
            inimigo.update(janela, gerenciador_fases.plataformas, jogador)
        elif inimigo is worm_boss_f2:
            inimigo.update(janela, jogador)
        else:
            inimigo.update(janela, gerenciador_fases.plataformas, jogador, outros_inimigos)

    processar_combate(
        jogador,
        outros_inimigos,
        gerenciador_fases.plataformas,
        menu_pausa.debug_ativo,
        estado,
    )

    if not menu_pausa.debug_ativo and jogador.vida <= 0:
        soundtrack.parar_tudo()
        rodar_cena_historia(
            janela,
            "derrota",
            intervalo_letra=INTERVALO_LETRA_PADRAO,
            aguardar_confirmacao=True,
        )
        estado = iniciar_nova_sessao(pular_intro=True)
        enter_anterior = True
        continue

    camera.set_world_bounds(gerenciador_fases.largura_mundo_atual, ALTURA_MUNDO)
    camera.follow(jogador, suavizacao=0.1)

    if boss is not None and gerenciador_fases.fase_atual == 4 and boss.vivo:
        boss.restringir_jogador_na_arena(jogador, camera)

    soundtrack.atualizar_jogo(
        gerenciador_fases.fase_atual,
        boss_em_tela=_boss_em_tela(gerenciador_fases, camera, janela),
        pausado=False,
        em_dialogo=False,
        dt=dt,
    )

    if gerenciador_fases.fase_atual == 4 and boss is not None and boss.vivo:
        if boss.arena_ativa or menu_pausa.debug_ativo:
            estado["tempo_na_fase_boss"] += dt

    if (
        gerenciador_fases.fase_atual == 4
        and boss is not None
        and not estado["creditos_exibidos"]
    ):
        venceu_por_tempo = boss.vivo and estado["tempo_na_fase_boss"] >= LIMITE_TEMPO_BOSS
        venceu_derrotando = not boss.vivo

        if venceu_por_tempo or venceu_derrotando:
            estado["creditos_exibidos"] = True
            rota_pac = (
                estado["rota_ao_entrar_boss"] == "pacifista"
                and estado["kills_oculto"] == 0
            )
            if venceu_por_tempo and not rota_pac:
                boss.vida = 0.0
                boss.vivo = False
                boss.arena_ativa = False

            _executar_historia_e_creditos(janela, rota_pac)
            estado = iniciar_nova_sessao(pular_intro=False)
            enter_anterior = True
            continue

    nova_fase = gerenciador_fases.verificar_gatilho(jogador, camera)
    if nova_fase is not None:
        if estado["kills_fase_atual"] == 0:
            jogador.defesa += 5
        jogador.vida = jogador.vida_maxima
        estado["tempo_jogo"] = 0.0
        estado["kills_fase_atual"] = 0

        if nova_fase == 2:
            soundtrack.parar_tudo()
            rodar_cena_historia(janela, "fim_fase_1", intervalo_letra=INTERVALO_LETRA_PADRAO)
            rodar_cena_historia(janela, "inicio_fase_2", intervalo_letra=INTERVALO_LETRA_PADRAO)
        elif nova_fase == 3:
            soundtrack.parar_tudo()
            rodar_cena_historia(janela, "fim_fase_2", intervalo_letra=INTERVALO_LETRA_PADRAO)
            rodar_cena_historia(janela, "inicio_fase_3", intervalo_letra=INTERVALO_LETRA_PADRAO)
        elif nova_fase == 4:
            soundtrack.parar_tudo()
            rodar_cena_historia(janela, "fim_fase_3", intervalo_letra=INTERVALO_LETRA_PADRAO)
            rodar_cena_historia(janela, "inicio_fase_4", intervalo_letra=INTERVALO_LETRA_FASE_4)

    # --- 3. RENDERIZAÇÃO ---
    gerenciador_fases.parallax.draw()

    img_chao = gerenciador_fases.img_chao
    if img_chao is not None:
        largura_bloco = img_chao.width if img_chao.width > 0 else 32
        inicio_x = int(camera.x // largura_bloco) * largura_bloco
        fim_x = inicio_x + janela.largura + largura_bloco
        ry = camera.transform_y(pos_y_chao)
        x_bloco = inicio_x
        while x_bloco < fim_x:
            janela.screen.blit(img_chao.image, (camera.transform_x(x_bloco), ry))
            x_bloco += largura_bloco

    gerenciador_fases.draw_acessorios_fundo(janela, camera)
    gerenciador_fases.draw_plataformas(janela, camera)
    gerenciador_fases.draw_acessorios_frente(janela, camera)
    gerenciador_fases.draw_inimigos(janela, camera)
    gerenciador_fases.draw_gatilho(janela, camera)
    jogador.draw(janela, camera)

    if miniboss is not None and gerenciador_fases.fase_atual == 1 and miniboss.vivo:
        miniboss.draw_barra_topo(janela)

    if worm_boss_f2 is not None and gerenciador_fases.fase_atual == 2 and worm_boss_f2.vivo:
        worm_boss_f2.draw_barra_topo(janela)

    if boss is not None and gerenciador_fases.fase_atual == 4 and boss.vivo:
        boss.draw_barra_topo(janela)

    cache_render.desenhar_hud(janela, jogador, estado["tempo_jogo"])
    desenhar_x_player(janela, jogador, gerenciador_fases.fase_atual)

    janela.update()
