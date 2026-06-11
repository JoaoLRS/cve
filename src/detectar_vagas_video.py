from pathlib import Path
import json
import pickle

import cv2

from filtros import (
    aplicar_gaussian_blur,
    aplicar_median_blur,
    converter_cinza,
    criar_kernel,
    dilatar,
    salvar_imagem,
    threshold_adaptativo,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTADOS_DIR = BASE_DIR / "resultados"

VIDEO_PATH = DATA_DIR / "carPark.mp4"
VAGAS_PKL_PATH = DATA_DIR / "vagas.pkl"
VAGAS_JSON_PATH = DATA_DIR / "vagas.json"
FRAME_EVIDENCIA_PATH = RESULTADOS_DIR / "frame_vagas_detectadas.png"

LARGURA_VAGA = 107
ALTURA_VAGA = 48
LIMIAR_VAGA_LIVRE = 900

GAUSSIAN_KERNEL = (3, 3)
ADAPTIVE_BLOCK_SIZE = 25
ADAPTIVE_C = 16
MEDIAN_KERNEL = 5
MORPH_KERNEL = (3, 3)
MORPH_ITERACOES = 1

NOME_JANELA = "Deteccao de vagas"


def carregar_vagas() -> list[tuple[int, int]]:
    if VAGAS_PKL_PATH.exists():
        with VAGAS_PKL_PATH.open("rb") as arquivo:
            vagas = pickle.load(arquivo)
    elif VAGAS_JSON_PATH.exists():
        with VAGAS_JSON_PATH.open("r", encoding="utf-8") as arquivo:
            vagas = [tuple(vaga) for vaga in json.load(arquivo)]
    else:
        raise FileNotFoundError(
            f"Arquivo de vagas nao encontrado: {VAGAS_PKL_PATH} ou {VAGAS_JSON_PATH}\n"
            "Execute primeiro: python src/selecionar_vagas.py"
        )

    if not vagas:
        raise ValueError(
            f"Nenhuma vaga foi cadastrada em: {VAGAS_PKL_PATH} ou {VAGAS_JSON_PATH}\n"
            "Execute novamente: python src/selecionar_vagas.py"
        )

    return vagas


def preparar_frame(frame):
    cinza = converter_cinza(frame)
    blur = aplicar_gaussian_blur(cinza, GAUSSIAN_KERNEL)
    threshold = threshold_adaptativo(
        blur,
        tamanho_janela=ADAPTIVE_BLOCK_SIZE,
        constante=ADAPTIVE_C,
        inverter=True,
    )
    mediana = aplicar_median_blur(threshold, MEDIAN_KERNEL)
    kernel = criar_kernel(MORPH_KERNEL)
    return dilatar(mediana, kernel, MORPH_ITERACOES)


def classificar_vagas(frame_original, frame_processado, vagas: list[tuple[int, int]]) -> int:
    vagas_livres = 0

    for x, y in vagas:
        roi = frame_processado[y : y + ALTURA_VAGA, x : x + LARGURA_VAGA]
        quantidade_pixels = cv2.countNonZero(roi)

        if quantidade_pixels < LIMIAR_VAGA_LIVRE:
            cor = (0, 255, 0)
            espessura = 4
            vagas_livres += 1
        else:
            cor = (0, 0, 255)
            espessura = 2

        cv2.rectangle(
            frame_original,
            (x, y),
            (x + LARGURA_VAGA, y + ALTURA_VAGA),
            cor,
            espessura,
        )
        cv2.putText(
            frame_original,
            str(quantidade_pixels),
            (x + 4, y + ALTURA_VAGA - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            cor,
            1,
        )

    return vagas_livres


def desenhar_contador(frame, vagas_livres: int, total_vagas: int) -> None:
    texto = f"Livres: {vagas_livres}/{total_vagas}"
    cv2.rectangle(frame, (35, 25), (300, 85), (0, 180, 0), cv2.FILLED)
    cv2.putText(
        frame,
        texto,
        (50, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.1,
        (255, 255, 255),
        3,
    )


def main() -> None:
    vagas = carregar_vagas()

    captura = cv2.VideoCapture(str(VIDEO_PATH))
    if not captura.isOpened():
        raise FileNotFoundError(f"Nao foi possivel abrir o video: {VIDEO_PATH}")

    frame_evidencia_salvo = False

    while True:
        sucesso, frame = captura.read()
        if not sucesso:
            captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_processado = preparar_frame(frame)
        vagas_livres = classificar_vagas(frame, frame_processado, vagas)
        desenhar_contador(frame, vagas_livres, len(vagas))

        if not frame_evidencia_salvo:
            salvar_imagem(FRAME_EVIDENCIA_PATH, frame)
            frame_evidencia_salvo = True

        cv2.imshow(NOME_JANELA, frame)

        tecla = cv2.waitKey(30) & 0xFF
        if tecla in (ord("q"), 27):
            break

    captura.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
