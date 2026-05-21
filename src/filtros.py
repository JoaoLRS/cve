from pathlib import Path

import cv2
import numpy as np


def carregar_imagem(caminho: Path) -> np.ndarray:
    imagem = cv2.imread(str(caminho))
    if imagem is None:
        raise FileNotFoundError(f"Nao foi possivel ler a imagem: {caminho}")
    return imagem


def converter_cinza(imagem: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def aplicar_gaussian_blur(imagem: np.ndarray, kernel: tuple[int, int] = (5, 5)) -> np.ndarray:
    return cv2.GaussianBlur(imagem, kernel, 0)


def aplicar_median_blur(imagem: np.ndarray, tamanho_kernel: int = 5) -> np.ndarray:
    return cv2.medianBlur(imagem, tamanho_kernel)


def equalizar_histograma(imagem: np.ndarray) -> np.ndarray:
    return cv2.equalizeHist(imagem)


def calcular_histograma(imagem: np.ndarray) -> np.ndarray:
    return cv2.calcHist([imagem], [0], None, [256], [0, 256])


def salvar_imagem(caminho: Path, imagem: np.ndarray) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(caminho), imagem):
        raise IOError(f"Nao foi possivel salvar a imagem: {caminho}")

def threshold_global(imagem: np.ndarray, limiar: int = 127) -> np.ndarray:
    _, binaria = cv2.threshold(imagem, limiar, 255, cv2.THRESH_BINARY)
    return binaria


def threshold_adaptativo(
    imagem: np.ndarray,
    tamanho_janela: int = 11,
    constante: int = 2,
) -> np.ndarray:
    return cv2.adaptiveThreshold(
        imagem,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        tamanho_janela,
        constante,
    )


def criar_kernel(tamanho: tuple[int, int] = (3, 3)) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_RECT, tamanho)


def dilatar(imagem: np.ndarray, kernel: np.ndarray, iteracoes: int = 1) -> np.ndarray:
    return cv2.dilate(imagem, kernel, iterations=iteracoes)


def erodir(imagem: np.ndarray, kernel: np.ndarray, iteracoes: int = 1) -> np.ndarray:
    return cv2.erode(imagem, kernel, iterations=iteracoes)


def abrir(imagem: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return cv2.morphologyEx(imagem, cv2.MORPH_OPEN, kernel)


def fechar(imagem: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return cv2.morphologyEx(imagem, cv2.MORPH_CLOSE, kernel)


def canny(imagem: np.ndarray, limiar1: int = 100, limiar2: int = 200) -> np.ndarray:
    return cv2.Canny(imagem, limiar1, limiar2)
