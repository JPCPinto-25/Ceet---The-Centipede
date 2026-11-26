import math


def _clamp_acima_do_chao(inimigo):
    limite_y_chao = inimigo.pos_y_chao - inimigo.height
    if inimigo.y > limite_y_chao:
        inimigo.y = limite_y_chao


def _pode_passar_por_baixo(inimigo, plataforma, apoio_y):
    """Permite passar por baixo se a altura da entidade for menor que o fundo da plataforma."""
    if plataforma.eh_chao_base or plataforma is inimigo.plataforma_atual:
        return False
    fundo_plataforma = plataforma.y + plataforma.height
    dentro_x = (inimigo.x + inimigo.width > plataforma.x) and (
        inimigo.x < plataforma.x + plataforma.width
    )
    return dentro_x and (inimigo.height < fundo_plataforma) and (apoio_y >= fundo_plataforma - 2.0)


def _calcular_intervalo_patrulha_300(inimigo, plataformas, largura_mundo):
    """Patrulha base de 300 px; exclui espaço de plataformas bloqueantes e expande no lado oposto se houver espaço."""
    apoio_y = (
        inimigo.plataforma_atual.y
        if inimigo.plataforma_atual is not None
        else inimigo.pos_y_chao
    )

    if not hasattr(inimigo, "_centro_patrulha_fixo"):
        inimigo._centro_patrulha_fixo = inimigo.x + inimigo.width * 0.5

    centro = inimigo._centro_patrulha_fixo
    esq = max(220.0, centro - 150.0)
    dir_lim = min(float(largura_mundo) - 40.0, centro + 150.0)

    if dir_lim - esq < 300.0:
        if esq <= 220.0:
            dir_lim = min(float(largura_mundo) - 40.0, esq + 300.0)
        elif dir_lim >= float(largura_mundo) - 40.0:
            esq = max(220.0, dir_lim - 300.0)

    for p in plataformas:
        if p.eh_chao_base or p is inimigo.plataforma_atual:
            continue
        if _pode_passar_por_baixo(inimigo, p, apoio_y):
            continue

        bloqueia_y = (p.y - apoio_y) < inimigo.height and (p.y + p.height > apoio_y - inimigo.height)
        if not bloqueia_y:
            continue

        p_esq = p.x
        p_dir = p.x + p.width

        # Se a plataforma está à direita do centro, exclui sua faixa e amplia à esquerda se disponível
        if p_esq < dir_lim and p_dir > esq:
            if (p_esq + p_dir) * 0.5 >= inimigo.x + inimigo.width * 0.5:
                excluido = max(0.0, min(dir_lim, p_dir) - max(esq, p_esq))
                dir_lim = min(dir_lim, p_esq - 4.0)
                esq = max(220.0, esq - excluido)
            else:
                excluido = max(0.0, min(dir_lim, p_dir) - max(esq, p_esq))
                esq = max(esq, p_dir + 4.0)
                dir_lim = min(float(largura_mundo) - 40.0, dir_lim + excluido)

    if dir_lim <= esq + inimigo.width + 8.0:
        dir_lim = min(float(largura_mundo) - 40.0, esq + inimigo.width + 24.0)

    return esq, dir_lim


def _patrulhar_em_cima_de_plataforma(inimigo, plat, dt):
    min_x = plat.x
    max_x = max(plat.x, plat.x + plat.width - inimigo.width)
    direcao = 1.0 if inimigo.direcao_direita else -1.0
    vel = getattr(inimigo, "vel_walk", getattr(inimigo, "vel_x", 55.0))
    inimigo.x += direcao * vel * dt

    if inimigo.x <= min_x:
        inimigo.x = min_x
        inimigo.direcao_direita = True
    elif inimigo.x >= max_x:
        inimigo.x = max_x
        inimigo.direcao_direita = False

    inimigo.y = min(inimigo.pos_y_chao - inimigo.height, plat.y - inimigo.height)


def _colisao_entre_entidades(inimigo, outros_inimigos, dt):
    if inimigo._cooldown_colisao_entidade > 0.0:
        inimigo._cooldown_colisao_entidade = max(0.0, inimigo._cooldown_colisao_entidade - dt)
        return

    if not inimigo.vivo or not outros_inimigos:
        return

    minha_rect = inimigo.get_hitbox()
    for outro in outros_inimigos:
        if outro is inimigo or not outro.vivo or getattr(outro, "eh_chefe", False):
            continue
        if not minha_rect.colliderect(outro.get_hitbox()):
            continue

        if inimigo.x + inimigo.width * 0.5 <= outro.x + outro.width * 0.5:
            inimigo.x -= 4.0
            outro.x += 4.0
            inimigo.direcao_direita = False
            outro.direcao_direita = True
        else:
            inimigo.x += 4.0
            outro.x -= 4.0
            inimigo.direcao_direita = True
            outro.direcao_direita = False

        inimigo._cooldown_colisao_entidade = 0.16
        outro._cooldown_colisao_entidade = 0.16
        break


def atualizar_movimento_worm(worm, dt, plataformas, outros_inimigos):
    if getattr(worm, "patrulhar_plataforma_fixa", False) and worm.plataforma_atual is not None:
        _patrulhar_em_cima_de_plataforma(worm, worm.plataforma_atual, dt)
        _colisao_entre_entidades(worm, outros_inimigos, dt)
        return

    largura_mundo = getattr(worm, "x_max", 5000.0)
    esq, dir_lim = _calcular_intervalo_patrulha_300(worm, plataformas, largura_mundo)

    direcao = 1.0 if worm.direcao_direita else -1.0
    worm.x += direcao * worm.vel_x * dt

    if worm.x <= esq:
        worm.x = esq
        worm.direcao_direita = True
    elif worm.x >= dir_lim - worm.width:
        worm.x = max(esq, dir_lim - worm.width)
        worm.direcao_direita = False

    _colisao_entre_entidades(worm, outros_inimigos, dt)
    worm.y = worm.pos_y_chao - worm.height
    _clamp_acima_do_chao(worm)


def atualizar_movimento_mushroom(mushroom, dt, plataformas, jogador, outros_inimigos):
    mushroom._set_estado("walk")

    if getattr(mushroom, "patrulhar_plataforma_fixa", False) and mushroom.plataforma_atual is not None:
        _patrulhar_em_cima_de_plataforma(mushroom, mushroom.plataforma_atual, dt)
        _colisao_entre_entidades(mushroom, outros_inimigos, dt)
        return

    if mushroom.plataforma_atual is not None:
        _patrulhar_em_cima_de_plataforma(mushroom, mushroom.plataforma_atual, dt)
        _colisao_entre_entidades(mushroom, outros_inimigos, dt)
        return

    largura_mundo = getattr(mushroom, "x_max", 5000.0)
    esq, dir_lim = _calcular_intervalo_patrulha_300(mushroom, plataformas, largura_mundo)

    direcao = 1.0 if mushroom.direcao_direita else -1.0
    mushroom.x += direcao * mushroom.vel_walk * dt

    if mushroom.x <= esq:
        mushroom.x = esq
        mushroom.direcao_direita = True
    elif mushroom.x >= dir_lim - mushroom.width:
        mushroom.x = max(esq, dir_lim - mushroom.width)
        mushroom.direcao_direita = False

    _colisao_entre_entidades(mushroom, outros_inimigos, dt)
    mushroom.y = mushroom.pos_y_chao - mushroom.height
    _clamp_acima_do_chao(mushroom)


def atualizar_movimento_blue_fly(fly, dt, jogador, outros_inimigos):
    fly.tempo_voo += dt
    direcao = 1.0 if fly.direcao_direita else -1.0
    fly.x += direcao * fly.vel_x * dt

    limite_esq = max(220.0, fly.x_min)
    limite_dir = max(limite_esq + 40.0, fly.x_max - fly.width)
    if fly.x <= limite_esq:
        fly.x = limite_esq
        fly.direcao_direita = True
    elif fly.x >= limite_dir:
        fly.x = limite_dir
        fly.direcao_direita = False

    _colisao_entre_entidades(fly, outros_inimigos, dt)
    fly.y = max(48.0, fly.y_base + math.sin(fly.tempo_voo * 4.5) * 14.0)
    _clamp_acima_do_chao(fly)
