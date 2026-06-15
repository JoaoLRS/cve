import shutil
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

import db

class ImagemTela(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout principal
        self.grid_rowconfigure(0, weight=0)  # Cabecalho
        self.grid_rowconfigure(1, weight=1)  # Grid de cards
        self.grid_rowconfigure(2, weight=0)  # Footer/Voltar
        self.grid_columnconfigure(0, weight=1)

        # 1. Cabecalho
        self.cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        self.cabecalho.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        self.cabecalho.grid_columnconfigure(0, weight=1)
        self.cabecalho.grid_columnconfigure(1, weight=0)

        self.titulo = ctk.CTkLabel(
            self.cabecalho,
            text="Imagem - Banco de Dados",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold")
        )
        self.titulo.grid(row=0, column=0, sticky="w")

        self.btn_importar = ctk.CTkButton(
            self.cabecalho,
            text="Importar Imagens",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            command=self.importar_imagens
        )
        self.btn_importar.grid(row=0, column=1, sticky="e")

        # 2. Grid de Cards com Scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 3. Footer com Botao Voltar
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        
        self.btn_voltar = ctk.CTkButton(
            self.footer,
            text="Voltar",
            fg_color="#a0a0a0",
            hover_color="#808080",
            text_color="black",
            command=lambda: self.controller.mostrar_tela("Menu")
        )
        self.btn_voltar.pack(side="left")

        # Estado das imagens carregadas
        self.cards_referencias = []

    def carregar_cards_imagens(self):
        # Limpa o frame de scroll
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.cards_referencias.clear()

        # Lista imagens do banco de dados
        imagens = db.listar_imagens()

        if not imagens:
            self.lbl_vazio = ctk.CTkLabel(
                self.scroll_frame,
                text="Nenhuma imagem cadastrada no banco de dados.\nClique no botao 'Importar Imagens' acima para adicionar.",
                font=ctk.CTkFont(family="Helvetica", size=14, slant="italic"),
                text_color="gray"
            )
            self.lbl_vazio.grid(row=0, column=0, columnspan=4, padx=20, pady=80, sticky="nsew")
            return

        # Renderiza os cards
        colunas = 4
        for idx, img_dados in enumerate(imagens):
            row = idx // colunas
            col = idx % colunas

            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, border_width=1, border_color="#3a3a3a")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            # Miniatura
            caminho_img = Path(img_dados["caminho"])
            try:
                # Verifica se o arquivo existe
                if not caminho_img.exists():
                    # Tenta caminho relativo ou padrão
                    caminho_img = db.BASE_DIR / caminho_img.relative_to(db.BASE_DIR)
                
                pil_img = Image.open(caminho_img)
                pil_img.thumbnail((160, 110))
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, 110))
            except Exception as e:
                # Imagem de fallback caso haja erro ao carregar
                pil_img = Image.new("RGB", (160, 110), color="#2c3e50")
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, 110))

            lbl_mini = ctk.CTkLabel(card, image=ctk_img, text="")
            lbl_mini.grid(row=0, column=0, padx=10, pady=10)
            self.cards_referencias.append(ctk_img) # Previne Garbage Collection da imagem

            # Nome
            lbl_nome = ctk.CTkLabel(
                card, 
                text=img_dados["nome"], 
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                wraplength=160
            )
            lbl_nome.grid(row=1, column=0, padx=10, pady=2, sticky="ew")

            # Data de Cadastro
            data_cad = img_dados["data_cadastro"].split()[0] if img_dados["data_cadastro"] else ""
            lbl_data = ctk.CTkLabel(
                card, 
                text=f"Cadastrado: {data_cad}", 
                font=ctk.CTkFont(family="Helvetica", size=10),
                text_color="gray"
            )
            lbl_data.grid(row=2, column=0, padx=10, pady=2, sticky="ew")

            # Botoes de Acao no Card
            btn_abrir = ctk.CTkButton(
                card,
                text="Processar",
                height=26,
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                command=lambda img_id=img_dados["id"]: self.abrir_processamento(img_id)
            )
            btn_abrir.grid(row=3, column=0, padx=10, pady=(8, 4), sticky="ew")

            btn_excluir = ctk.CTkButton(
                card,
                text="Excluir",
                height=24,
                fg_color="#c0392b",
                hover_color="#962d22",
                font=ctk.CTkFont(family="Helvetica", size=11),
                command=lambda img_id=img_dados["id"]: self.confirmar_exclusao(img_id)
            )
            btn_excluir.grid(row=4, column=0, padx=10, pady=(2, 10), sticky="ew")

    def abrir_processamento(self, imagem_id):
        self.controller.mostrar_tela("Processamento", imagem_id=imagem_id)

    def confirmar_exclusao(self, imagem_id):
        if messagebox.askyesno("Excluir Imagem", "Tem certeza que deseja excluir esta imagem e seus dados de vagas permanentemente?"):
            db.remover_imagem(imagem_id)
            self.carregar_cards_imagens()

    def importar_imagens(self):
        # Pergunta se o usuario quer importar arquivo unico ou pasta
        dialogo = ctk.CTkOptionMenu(
            self,
            values=["Importar Arquivo", "Importar Pasta (Lote)"],
            command=self.executar_importacao
        )
        dialogo.pack(padx=20, pady=20)
        dialogo.destroy() # Apenas exibe o popup
        
        # Como o CustomTkinter nao tem uma caixa de dialogo nativa de multipla escolha simples,
        # usaremos o messagebox clássico
        resposta = messagebox.askyesnocancel(
            "Tipo de Importacao",
            "Deseja importar uma PASTA completa de imagens (Lote de teste)?\n"
            "Clique 'Sim' para pasta, 'Nao' para arquivo individual, ou 'Cancelar'."
        )

        dest_dir = db.DATA_DIR / "importadas"
        dest_dir.mkdir(parents=True, exist_ok=True)

        if resposta is True:  # Pasta
            pasta_selecionada = filedialog.askdirectory(title="Selecionar Pasta com Imagens")
            if not pasta_selecionada:
                return

            caminhos_imagens = list(Path(pasta_selecionada).glob("*.png")) + list(Path(pasta_selecionada).glob("*.jpg"))
            if not caminhos_imagens:
                messagebox.showwarning("Nenhuma Imagem", "Nenhuma imagem (.png ou .jpg) encontrada na pasta selecionada.")
                return

            importados_count = 0
            for caminho_img in caminhos_imagens:
                caminho_destino = dest_dir / caminho_img.name
                shutil.copy2(caminho_img, caminho_destino)
                # Cadastra no banco
                db.cadastrar_imagem(caminho_img.name, str(caminho_destino))
                importados_count += 1

            messagebox.showinfo("Sucesso", f"{importados_count} imagens importadas com sucesso da pasta!")
            self.carregar_cards_imagens()

        elif resposta is False:  # Arquivo Unico
            arquivo_selecionado = filedialog.askopenfilename(
                title="Selecionar Imagem",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
            )
            if not arquivo_selecionado:
                return

            caminho_img = Path(arquivo_selecionado)
            caminho_destino = dest_dir / caminho_img.name
            shutil.copy2(caminho_img, caminho_destino)
            db.cadastrar_imagem(caminho_img.name, str(caminho_destino))

            messagebox.showinfo("Sucesso", "Imagem importada com sucesso!")
            self.carregar_cards_imagens()
