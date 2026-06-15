import customtkinter as ctk
import db

# Importar as telas
from telas.menu import MenuTela
from telas.imagem import ImagemTela
from telas.processamento import ProcessamentoTela
from telas.video import VideoTela
from telas.avaliacao import AvaliacaoTela

class CVEApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar Titulo e Dimensoes da Janela
        self.title("CVE - Contabilização de vagas de estacionamento")
        self.geometry("1200x750")
        self.minsize(1100, 700)

        # Centraliza a janela na tela do usuario
        self.centralizar_janela()

        # Configurar Estetica Visual (Tema Escuro e Azul Moderno)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Inicializa o banco de dados SQLite
        db.inicializar_banco()

        # Container principal onde as telas serao montadas
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dicionario para armazenar as instancias das telas
        self.telas = {}

        # Instanciar as telas no container
        for TelaClasse in (MenuTela, ImagemTela, ProcessamentoTela, VideoTela, AvaliacaoTela):
            nome_tela = TelaClasse.__name__.replace("Tela", "")
            # Cria a tela
            tela = TelaClasse(parent=self.container, controller=self)
            self.telas[nome_tela] = tela
            # Posiciona no mesmo espaco (grid stack)
            tela.grid(row=0, column=0, sticky="nsew")

        # Inicia mostrando o Menu Principal
        self.mostrar_tela("Menu")

    def mostrar_tela(self, nome_tela, **kwargs):
        tela = self.telas.get(nome_tela)
        if tela:
            # Acoes especificas ao carregar cada tela
            if nome_tela == "Imagem":
                tela.carregar_cards_imagens()
            elif nome_tela == "Processamento":
                imagem_id = kwargs.get("imagem_id")
                if imagem_id is not None:
                    tela.carregar_dados_imagem(imagem_id)
            elif nome_tela == "Video":
                tela.carregar_dados_video()
            elif nome_tela == "Avaliacao":
                tela.carregar_dados_avaliacao()

            # Traz a tela para o topo
            tela.tkraise()

    def centralizar_janela(self):
        self.update_idletasks()
        largura = 1200
        altura = 750
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")


if __name__ == "__main__":
    app = CVEApp()
    app.mainloop()
