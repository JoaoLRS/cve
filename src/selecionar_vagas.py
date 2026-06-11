from pathlib import Path
import json
import pickle

import cv2

from filtros import carregar_imagem


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

IMG_PATH = DATA_DIR / "carParkImg.png"
VAGAS_PKL_PATH = DATA_DIR / "vagas.pkl"
VAGAS_JSON_PATH = DATA_DIR / "vagas.json"

LARGURA_VAGA = 107
ALTURA_VAGA = 48

NOME_JANELA = "Selecionar vagas"


def carregar_vagas() -> list[tuple[int, int]]:
    if VAGAS_PKL_PATH.exists():
        with VAGAS_PKL_PATH.open("rb") as arquivo:
            return pickle.load(arquivo)

    if VAGAS_JSON_PATH.exists():
        with VAGAS_JSON_PATH.open("r", encoding="utf-8") as arquivo:
            return [tuple(vaga) for vaga in json.load(arquivo)]

    return []


def salvar_vagas(vagas: list[tuple[int, int]]) -> None:
    VAGAS_PKL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VAGAS_PKL_PATH.open("wb") as arquivo:
        pickle.dump(vagas, arquivo)
    with VAGAS_JSON_PATH.open("w", encoding="utf-8") as arquivo:
        json.dump(vagas, arquivo, indent=2)


def desenhar_vagas(imagem, vagas: list[tuple[int, int]]):
    imagem_vagas = imagem.copy()
    for indice, (x, y) in enumerate(vagas, start=1):
        cv2.rectangle(
            imagem_vagas,
            (x, y),
            (x + LARGURA_VAGA, y + ALTURA_VAGA),
            (255, 0, 255),
            2,
        )
        cv2.putText(
            imagem_vagas,
            str(indice),
            (x + 4, y + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 255),
            1,
        )
    return imagem_vagas


def encontrar_vaga_clicada(vagas: list[tuple[int, int]], x: int, y: int) -> int | None:
    for indice, (x_vaga, y_vaga) in enumerate(vagas):
        dentro_x = x_vaga <= x <= x_vaga + LARGURA_VAGA
        dentro_y = y_vaga <= y <= y_vaga + ALTURA_VAGA
        if dentro_x and dentro_y:
            return indice
    return None


def main() -> None:
    imagem = carregar_imagem(IMG_PATH)
    vagas = carregar_vagas()

    def mouse_callback(evento, x, y, flags, params) -> None:
        if evento == cv2.EVENT_LBUTTONDOWN:
            vagas.append((x, y))
            salvar_vagas(vagas)

        if evento == cv2.EVENT_RBUTTONDOWN:
            indice = encontrar_vaga_clicada(vagas, x, y)
            if indice is not None:
                vagas.pop(indice)
                salvar_vagas(vagas)

    cv2.namedWindow(NOME_JANELA)
    cv2.setMouseCallback(NOME_JANELA, mouse_callback)

    while True:
        imagem_vagas = desenhar_vagas(imagem, vagas)
        cv2.putText(
            imagem_vagas,
            f"Vagas: {len(vagas)} | esquerdo adiciona | direito remove | s salva | q sai",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        cv2.imshow(NOME_JANELA, imagem_vagas)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("s"):
            salvar_vagas(vagas)
            print(f"{len(vagas)} vagas salvas em: {VAGAS_PKL_PATH}")
        elif tecla in (ord("q"), 27):
            salvar_vagas(vagas)
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
