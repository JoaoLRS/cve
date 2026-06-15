from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk
import cv2
from PIL import Image
import json

import db
import detector


class VideoTela(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Estado da reprodução do vídeo
        self.video_path = db.DATA_DIR / "carPark.mp4"
        self.captura = None
        self.play_ativo = False
        self.pipeline_config = {}
        self.total_frames = 0
        self.fps = 24
        self.frame_atual_idx = 0
        self.velocidade = 1.0
        self.aba_ativa = "resultado"  # 'resultado' ou 'filtro'

        # Layout Principal
        self.grid_rowconfigure(0, weight=0)  # Cabecalho
        self.grid_rowconfigure(1, weight=1)  # Exibição do vídeo
        self.grid_rowconfigure(2, weight=0)  # Controles de reprodução
        self.grid_rowconfigure(3, weight=0)  # Rodape/Voltar
        self.grid_columnconfigure(0, weight=1)

        # 1. Cabeçalho
        self.cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        self.cabecalho.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.cabecalho.grid_columnconfigure(0, weight=1)
        self.cabecalho.grid_columnconfigure(1, weight=0)

        self.titulo = ctk.CTkLabel(
            self.cabecalho,
            text=f"Vídeo: {self.video_path.name}",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
        )
        self.titulo.grid(row=0, column=0, sticky="w")

        # Seleção de Pipeline
        self.pipeline_frame = ctk.CTkFrame(self.cabecalho, fg_color="transparent")
        self.pipeline_frame.grid(row=0, column=1, sticky="e")

        self.lbl_pipe = ctk.CTkLabel(self.pipeline_frame, text="Pipeline Utilizado: ", font=ctk.CTkFont(size=12))
        self.lbl_pipe.pack(side="left", padx=5)

        self.cb_pipelines = ctk.CTkOptionMenu(
            self.pipeline_frame,
            values=[],
            command=self.alterar_pipeline,
        )
        self.cb_pipelines.pack(side="left")

        # Abas de Visualização (Abas de resultado vs binarizado)
        self.abas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.abas_frame.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        self.btn_aba_res = ctk.CTkButton(
            self.abas_frame,
            text="Resultado Final",
            width=120,
            command=lambda: self.definir_aba("resultado"),
            fg_color="#1f538d",
        )
        self.btn_aba_res.pack(side="left", padx=2)

        self.btn_aba_filt = ctk.CTkButton(
            self.abas_frame,
            text="Filtro Aplicado (Binário)",
            width=150,
            command=lambda: self.definir_aba("filtro"),
            fg_color="#3a3a3a",
        )
        self.btn_aba_filt.pack(side="left", padx=2)

        # 2. Tela de Exibição de Vídeo (Canvas ou Label)
        self.video_canvas = ctk.CTkLabel(self, text="Carregando vídeo...", fg_color="black")
        self.video_canvas.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        # 3. Controles de Reprodução
        self.controles = ctk.CTkFrame(self)
        self.controles.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.controles.grid_columnconfigure(3, weight=1)

        self.btn_play = ctk.CTkButton(
            self.controles,
            text="Play",
            width=80,
            command=self.alternar_play_pause,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="white",
        )
        self.btn_play.grid(row=0, column=0, padx=10, pady=10)

        self.btn_restart = ctk.CTkButton(
            self.controles,
            text="Reiniciar",
            width=80,
            command=self.reiniciar_video,
            fg_color="#e67e22",
            hover_color="#d35400",
        )
        self.btn_restart.grid(row=0, column=1, padx=10, pady=10)

        # Velocidade
        self.lbl_vel = ctk.CTkLabel(self.controles, text="Velocidade:")
        self.lbl_vel.grid(row=0, column=2, padx=(15, 5), pady=10)

        self.cb_velocidade = ctk.CTkOptionMenu(
            self.controles,
            values=["0.5x", "1.0x", "1.5x", "2.0x"],
            width=80,
            command=self.alterar_velocidade,
        )
        self.cb_velocidade.grid(row=0, column=3, sticky="w", padx=5, pady=10)
        self.cb_velocidade.set("1.0x")

        # Timeline Slider
        self.slider_timeline = ctk.CTkSlider(self.controles, from_=0, to=100, command=self.arrastar_timeline)
        self.slider_timeline.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")
        self.slider_timeline.set(0)

        # 4. Rodapé/Voltar
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_voltar = ctk.CTkButton(
            self.footer,
            text="Voltar",
            fg_color="#a0a0a0",
            hover_color="#808080",
            text_color="black",
            command=self.voltar_menu,
        )
        self.btn_voltar.pack(side="left")

        self.imagem_referencia = None

    def carregar_dados_video(self):
        # Atualiza a combo box de pipelines
        pipes = db.listar_pipelines()
        self.cb_pipelines.configure(values=pipes)
        if pipes:
            self.cb_pipelines.set(pipes[0])
            self.alterar_pipeline(pipes[0])

        # Inicializa a captura do vídeo
        caminho_base_video = db.BASE_DIR / "data" / "carPark.mp4"
        
        # Garante que self.video_path seja um objeto Path absoluto e correto
        self.video_path = caminho_base_video

        # Se o arquivo não existir fisicamente ali, avisa o usuário em vez de quebrar
        if not self.video_path.exists():
            messagebox.showerror(
                "Arquivo Não Encontrado", 
                f"O arquivo de vídeo não foi encontrado na pasta do projeto:\n{self.video_path}\n\n"
                f"Certifique-se de que o arquivo 'carPark.mp4' está dentro da pasta 'data'."
            )
            return

        # Para caminhos com acento no Windows, converter para string absoluta ajuda o OpenCV
        caminho_str = str(self.video_path.resolve())
        self.captura = cv2.VideoCapture(caminho_str)
        if not self.captura.isOpened():
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo de vídeo: {self.video_path}")
            return

        self.total_frames = int(self.captura.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.captura.get(cv2.CAP_PROP_FPS))
        if self.fps <= 0:
            self.fps = 24

        self.slider_timeline.configure(to=self.total_frames - 1)
        self.frame_atual_idx = 0
        self.slider_timeline.set(0)

        # Mostra o primeiro frame
        self.atualizar_tela_com_frame_atual()

    def alternar_play_pause(self):
        self.play_ativo = not self.play_ativo
        if self.play_ativo:
            self.btn_play.configure(text="Pause", fg_color="#e74c3c", hover_color="#c0392b")
            self.reproduzir_loop()
        else:
            self.btn_play.configure(text="Play", fg_color="#2ecc71", hover_color="#27ae60")

    def reproduzir_loop(self):
        if not self.play_ativo:
            return

        if self.captura is None:
            return

        # Lê o frame
        ret, frame = self.captura.read()
        if not ret:
            # Reseta o vídeo no fim
            self.captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_atual_idx = 0
            ret, frame = self.captura.read()

        self.frame_atual_idx = int(self.captura.get(cv2.CAP_PROP_POS_FRAMES))
        self.slider_timeline.set(self.frame_atual_idx)

        # Processa e exibe
        self.processar_e_exibir_frame(frame)

        # Calcula o delay de frames (24 fps -> 1000/24 = 41.6ms)
        delay = int((1000 / self.fps) / self.velocidade)

        # Agenda a próxima leitura
        self.after(delay, self.reproduzir_loop)

    def processar_e_exibir_frame(self, frame):
        if frame is None:
            return

        # Carrega vagas (usando id 0 ou id da primeira imagem do banco)
        vagas = db.obter_vagas_imagem(0)
        if not vagas:
            # Se não tem na tabela do db, tenta carregar do vagas.json
            json_path = db.DATA_DIR / "vagas.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    vagas = [tuple(v) for v in json.load(f)]

        if not vagas:
            # Caso limite
            vagas = []

        limiar = self.pipeline_config.get("limiar_vaga_livre", 900)

        # Executa PDI
        binario_final, etapas = detector.processar_frame_intermediarios(frame, self.pipeline_config)

        if self.aba_ativa == "resultado":
            frame_anotado, livres, _ = detector.classificar_vagas(frame, binario_final, vagas, limiar)
            detector.desenhar_contador(frame_anotado, livres, len(vagas))
            img_exibir = frame_anotado
        else:
            # Converte binário para RGB para visualização
            img_exibir = cv2.cvtColor(binario_final, cv2.COLOR_GRAY2BGR)

        # Redimensiona para caber na GUI mantendo proporção (ex: 800x520)
        h_target, w_target = 520, 800
        img_redim = cv2.resize(img_exibir, (w_target, h_target))

        # Converte de BGR para RGB para o Tkinter
        img_rgb = cv2.cvtColor(img_redim, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w_target, h_target))

        self.video_canvas.configure(image=ctk_img, text="")
        self.imagem_referencia = ctk_img  # GC prevention

    def atualizar_tela_com_frame_atual(self):
        if self.captura is None:
            return
        self.captura.set(cv2.CAP_PROP_POS_FRAMES, self.frame_atual_idx)
        ret, frame = self.captura.read()
        if ret:
            self.processar_e_exibir_frame(frame)

    def arrastar_timeline(self, valor):
        self.frame_atual_idx = int(float(valor))
        self.atualizar_tela_com_frame_atual()

    def reiniciar_video(self):
        self.frame_atual_idx = 0
        self.slider_timeline.set(0)
        self.atualizar_tela_com_frame_atual()

    def alterar_velocidade(self, valor):
        self.velocidade = float(valor.replace("x", ""))

    def definir_aba(self, aba):
        self.aba_ativa = aba
        if aba == "resultado":
            self.btn_aba_res.configure(fg_color="#1f538d")
            self.btn_aba_filt.configure(fg_color="#3a3a3a")
        else:
            self.btn_aba_res.configure(fg_color="#3a3a3a")
            self.btn_aba_filt.configure(fg_color="#1f538d")

        # Atualiza o frame corrente na tela com a nova aba de visualização
        self.atualizar_tela_com_frame_atual()

    def alterar_pipeline(self, nome_pipeline):
        config = db.obter_pipeline(nome_pipeline)
        if config:
            self.pipeline_config = config
            self.atualizar_tela_com_frame_atual()

    def voltar_menu(self):
        self.play_ativo = False
        if self.captura:
            self.captura.release()
            self.captura = None
        self.controller.mostrar_tela("Menu")
