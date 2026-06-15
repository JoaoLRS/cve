import customtkinter as ctk

class MenuTela(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout centralizado
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # Titulo Principal
        self.titulo = ctk.CTkLabel(
            self,
            text="CVE - Contabilização de vagas de estacionamento",
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color="#1f538d"
        )
        self.titulo.grid(row=1, column=0, columnspan=3, padx=20, pady=20, sticky="n")

        # Subtitulo/Descricao
        self.subtitulo = ctk.CTkLabel(
            self,
            text="Selecione o modo de operação para iniciar o processamento de imagens",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color="gray"
        )
        self.subtitulo.grid(row=1, column=0, columnspan=3, padx=20, pady=(60, 20), sticky="n")

        # Frame para os Botoes
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.btn_frame.grid_rowconfigure(0, weight=1)

        # Botao Imagem
        self.btn_imagem = ctk.CTkButton(
            self.btn_frame,
            text="Módulo Imagem\n(CDU-02 / CDU-03)",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            height=80,
            width=200,
            corner_radius=12,
            command=lambda: self.controller.mostrar_tela("Imagem")
        )
        self.btn_imagem.grid(row=0, column=0, padx=20, pady=20)

        # Botao Video
        self.btn_video = ctk.CTkButton(
            self.btn_frame,
            text="Módulo Vídeo\n(CDU-04)",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            height=80,
            width=200,
            corner_radius=12,
            fg_color="#2c82c9",
            hover_color="#22659c",
            command=lambda: self.controller.mostrar_tela("Video")
        )
        self.btn_video.grid(row=0, column=1, padx=20, pady=20)

        # Botao Avaliacao
        self.btn_avaliacao = ctk.CTkButton(
            self.btn_frame,
            text="Módulo Avaliação\n(CDU-05)",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            height=80,
            width=200,
            corner_radius=12,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=lambda: self.controller.mostrar_tela("Avaliacao")
        )
        self.btn_avaliacao.grid(row=0, column=2, padx=20, pady=20)

        # Footer
        self.footer = ctk.CTkLabel(
            self,
            text="Disciplina: Processamento Digital de Imagens | Prof. OpenCV",
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color="gray"
        )
        self.footer.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="s")
