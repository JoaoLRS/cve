import json
from pathlib import Path, PureWindowsPath
from tkinter import messagebox, simpledialog
import customtkinter as ctk
import cv2
from PIL import Image
import numpy as np
import db
import detector


class ProcessamentoTela(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.imagem_id = None
        self.imagem_dados = None
        self.pipeline_config = {}

        # Configuração de Layout Dividido: Esquerda (Filtros), Direita (Visualização)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=350)  # Filtros (Fixo)
        self.grid_columnconfigure(1, weight=1)  # Visualização / Resultados

        # ---------------- ESQUERDA: PAINEL DE FILTROS ----------------
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.sidebar.grid_rowconfigure((0, 1, 2, 3), weight=0)
        self.sidebar.grid_rowconfigure(4, weight=1)  # Área de sliders rolável

        # Título lateral
        self.lbl_filtro_titulo = ctk.CTkLabel(
            self.sidebar,
            text="Configuração do Pipeline",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
        )
        self.lbl_filtro_titulo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Dropdown de Pipelines
        self.lbl_select_pipe = ctk.CTkLabel(self.sidebar, text="Pipeline selecionado:", font=ctk.CTkFont(size=12))
        self.lbl_select_pipe.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")

        self.cb_pipelines = ctk.CTkOptionMenu(
            self.sidebar,
            values=[],
            command=self.carregar_pipeline_selecionado,
        )
        self.cb_pipelines.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Botão para salvar o pipeline atual
        self.btn_salvar_pipe = ctk.CTkButton(
            self.sidebar,
            text="Salvar pipeline",
            command=self.salvar_pipeline_atual,
            fg_color="#2c82c9",
            hover_color="#1e5885",
        )
        self.btn_salvar_pipe.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # ScrollFrame para os Sliders de Configuração
        self.sliders_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.sliders_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.sliders_frame.grid_columnconfigure(0, weight=1)

        # Criar Controles/Sliders
        self.criar_controles_filtros()

        # Botões de Ação no Fim da Sidebar
        self.action_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.action_frame.grid(row=5, column=0, padx=20, pady=15, sticky="ew")

        self.btn_processar = ctk.CTkButton(
            self.action_frame,
            text="Processar imagem",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self.executar_processamento,
        )
        self.btn_processar.pack(fill="x", pady=5)

        self.btn_voltar = ctk.CTkButton(
            self.action_frame,
            text="Voltar ao banco de imagens",
            fg_color="#7f8c8d",
            hover_color="#636e72",
            command=lambda: self.controller.mostrar_tela("Imagem"),
        )
        self.btn_voltar.pack(fill="x", pady=5)

        # ---------------- DIREITA: VISUALIZAÇÃO E RESULTADOS ----------------
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_rowconfigure(0, weight=0)  # Título / Info
        self.main_content.grid_rowconfigure(1, weight=0)  # Linha do Pipeline
        self.main_content.grid_rowconfigure(2, weight=1)  # Grid de Cards de imagem
        self.main_content.grid_columnconfigure(0, weight=1)

        # Cabeçalho da Direita
        self.info_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        self.lbl_titulo_img = ctk.CTkLabel(
            self.info_frame,
            text="Processamento da imagem: ...",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
        )
        self.lbl_titulo_img.pack(side="left", anchor="w")

        # Botões de marcação e gabarito
        self.btn_marcar = ctk.CTkButton(
            self.info_frame,
            text="Marcar Vagas",
            font=ctk.CTkFont(size=12),
            fg_color="#8e44ad",
            hover_color="#732d91",
            command=self.marcar_vagas_interativo,
        )
        self.btn_marcar.pack(side="right", padx=5)

        self.btn_gabarito = ctk.CTkButton(
            self.info_frame,
            text="Editar Gabarito",
            font=ctk.CTkFont(size=12),
            fg_color="#d35400",
            hover_color="#a04000",
            command=self.editar_gabarito_interativo,
        )
        self.btn_gabarito.pack(side="right", padx=5)

        # Indicador visual do Pipeline Utilizado
        self.lbl_fluxo_pipe = ctk.CTkLabel(
            self.main_content,
            text="Pipeline utilizado: imagem original ➔ escala de cinza ➔ suavização ➔ limiarização adaptativa ➔ filtro de mediana ➔ dilatação ➔ resultado final",
            font=ctk.CTkFont(family="Helvetica", size=12, slant="italic"),
            text_color="#3498db",
        )
        self.lbl_fluxo_pipe.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Grid de cards com scroll para os resultados do processamento
        self.results_scroll = ctk.CTkScrollableFrame(self.main_content)
        self.results_scroll.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.results_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        # Cache de imagens para exibição
        self.imagens_processadas_cache = []

    def criar_controles_filtros(self):
        # 1. Gaussian Blur Kernel
        self.lbl_gauss = ctk.CTkLabel(self.sliders_frame, text="Gaussian Blur Kernel (ímpar):")
        self.lbl_gauss.pack(anchor="w", padx=10, pady=(10, 0))
        self.slider_gauss = ctk.CTkSlider(self.sliders_frame, from_=1, to=15, number_of_steps=7, command=self.ajustar_gauss)
        self.slider_gauss.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_gauss.set(3)

        # 2. Adaptive Threshold Block Size
        self.lbl_thresh_block = ctk.CTkLabel(self.sliders_frame, text="Adaptive Thresh Janela (ímpar):")
        self.lbl_thresh_block.pack(anchor="w", padx=10, pady=0)
        self.slider_thresh_block = ctk.CTkSlider(self.sliders_frame, from_=3, to=51, number_of_steps=24, command=self.ajustar_thresh_block)
        self.slider_thresh_block.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_thresh_block.set(25)

        # 3. Adaptive Threshold C
        self.lbl_thresh_c = ctk.CTkLabel(self.sliders_frame, text="Adaptive Thresh C:")
        self.lbl_thresh_c.pack(anchor="w", padx=10, pady=0)
        self.slider_thresh_c = ctk.CTkSlider(self.sliders_frame, from_=1, to=30, number_of_steps=29, command=self.ajustar_thresh_c)
        self.slider_thresh_c.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_thresh_c.set(16)

        # 4. Median Blur Kernel
        self.lbl_median = ctk.CTkLabel(self.sliders_frame, text="Median Blur Kernel (ímpar):")
        self.lbl_median.pack(anchor="w", padx=10, pady=0)
        self.slider_median = ctk.CTkSlider(self.sliders_frame, from_=1, to=15, number_of_steps=7, command=self.ajustar_median)
        self.slider_median.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_median.set(5)

        # 5. Morphological Kernel Size
        self.lbl_morph_k = ctk.CTkLabel(self.sliders_frame, text="Kernel Morfológico (ímpar):")
        self.lbl_morph_k.pack(anchor="w", padx=10, pady=0)
        self.slider_morph_k = ctk.CTkSlider(self.sliders_frame, from_=1, to=9, number_of_steps=4, command=self.ajustar_morph_k)
        self.slider_morph_k.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_morph_k.set(3)

        # 6. Morphological Iterations
        self.lbl_morph_it = ctk.CTkLabel(self.sliders_frame, text="Dilatação - número de iterações:")
        self.lbl_morph_it.pack(anchor="w", padx=10, pady=0)
        self.slider_morph_it = ctk.CTkSlider(self.sliders_frame, from_=1, to=5, number_of_steps=4, command=self.ajustar_morph_it)
        self.slider_morph_it.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_morph_it.set(1)

        # 7. Limiar Vaga Livre (Count non zero pixels)
        self.lbl_limiar = ctk.CTkLabel(self.sliders_frame, text="Limiar para classificar vaga livre:")
        self.lbl_limiar.pack(anchor="w", padx=10, pady=0)
        self.slider_limiar = ctk.CTkSlider(self.sliders_frame, from_=100, to=3000, number_of_steps=29, command=self.ajustar_limiar)
        self.slider_limiar.pack(fill="x", padx=10, pady=(0, 10))
        self.slider_limiar.set(900)

    # Métodos auxiliares de ajuste de valores ímpares nos sliders
    def ajustar_gauss(self, val):
        val = int(float(val))
        if val % 2 == 0:
            val += 1
        self.lbl_gauss.configure(text=f"Gaussian Blur Kernel (ímpar): {val}x{val}")
        self.pipeline_config["gaussian_kernel"] = [val, val]

    def ajustar_thresh_block(self, val):
        val = int(float(val))
        if val % 2 == 0:
            val += 1
        self.lbl_thresh_block.configure(text=f"Adaptive Thresh Janela (ímpar): {val}")
        self.pipeline_config["adaptive_block_size"] = val

    def ajustar_thresh_c(self, val):
        val = int(float(val))
        self.lbl_thresh_c.configure(text=f"Adaptive Thresh C: {val}")
        self.pipeline_config["adaptive_c"] = val

    def ajustar_median(self, val):
        val = int(float(val))
        if val % 2 == 0:
            val += 1
        self.lbl_median.configure(text=f"Median Blur Kernel (ímpar): {val}")
        self.pipeline_config["median_kernel"] = val

    def ajustar_morph_k(self, val):
        val = int(float(val))
        if val % 2 == 0:
            val += 1
        self.lbl_morph_k.configure(text=f"Kernel Morfológico (ímpar): {val}x{val}")
        self.pipeline_config["morph_kernel"] = [val, val]

    def ajustar_morph_it(self, val):
        val = int(float(val))
        self.lbl_morph_it.configure(text=f"Dilatação - número de iterações: {val}")
        self.pipeline_config["morph_iterations"] = val

    def ajustar_limiar(self, val):
        val = int(float(val))
        self.lbl_limiar.configure(text=f"Limiar para classificar vaga livre: {val}")
        self.pipeline_config["limiar_vaga_livre"] = val

    def carregar_dados_imagem(self, imagem_id):
        self.imagem_id = imagem_id
        self.imagem_dados = db.obter_imagem(imagem_id)

        # Atualiza título da tela
        self.lbl_titulo_img.configure(text=f"Processamento da imagem: {self.imagem_dados['nome']}")

        # Atualiza lista de pipelines no OptionMenu
        pipes = db.listar_pipelines()
        self.cb_pipelines.configure(values=pipes)
        if pipes:
            self.cb_pipelines.set(pipes[0])
            self.carregar_pipeline_selecionado(pipes[0])

        # Executa processamento inicial
        self.executar_processamento()

    def carregar_pipeline_selecionado(self, nome_pipeline):
        config = db.obter_pipeline(nome_pipeline)
        if config:
            self.pipeline_config = config
            # Atualiza os sliders fisicamente na tela
            self.slider_gauss.set(config.get("gaussian_kernel", [3, 3])[0])
            self.ajustar_gauss(config.get("gaussian_kernel", [3, 3])[0])

            self.slider_thresh_block.set(config.get("adaptive_block_size", 25))
            self.ajustar_thresh_block(config.get("adaptive_block_size", 25))

            self.slider_thresh_c.set(config.get("adaptive_c", 16))
            self.ajustar_thresh_c(config.get("adaptive_c", 16))

            self.slider_median.set(config.get("median_kernel", 5))
            self.ajustar_median(config.get("median_kernel", 5))

            self.slider_morph_k.set(config.get("morph_kernel", [3, 3])[0])
            self.ajustar_morph_k(config.get("morph_kernel", [3, 3])[0])

            self.slider_morph_it.set(config.get("morph_iterations", 1))
            self.ajustar_morph_it(config.get("morph_iterations", 1))

            self.slider_limiar.set(config.get("limiar_vaga_livre", 900))
            self.ajustar_limiar(config.get("limiar_vaga_livre", 900))

    def salvar_pipeline_atual(self):
        nome = simpledialog.askstring(
            "Salvar Pipeline",
            "Digite o nome para esta configuração de pipeline:"
            )
        if nome:
            db.salvar_pipeline(nome, self.pipeline_config)
            # Recarrega a combo box
            pipes = db.listar_pipelines()
            self.cb_pipelines.configure(values=pipes)
            self.cb_pipelines.set(nome)
            messagebox.showinfo("Pipeline salvo", f"O pipeline '{nome}' foi salvo com sucesso!")

    def executar_processamento(self):
        if not self.imagem_dados:
            return

        if isinstance(self.imagem_dados, dict):
            caminho_do_banco = self.imagem_dados.get("caminho") or self.imagem_dados.get("caminho_img")
        else:
            caminho_do_banco = self.imagem_dados[1]

        caminho_original = Path(caminho_do_banco)

        if not caminho_original.exists():
            caminho_img = db.BASE_DIR / "data" / "importadas" / caminho_original.name
        else:
            caminho_img = caminho_original      
            

        # Carrega a imagem via OpenCV
        if not caminho_img.exists():
            messagebox.showerror("Erro", f"Arquivo nao existe na pasta:\n{caminho_img}")
            return

        # Carrega a imagem via OpenCV suportando acentos no caminho (Windows)
        try:
            img_cv2 = cv2.imdecode(np.fromfile(str(caminho_img), dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            img_cv2 = None

        if img_cv2 is None:
            messagebox.showerror("Erro", f"Nao foi possivel carregar imagem: {caminho_img}")
            return

        # Carrega as vagas cadastradas para esta imagem
        vagas = db.obter_vagas_imagem(self.imagem_id)
        if not vagas:
            # Se nao tem vagas especificas, tenta carregar as vagas padrao do vagas.json/vagas.pkl
            vagas = db.obter_vagas_imagem(0) # imagem_id 0 sera reservada para padrao se existir
            if not vagas:
                # Se ainda assim nao achar, tenta ler do arquivo vagas.json padrao do projeto
                json_path = db.DATA_DIR / "vagas.json"
                if json_path.exists():
                    with open(json_path, "r", encoding="utf-8") as f:
                        vagas = [tuple(v) for v in json.load(f)]
                        # Cadastra como vagas padrao da imagem no SQLite
                        db.atualizar_vagas_imagem(self.imagem_id, vagas)

        # Executa processamento
        resultado = detector.processar_imagem_completo(img_cv2, self.pipeline_config, vagas)

        # Limpa visualizações anteriores
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        self.imagens_processadas_cache.clear()

        # Renderizar as etapas nos cards
        idx = 0
        colunas = 3

        # Renderiza primeiro as intermediarias
        for nome_etapa, img_etapa in resultado["imagens_intermediarias"].items():
            card = ctk.CTkFrame(self.results_scroll, corner_radius=8, border_width=1)
            row = idx // colunas
            col = idx % colunas
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Converte para exibir no TK
            img_rgb = cv2.cvtColor(img_etapa, cv2.COLOR_GRAY2RGB)
            pil_img = Image.fromarray(img_rgb)
            pil_img.thumbnail((230, 150))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(230, 150))

            lbl_img = ctk.CTkLabel(card, image=ctk_img, text="")
            lbl_img.pack(padx=10, pady=5)
            self.imagens_processadas_cache.append(ctk_img)

            lbl_nome = ctk.CTkLabel(card, text=nome_etapa, font=ctk.CTkFont(weight="bold"))
            lbl_nome.pack(pady=3)

            idx += 1

        # Renderiza a Final
        card_final = ctk.CTkFrame(self.results_scroll, corner_radius=8, border_width=2, border_color="#2ecc71")
        row = idx // colunas
        col = idx % colunas
        card_final.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        img_final_rgb = cv2.cvtColor(resultado["resultado_final"], cv2.COLOR_BGR2RGB)
        pil_final = Image.fromarray(img_final_rgb)
        pil_final.thumbnail((230, 150))
        ctk_final = ctk.CTkImage(light_image=pil_final, dark_image=pil_final, size=(230, 150))

        lbl_final = ctk.CTkLabel(card_final, image=ctk_final, text="")
        lbl_final.pack(padx=10, pady=5)
        self.imagens_processadas_cache.append(ctk_final)

        lbl_final_titulo = ctk.CTkLabel(card_final, text="Resultado final da detecção", font=ctk.CTkFont(weight="bold", size=13))
        lbl_final_titulo.pack(pady=2)

        # Estatísticas do Resultado Local
        total = len(vagas)
        livres = resultado["vagas_livres"]
        info_txt = f"Vagas livres detectadas: {livres} / Total de vagas: {total}"

        # Verifica se há Gabarito para calcular a taxa de acerto
        gabarito = db.obter_ground_truth(self.imagem_id)
        if gabarito:
            # gabarito e uma lista com indices ou estados
            # Vamos calcular a taxa de acerto local
            # Detalhes das vagas
            certos = 0
            for det in resultado["detalhes_vagas"]:
                vaga_idx = det["indice"] - 1 # 0-indexed
                real_livre = vaga_idx in gabarito # se o indice esta no gabarito, ela e livre real
                det_livre = det["status"] == "livre"
                if real_livre == det_livre:
                    certos += 1
            taxa_acerto = (certos / total) * 100 if total > 0 else 0
            info_txt += f"\nTaxa de acerto nesta imagem: {taxa_acerto:.1f}%"

        lbl_stats = ctk.CTkLabel(card_final, text=info_txt, font=ctk.CTkFont(size=11, slant="italic"))
        lbl_stats.pack(pady=2)

    def marcar_vagas_interativo(self):
        if not self.imagem_dados:
            return

        caminho_img = Path(self.imagem_dados["caminho"])

        if not caminho_img.exists():
            nome_arquivo = PureWindowsPath(self.imagem_dados["caminho"]).name
            caminho_img = db.DATA_DIR / "importadas" / nome_arquivo

        imagem = cv2.imread(str(caminho_img))
        if imagem is None:
            messagebox.showerror("Erro", f"Nao foi possivel abrir imagem: {caminho_img}")
            return

        # Carrega vagas existentes
        vagas = db.obter_vagas_imagem(self.imagem_id)

        largura_vaga = 107
        altura_vaga = 48
        nome_janela = "Marcação de Vagas - Clique para Adicionar / R-Clique para Remover"

        # Callback do mouse
        def mouse_callback(evento, x, y, flags, params):
            if evento == cv2.EVENT_LBUTTONDOWN:
                vagas.append((x, y))
            elif evento == cv2.EVENT_RBUTTONDOWN:
                for idx, (vx, vy) in enumerate(vagas):
                    if vx <= x <= vx + largura_vaga and vy <= y <= vy + altura_vaga:
                        vagas.pop(idx)
                        break

        cv2.namedWindow(nome_janela)
        cv2.setMouseCallback(nome_janela, mouse_callback)

        messagebox.showinfo("Instruções de Marcação", 
                            "Clique com o BOTÃO ESQUERDO para ADICIONAR uma vaga.\n"
                            "Clique com o BOTÃO DIREITO sobre uma vaga para REMOVER.\n"
                            "Pressione a tecla 'S' para salvar e sair.\n"
                            "Pressione 'Q' ou 'ESC' para sair sem salvar.")

        while True:
            temp_img = imagem.copy()
            for idx, (x, y) in enumerate(vagas):
                cv2.rectangle(temp_img, (x, y), (x + largura_vaga, y + altura_vaga), (255, 0, 255), 2)
                cv2.putText(temp_img, str(idx+1), (x+4, y+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

            cv2.imshow(nome_janela, temp_img)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("s"):
                db.atualizar_vagas_imagem(self.imagem_id, vagas)
                break
            elif tecla in (ord("q"), 27):
                break

        cv2.destroyAllWindows()
        self.executar_processamento()

    def editar_gabarito_interativo(self):
        if not self.imagem_dados:
            return

        vagas = db.obter_vagas_imagem(self.imagem_id)
        if not vagas:
            messagebox.showwarning("Aviso", "Antes de editar o gabarito, marque as vagas na imagem!")
            return

        # Carrega o gabarito atual
        gabarito = db.obter_ground_truth(self.imagem_id)

        # Pergunta de forma textual ou abre janela OpenCV para selecionar vagas livres no clique
        # Janela OpenCV é muito mais interativa para gabarito:
        # Ele mostra as vagas enumeradas, se ele clicar na vaga ela fica VERDE (livre) ou VERMELHA (ocupada).
        caminho_banco = Path(self.imagem_dados["caminho"])
        
        if not caminho_banco.exists():
            # Se mudou de pasta, reconstrói o caminho na pasta atual do projeto
            caminho_img = db.BASE_DIR / "data" / "importadas" / caminho_banco.name
        else:
            caminho_img = caminho_banco

        # Verificação física do arquivo
        if not caminho_img.exists():
            messagebox.showerror("Erro", f"Arquivo de imagem nao encontrado:\n{caminho_img}")
            return

        # Carrega a imagem tratando os acentos no caminho (Área de Trabalho/OneDrive)
        try:
            imagem = cv2.imdecode(np.fromfile(str(caminho_img), dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception:
            imagem = None

        if imagem is None:
            messagebox.showerror("Erro", f"Nao foi possivel abrir a imagem pelo OpenCV:\n{caminho_img}")
            return
        largura_vaga = 107
        altura_vaga = 48
        nome_janela = "Editar Gabarito - Clique para alternar Livre (Verde) / Ocupado (Vermelho)"

        # Converte gabarito para set para facilidade
        livres_set = set(gabarito)

        def mouse_callback(evento, x, y, flags, params):
            if evento == cv2.EVENT_LBUTTONDOWN:
                for idx, (vx, vy) in enumerate(vagas):
                    if vx <= x <= vx + largura_vaga and vy <= y <= vy + altura_vaga:
                        if idx in livres_set:
                            livres_set.remove(idx)
                        else:
                            livres_set.add(idx)
                        break

        cv2.namedWindow(nome_janela)
        cv2.setMouseCallback(nome_janela, mouse_callback)

        messagebox.showinfo("Instruções de Gabarito", 
                            "Clique com o BOTÃO ESQUERDO em uma vaga para alternar seu estado:\n"
                            "- Verde: Vaga Vazia (Livre)\n"
                            "- Vermelho: Vaga Ocupada\n"
                            "Pressione a tecla 'S' para salvar e sair.")

        while True:
            temp_img = imagem.copy()
            for idx, (x, y) in enumerate(vagas):
                cor = (0, 255, 0) if idx in livres_set else (0, 0, 255)
                cv2.rectangle(temp_img, (x, y), (x + largura_vaga, y + altura_vaga), cor, 2)
                cv2.putText(temp_img, f"V{idx+1}", (x+4, y+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 1)

            cv2.imshow(nome_janela, temp_img)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("s"):
                db.salvar_ground_truth(self.imagem_id, list(livres_set))
                break
            elif tecla in (ord("q"), 27):
                break

        cv2.destroyAllWindows()
        self.executar_processamento()
