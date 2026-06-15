import cv2
import numpy as np
from filtros import (
    converter_cinza,
    aplicar_gaussian_blur,
    aplicar_median_blur,
    threshold_adaptativo,
    criar_kernel,
    dilatar,
)

LARGURA_VAGA_PADRAO = 107
ALTURA_VAGA_PADRAO = 48


def processar_frame_intermediarios(frame: np.ndarray, config: dict) -> tuple[np.ndarray, dict]:
    """
    Processa o frame aplicando os filtros sequencialmente e retorna a imagem binarizada final
    junto com um dicionario contendo os resultados de cada etapa intermediaria.
    """
    etapas = {}

    # 1. Escala de Cinza
    cinza = converter_cinza(frame)
    etapas["1. Grayscale"] = cinza

    # 2. Gaussian Blur
    g_kernel = tuple(config.get("gaussian_kernel", [3, 3]))
    blur = aplicar_gaussian_blur(cinza, g_kernel)
    etapas["2. Gaussian Blur"] = blur

    # 3. Adaptive Threshold
    block_size = config.get("adaptive_block_size", 25)
    c_val = config.get("adaptive_c", 16)
    threshold = threshold_adaptativo(
        blur, tamanho_janela=block_size, constante=c_val, inverter=True
    )
    etapas["3. Adaptive Threshold"] = threshold

    # 4. Median Blur
    m_kernel = config.get("median_kernel", 5)
    mediana = aplicar_median_blur(threshold, m_kernel)
    etapas["4. Median Blur"] = mediana

    # 5. Dilatacao
    k_size = tuple(config.get("morph_kernel", [3, 3]))
    iterations = config.get("morph_iterations", 1)
    kernel = criar_kernel(k_size)
    binaria_final = dilatar(mediana, kernel, iterations)
    etapas["5. Dilatacao"] = binaria_final

    return binaria_final, etapas


def classificar_vagas(
    frame_original: np.ndarray,
    frame_processado: np.ndarray,
    vagas: list,
    limiar: int,
) -> tuple[np.ndarray, int, list]:
    """
    Classifica cada vaga com base na quantidade de pixels nao nulos (brancos)
    e desenha os retangulos (verde para livre, vermelho para ocupado).
    Retorna o frame anotado, a quantidade de vagas livres e os detalhes de cada vaga.
    """
    frame_anotado = frame_original.copy()
    vagas_livres = 0
    detalhes = []

    for indice, vaga in enumerate(vagas):
        # Suporta tanto coordenadas de ponto único (x, y) quanto de retângulo completo (x, y, w, h)
        if len(vaga) == 2:
            x, y = vaga
            w = LARGURA_VAGA_PADRAO
            h = ALTURA_VAGA_PADRAO
        else:
            x, y, w, h = vaga

        # Garante que a ROI esteja dentro dos limites da imagem
        h_img, w_img = frame_processado.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_img, x + w), min(h_img, y + h)

        roi = frame_processado[y1:y2, x1:x2]
        if roi.size == 0:
            pixels = 0
        else:
            pixels = cv2.countNonZero(roi)

        status_livre = pixels < limiar
        if status_livre:
            cor = (0, 255, 0)  # Verde
            espessura = 3
            vagas_livres += 1
            status_str = "livre"
        else:
            cor = (0, 0, 255)  # Vermelho
            espessura = 2
            status_str = "ocupada"

        detalhes.append(
            {
                "indice": indice + 1,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "pixels": pixels,
                "status": status_str,
            }
        )

        # Desenhar retângulo e texto com o contador de pixels brancos
        cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), cor, espessura)
        cv2.putText(
            frame_anotado,
            str(pixels),
            (x1 + 4, y1 + h - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            cor,
            1,
        )
        cv2.putText(
            frame_anotado,
            str(indice + 1),
            (x1 + 4, y1 + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 0, 255),
            1,
        )

    return frame_anotado, vagas_livres, detalhes


def desenhar_contador(frame: np.ndarray, vagas_livres: int, total_vagas: int) -> None:
    texto = f"Livres: {vagas_livres}/{total_vagas}"
    # Caixa verde com o contador no topo esquerdo
    cv2.rectangle(frame, (20, 20), (250, 70), (0, 180, 0), cv2.FILLED)
    cv2.putText(
        frame,
        texto,
        (35, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
    )


def processar_imagem_completo(
    imagem: np.ndarray,
    config: dict,
    vagas: list,
) -> dict:
    """
    Executa o pipeline completo de processamento de imagem e classificacao de vagas.
    Retorna um dicionario com os resultados intermediarios, finais e metricas.
    """
    limiar = config.get("limiar_vaga_livre", 900)

    # 1. Processar filtros intermediarios
    binaria_final, etapas = processar_frame_intermediarios(imagem, config)

    # 2. Classificar vagas e desenhar
    anotada, livres, detalhes = classificar_vagas(imagem, binaria_final, vagas, limiar)

    # 3. Desenhar o painel contador de vagas livres
    desenhar_contador(anotada, livres, len(vagas))

    return {
        "resultado_final": anotada,
        "imagens_intermediarias": etapas,
        "vagas_livres": livres,
        "detalhes_vagas": detalhes,
    }
