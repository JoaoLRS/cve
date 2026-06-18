from pathlib import Path, PureWindowsPath
from tkinter import messagebox
import customtkinter as ctk
import cv2
import json

# Integração do Matplotlib com o Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

import db
import detector


class AvaliacaoTela(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Estado da avaliação
        self.pipeline_ativo = None
        self.imagens_avaliacao = []

        # Layout Principal: Esquerda (Configurações e Tabela), Direita (Matriz e Galeria)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=400)  # Configurações e Tabela
        self.grid_columnconfigure(1, weight=1)  # Gráficos e Galeria

        # ---------------- ESQUERDA: CONTROLES E MÉTRICAS ----------------
        self.esquerda_frame = ctk.CTkFrame(self, corner_radius=0)
        self.esquerda_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.esquerda_frame.grid_rowconfigure(4, weight=1)

        self.lbl_titulo = ctk.CTkLabel(
            self.esquerda_frame,
            text="Módulo de Avaliação em Lote",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
        )
        self.lbl_titulo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Seleção de Pipeline
        self.lbl_pipe = ctk.CTkLabel(self.esquerda_frame, text="Pipeline avaliado:")
        self.lbl_pipe.grid(row=1, column=0, padx=20, pady=(10, 2), sticky="w")

        self.cb_pipelines = ctk.CTkOptionMenu(self.esquerda_frame, values=[])
        self.cb_pipelines.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Botão para Executar a Avaliação
        self.btn_avaliar = ctk.CTkButton(
            self.esquerda_frame,
            text="Executar Avaliação das 30 imagens",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.executar_avaliacao_lote,
        )
        self.btn_avaliar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # ScrollFrame para Estatísticas Gerais e Comparação de Pipelines
        self.stats_scroll = ctk.CTkScrollableFrame(self.esquerda_frame, fg_color="transparent")
        self.stats_scroll.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.stats_scroll.grid_columnconfigure(0, weight=1)

        # Labels de Métricas Globais (inicialmente vazios)
        self.lbl_acuracia = ctk.CTkLabel(
            self.stats_scroll,
            text="Acurácia Geral: -",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_acuracia.pack(anchor="w", padx=10, pady=5)

        self.lbl_recall = ctk.CTkLabel(
            self.stats_scroll,
            text="Taxa de acerto das vagas livres: -",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71",
        )
        self.lbl_recall.pack(anchor="w", padx=10, pady=5)

        self.lbl_precisao = ctk.CTkLabel(
            self.stats_scroll,
            text="Precisão das vagas livres: -",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_precisao.pack(anchor="w", padx=10, pady=2)

        self.lbl_f1 = ctk.CTkLabel(
            self.stats_scroll,
            text="F1-Score: -",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_f1.pack(anchor="w", padx=10, pady=2)

        self.lbl_comparativo = ctk.CTkLabel(
            self.stats_scroll,
            text="\nTabela Comparativa de Pipelines:",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.lbl_comparativo.pack(anchor="w", padx=10, pady=(15, 5))

        self.txt_comparativo = ctk.CTkTextbox(self.stats_scroll, height=150, font=ctk.CTkFont(family="Courier", size=11))
        self.txt_comparativo.pack(fill="x", padx=10, pady=5)
        self.txt_comparativo.insert("0.0", "Execute a avaliação para comparar os pipelines cadastrados.")
        self.txt_comparativo.configure(state="disabled")

        # Botão para exportar relatório acadêmico
        self.btn_exportar = ctk.CTkButton(
            self.esquerda_frame,
            text="Exportar relatório da avaliação",
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.exportar_relatorio,
        )
        self.btn_exportar.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.btn_voltar = ctk.CTkButton(
            self.esquerda_frame,
            text="Voltar ao menu",
            fg_color="#7f8c8d",
            hover_color="#636e72",
            command=lambda: self.controller.mostrar_tela("Menu"),
        )
        self.btn_voltar.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="ew")

        # ---------------- DIREITA: MATRIZ DE CONFUSÃO E DETALHES ----------------
        self.direita_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.direita_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.direita_frame.grid_rowconfigure(0, weight=0)  # Título e Qtde imagens
        self.direita_frame.grid_rowconfigure(1, weight=1)  # Área da Matriz de Confusão
        self.direita_frame.grid_rowconfigure(2, weight=1)  # Galeria de miniaturas de lote
        self.direita_frame.grid_columnconfigure(0, weight=1)

        self.lbl_direita_titulo = ctk.CTkLabel(
            self.direita_frame,
            text="Resultados da avaliação nas imagens de teste",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
        )
        self.lbl_direita_titulo.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Matriz de Confusão Canvas Frame
        self.matriz_frame = ctk.CTkFrame(self.direita_frame)
        self.matriz_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.lbl_matriz_info = ctk.CTkLabel(
            self.matriz_frame,
            text="A matriz de confusão será exibida após executar a avaliação.",
            font=ctk.CTkFont(slant="italic"),
        )
        self.lbl_matriz_info.pack(expand=True, fill="both")

        # Galeria de lote com scroll
        self.galeria_scroll = ctk.CTkScrollableFrame(self.direita_frame, orientation="horizontal", label_text="Imagens avaliadas")
        self.galeria_scroll.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.resultado_benchmark_ultimo = {}

    def carregar_dados_avaliacao(self):
        # Atualiza a combo box de pipelines
        pipes = db.listar_pipelines()
        self.cb_pipelines.configure(values=pipes)
        if pipes:
            self.cb_pipelines.set(pipes[0])

        # Verifica quantidade de imagens com gabarito no banco
        imagens = db.listar_imagens()
        lote_gabarito = []
        for img in imagens:
            gab = db.obter_ground_truth(img["id"])
            if gab:
                lote_gabarito.append(img)

        self.imagens_avaliacao = lote_gabarito

        # Atualiza título com quantidade de imagens com gabarito no banco
        self.lbl_direita_titulo.configure(
            text=f"Resultados da avaliação nas imagens de teste (lote atual: {len(lote_gabarito)} imagens com gabarito)"
        )

        # Renderiza a galeria de miniaturas de teste
        self.renderizar_galeria_lote()

    def renderizar_galeria_lote(self):
        for widget in self.galeria_scroll.winfo_children():
            widget.destroy()

        if not self.imagens_avaliacao:
            lbl_vazio = ctk.CTkLabel(
                self.galeria_scroll,
                text="Nenhuma imagem de teste com gabarito (Ground Truth) cadastrado no banco.\n"
                "Importe imagens e use a tela de Processamento para marcar as vagas e o gabarito de cada uma.",
                font=ctk.CTkFont(size=12, slant="italic"),
            )
            lbl_vazio.pack(padx=20, pady=20)
            return

        for img in self.imagens_avaliacao:
            card = ctk.CTkFrame(self.galeria_scroll, corner_radius=6, border_width=1, width=120)
            card.pack(side="left", padx=5, pady=5)

            lbl_nome = ctk.CTkLabel(
                card,
                text=img["nome"],
                font=ctk.CTkFont(size=10, weight="bold"),
                wraplength=100,
            )
            lbl_nome.pack(padx=5, pady=5)

            vagas = db.obter_vagas_imagem(img["id"])
            gab = db.obter_ground_truth(img["id"])
            lbl_info = ctk.CTkLabel(
                card,
                text=f"Vagas marcadas: {len(vagas)}\nLivres no gabarito: {len(gab)}",
                font=ctk.CTkFont(size=9),
                text_color="gray",
            )
            lbl_info.pack(padx=5, pady=5)

    def executar_avaliacao_lote(self):
        nome_pipe = self.cb_pipelines.get()
        if not nome_pipe:
            messagebox.showwarning(
                "Pipeline não selecionado",
                "Selecione um pipeline antes de executar a avaliação."
            )
            return

        if len(self.imagens_avaliacao) < 1:
            # Força o cadastro de pelo menos 1 imagem com gabarito antes do benchmark.
            # Idealmente, o professor quer pelo menos 30. Vamos alertar.
            messagebox.showwarning(
                "Aviso de Dados",
                "Você precisa ter imagens de teste cadastradas com gabaritos de vagas no banco de dados.\n"
                f"Lote atual tem apenas {len(self.imagens_avaliacao)} imagens. Recomenda-se carregar pelo menos 30 imagens.",
            )
            if not self.imagens_avaliacao:
                return

        config_avaliar = db.obter_pipeline(nome_pipe)

        # Variáveis da Matriz de Confusão Geral
        # TP = Vaga vazia classificada como vazia
        # FP = Vaga ocupada classificada como vazia
        # FN = Vaga vazia classificada como ocupada
        # TN = Vaga ocupada classificada como ocupada
        tp = fp = fn = tn = 0

        detalhes_lote = []

        # Processa cada imagem do lote
        for img_dados in self.imagens_avaliacao:
            caminho_img = Path(img_dados["caminho"])

            if not caminho_img.exists():
                nome_arquivo = PureWindowsPath(img_dados["caminho"]).name
                caminho_img = db.DATA_DIR / "importadas" / nome_arquivo

            img_cv2 = cv2.imread(str(caminho_img))
            if img_cv2 is None:
                continue

            vagas = db.obter_vagas_imagem(img_dados["id"])
            gabarito = db.obter_ground_truth(img_dados["id"])  # Lista com índices das vagas livres reais
            gabarito_set = set(gabarito)

            resultado = detector.processar_imagem_completo(img_cv2, config_avaliar, vagas)

            certos_img = 0
            total_img = len(vagas)

            for det in resultado["detalhes_vagas"]:
                vaga_idx = det["indice"] - 1  # 0-indexed
                real_livre = vaga_idx in gabarito_set
                det_livre = det["status"] == "livre"

                # Classificação para a Matriz de Confusão
                if real_livre and det_livre:
                    tp += 1
                elif not real_livre and det_livre:
                    fp += 1
                elif real_livre and not det_livre:
                    fn += 1
                elif not real_livre and not det_livre:
                    tn += 1

                if real_livre == det_livre:
                    certos_img += 1

            taxa_acerto_img = (certos_img / total_img) * 100 if total_img > 0 else 0
            detalhes_lote.append(
                {
                    "imagem": img_dados["nome"],
                    "vagas": total_img,
                    "livres_detectadas": resultado["vagas_livres"],
                    "livres_reais": len(gabarito),
                    "acerto": taxa_acerto_img,
                }
            )

        # Cálculo das métricas estatísticas globais
        total_classificacoes = tp + fp + fn + tn
        acuracia = ((tp + tn) / total_classificacoes) * 100 if total_classificacoes > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0  # Taxa de acerto de vagas vazias
        precisao = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        f1_score = (2 * precisao * recall) / (precisao + recall) if (precisao + recall) > 0 else 0

        # Atualiza tela
        self.lbl_acuracia.configure(text=f"Acurácia Geral: {acuracia:.2f}%")
        self.lbl_recall.configure(text=f"Taxa de acerto das vagas livres: {recall:.2f}%")
        self.lbl_precisao.configure(text=f"Precisão das vagas livres: {precisao:.2f}%")
        self.lbl_f1.configure(text=f"F1-Score: {f1_score:.2f}%")

        # Armazena resultados para exportar depois
        self.resultado_benchmark_ultimo = {
            "pipeline": nome_pipe,
            "lote_tamanho": len(self.imagens_avaliacao),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "acuracia": acuracia,
            "recall": recall,
            "precisao": precisao,
            "f1_score": f1_score,
            "detalhes": detalhes_lote,
        }

        # Plota Matriz de Confusão no Canvas do TK
        self.plotar_matriz_confusao(tp, fp, fn, tn)

        # Executa comparação em lote com todos os pipelines do banco de dados
        self.comparar_pipelines_banco(nome_pipe)

    def plotar_matriz_confusao(self, tp, fp, fn, tn):
        # Limpa o frame da matriz
        for widget in self.matriz_frame.winfo_children():
            widget.destroy()

        # Configuração do gráfico
        fig, ax = plt.subplots(figsize=(4.5, 3.2), dpi=100)
        fig.patch.set_facecolor("#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#f2f2f2")
        ax.set_facecolor("#2b2b2b")

        matriz = np.array([[tn, fp], [fn, tp]])

        im = ax.imshow(matriz, cmap="Blues", interpolation="nearest")

        # Configuração de rótulos
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Ocupada", "Livre"], color="white" if ctk.get_appearance_mode() == "Dark" else "black")
        ax.set_yticklabels(["Ocupada", "Livre"], color="white" if ctk.get_appearance_mode() == "Dark" else "black")
        ax.set_xlabel("Predito", color="white" if ctk.get_appearance_mode() == "Dark" else "black", fontsize=10)
        ax.set_ylabel("Real", color="white" if ctk.get_appearance_mode() == "Dark" else "black", fontsize=10)
        ax.set_title("Matriz de Confusão Geral\nClasse positiva: Vaga livre", color="white" if ctk.get_appearance_mode() == "Dark" else "black", fontsize=11, weight="bold")

        # Adiciona valores textuais na matriz
        rotulos = [
            [f"TN\n{tn}", f"FP\n{fp}"],
            [f"FN\n{fn}", f"TP\n{tp}"],
        ]

        for i in range(2):
            for j in range(2):
                val = matriz[i, j]
                ax.text(
                    j,
                    i,
                    rotulos[i][j],
                    ha="center",
                    va="center",
                    color="white" if val > (matriz.max() / 2) else "black",
                    fontweight="bold",
                    fontsize=12,
                )
        fig.tight_layout()

        # Adiciona canvas no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.matriz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def comparar_pipelines_banco(self, pipeline_ativo_nome):
        pipelines = db.listar_pipelines()
        resultados_comparacao = []

        for pipe_nome in pipelines:
            config = db.obter_pipeline(pipe_nome)
            # Executa avaliação rápida
            tp = fp = fn = tn = 0
            for img_dados in self.imagens_avaliacao:
                caminho_img = Path(img_dados["caminho"])

                if not caminho_img.exists():
                    nome_arquivo = PureWindowsPath(img_dados["caminho"]).name
                    caminho_img = db.DATA_DIR / "importadas" / nome_arquivo

                img_cv2 = cv2.imread(str(caminho_img))
                if img_cv2 is None:
                    continue

                vagas = db.obter_vagas_imagem(img_dados["id"])
                gabarito = db.obter_ground_truth(img_dados["id"])
                gabarito_set = set(gabarito)

                resultado = detector.processar_imagem_completo(img_cv2, config, vagas)
                for det in resultado["detalhes_vagas"]:
                    vaga_idx = det["indice"] - 1
                    real_livre = vaga_idx in gabarito_set
                    det_livre = det["status"] == "livre"

                    if real_livre and det_livre:
                        tp += 1
                    elif not real_livre and det_livre:
                        fp += 1
                    elif real_livre and not det_livre:
                        fn += 1
                    elif not real_livre and not det_livre:
                        tn += 1

            total = tp + fp + fn + tn
            acuracia = ((tp + tn) / total) * 100 if total > 0 else 0
            recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
            resultados_comparacao.append(f"{pipe_nome:<20} | Acc: {acuracia:6.2f}% | Rec: {recall:6.2f}%")

        self.txt_comparativo.configure(state="normal")
        self.txt_comparativo.delete("0.0", "end")
        header = f"{'Pipeline':<20} | {'Acurácia':<8} | {'Recall':<8}\n"
        header += "-" * 42 + "\n"
        self.txt_comparativo.insert("end", header)
        for res in resultados_comparacao:
            self.txt_comparativo.insert("end", res + "\n")
        self.txt_comparativo.configure(state="disabled")

    def exportar_relatorio(self):
        if not self.resultado_benchmark_ultimo:
            messagebox.showwarning(
                 "Avaliação não executada",
                 "Execute a avaliação em lote antes de exportar o relatório."
                )
            return

        caminho_saida = db.BASE_DIR / "resultados" / "relatorio_avaliacao.md"
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)

        res = self.resultado_benchmark_ultimo

        markdown_content = f"""# Relatório de Avaliação de Desempenho - Detecção de Vagas

**Pipeline Avaliado:** {res["pipeline"]}  
**Tamanho do Lote de Teste:** {res["lote_tamanho"]} imagens  

---

## 1. Métricas Estatísticas Globais

*   **Acurácia Geral (Taxa de Acerto):** {res["acuracia"]:.2f}%
*   **Recall de Vagas Vazias (Taxa de Acerto Específica):** {res["recall"]:.2f}%
*   **Precisão de Vagas Vazias:** {res["precisao"]:.2f}%
*   **F1-Score:** {res["f1_score"]:.2f}%

---

## 2. Matriz de Confusão Geral

| Real \\ Predito | Ocupada (Negativo) | Livre (Positivo) |
| :--- | :---: | :---: |
| **Ocupada (Real)** | {res["tn"]} (Verdadeiro Negativo) | {res["fp"]} (Falso Positivo) |
| **Livre (Real)** | {res["fn"]} (Falso Negativo) | {res["tp"]} (Verdadeiro Positivo) |

---

## 3. Desempenho Detalhado por Imagem

| Imagem | Total de Vagas | Vagas Livres Reais | Vagas Livres Detectadas | Taxa de Acerto |
| :--- | :---: | :---: | :---: | :---: |
"""

        for det in res["detalhes"]:
            markdown_content += f"| {det['imagem']} | {det['vagas']} | {det['livres_reais']} | {det['livres_detectadas']} | {det['acerto']:.1f}% |\n"

        markdown_content += """
---
*Relatório gerado automaticamente pelo sistema CVE de Contabilização de Vagas.*
"""

        try:
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            messagebox.showinfo(
                "Exportação Concluída",
                f"Relatório exportado com sucesso em:\n{caminho_saida}\n\nO arquivo contém as métricas, a matriz de confusão e o desempenho por imagem.",
            )
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o relatório: {e}")
