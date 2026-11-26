from PPlay.sprite import Sprite
from config import CAMINHO_INTRO, LARGURA_JANELA, ALTURA_JANELA


def rodar_animacao_inicial(janela, duracao_segundos=3.0, total_frames=1):
    """Roda a animação inicial (spritesheet) pela duração informada."""
    anim_abertura = Sprite(CAMINHO_INTRO, total_frames=total_frames)
    anim_abertura.set_total_duration(int(duracao_segundos * 1000))
    anim_abertura.set_loop(True)

    anim_abertura.x = (LARGURA_JANELA - anim_abertura.width) / 2
    anim_abertura.y = (ALTURA_JANELA - anim_abertura.height) / 2

    tempo_decorrido = 0.0

    while tempo_decorrido < duracao_segundos:
        dt = janela.delta_time()
        tempo_decorrido += dt

        janela.screen.fill(janela.cor_fundo)
        anim_abertura.update()
        anim_abertura.draw()
        janela.update()
