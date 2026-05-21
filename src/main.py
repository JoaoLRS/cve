from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from filtros import (
    abrir,
    aplicar_gaussian_blur,
    aplicar_median_blur,
    canny,
    carregar_imagem,
    calcular_histograma,
    converter_cinza,
    criar_kernel,
    dilatar,
    erodir,
    equalizar_histograma,
    fechar,
    salvar_imagem,
    threshold_adaptativo,
    threshold_global,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTADOS_DIR = BASE_DIR / "resultados"

IMG_PATH = DATA_DIR / "carParkImg.png"
VIDEO_PATH = DATA_DIR / "carPark.mp4"


def salvar_histograma(imagem_gray, caminho_saida: Path, titulo: str) -> None:
    hist = calcular_histograma(imagem_gray)
    plt.figure(figsize=(8, 4))
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.title(titulo)
    plt.xlabel("Intensidade")
    plt.ylabel("Frequencia")
    plt.tight_layout()
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho_saida)
    plt.close()


def processar_imagem() -> None:
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

    imagem = carregar_imagem(IMG_PATH)
    cinza = converter_cinza(imagem)
    blur = aplicar_gaussian_blur(cinza)
    median = aplicar_median_blur(cinza)
    equalizada = equalizar_histograma(cinza)

    thresh_global = threshold_global(cinza)
    thresh_adaptativo = threshold_adaptativo(blur)

    kernel = criar_kernel((3, 3))
    dilatacao = dilatar(thresh_adaptativo, kernel)
    erosao = erodir(thresh_adaptativo, kernel)
    abertura = abrir(thresh_adaptativo, kernel)
    fechamento = fechar(thresh_adaptativo, kernel)
    bordas = canny(blur)

    salvar_imagem(RESULTADOS_DIR / "grayscale.png", cinza)
    salvar_imagem(RESULTADOS_DIR / "blur.png", blur)
    salvar_imagem(RESULTADOS_DIR / "median.png", median)
    salvar_imagem(RESULTADOS_DIR / "equalizada.png", equalizada)
    salvar_histograma(cinza, RESULTADOS_DIR / "histograma.png", "Histograma - escala de cinza")
    salvar_histograma(equalizada, RESULTADOS_DIR / "histograma_equalizada.png", "Histograma - equalizada")
    salvar_imagem(RESULTADOS_DIR / "threshold_global.png", thresh_global)
    salvar_imagem(RESULTADOS_DIR / "threshold_adaptativo.png", thresh_adaptativo)
    salvar_imagem(RESULTADOS_DIR / "dilatacao.png", dilatacao)
    salvar_imagem(RESULTADOS_DIR / "erosao.png", erosao)
    salvar_imagem(RESULTADOS_DIR / "abertura.png", abertura)
    salvar_imagem(RESULTADOS_DIR / "fechamento.png", fechamento)
    salvar_imagem(RESULTADOS_DIR / "canny.png", bordas)

    print(f"Imagem processada com sucesso em: {RESULTADOS_DIR}")


def processar_video() -> None:
    captura = cv2.VideoCapture(str(VIDEO_PATH))
    if not captura.isOpened():
        raise FileNotFoundError(f"Nao foi possivel abrir o video: {VIDEO_PATH}")

    while True:
        ret, frame = captura.read()
        if not ret:
            break

        cinza = converter_cinza(frame)
        blur = aplicar_gaussian_blur(cinza)
        adaptativo = threshold_adaptativo(blur)

        cv2.imshow("Video - Threshold adaptativo", adaptativo)
        if cv2.waitKey(30) == 27:
            break

    captura.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    processar_imagem()
