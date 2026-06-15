from pathlib import Path
import sqlite3
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "cve.db"


def obter_conexao():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    with obter_conexao() as conn:
        cursor = conn.cursor()

        # Tabela de imagens
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS imagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                caminho TEXT NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Tabela de pipelines de filtros
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pipelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                config TEXT NOT NULL
            )
            """
        )

        # Tabela de coordenadas das vagas por imagem
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vagas_imagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imagem_id INTEGER NOT NULL,
                coordenadas TEXT NOT NULL,
                FOREIGN KEY (imagem_id) REFERENCES imagens(id) ON DELETE CASCADE
            )
            """
        )

        # Tabela de gabarito (Ground Truth) de vagas livres por imagem
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ground_truth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imagem_id INTEGER NOT NULL,
                vagas_livres TEXT NOT NULL,
                FOREIGN KEY (imagem_id) REFERENCES imagens(id) ON DELETE CASCADE
            )
            """
        )

        # Adicionar alguns pipelines padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM pipelines")
        if cursor.fetchone()[0] == 0:
            config_padrao = {
                "gaussian_kernel": [3, 3],
                "adaptive_block_size": 25,
                "adaptive_c": 16,
                "median_kernel": 5,
                "morph_kernel": [3, 3],
                "morph_iterations": 1,
                "limiar_vaga_livre": 900,
            }
            cursor.execute(
                "INSERT INTO pipelines (nome, config) VALUES (?, ?)",
                ("Configuracao Padrao", json.dumps(config_padrao)),
            )

            config_suave = {
                "gaussian_kernel": [5, 5],
                "adaptive_block_size": 31,
                "adaptive_c": 12,
                "median_kernel": 7,
                "morph_kernel": [3, 3],
                "morph_iterations": 2,
                "limiar_vaga_livre": 1000,
            }
            cursor.execute(
                "INSERT INTO pipelines (nome, config) VALUES (?, ?)",
                ("Suavizacao Intensa", json.dumps(config_suave)),
            )

        conn.commit()


# Operações com Imagens
def cadastrar_imagem(nome: str, caminho: str) -> int:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO imagens (nome, caminho) VALUES (?, ?)",
            (nome, caminho),
        )
        conn.commit()
        return cursor.lastrowid


def listar_imagens():
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM imagens ORDER BY data_cadastro DESC")
        return [dict(row) for row in cursor.fetchall()]


def obter_imagem(imagem_id: int):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM imagens WHERE id = ?", (imagem_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def remover_imagem(imagem_id: int):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM imagens WHERE id = ?", (imagem_id,))
        conn.commit()


# Operações com Pipelines
def salvar_pipeline(nome: str, config: dict):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        config_str = json.dumps(config)
        cursor.execute(
            """
            INSERT INTO pipelines (nome, config)
            VALUES (?, ?)
            ON CONFLICT(nome) DO UPDATE SET config = excluded.config
            """,
            (nome, config_str),
        )
        conn.commit()


def obter_pipeline(nome: str) -> dict | None:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT config FROM pipelines WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        return json.loads(row["config"]) if row else None


def listar_pipelines():
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM pipelines")
        return [row["nome"] for row in cursor.fetchall()]


# Operações com Vagas
def salvar_vagas_imagem(imagem_id: int, coordenadas: list):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        coordenadas_str = json.dumps(coordenadas)
        cursor.execute(
            """
            INSERT INTO vagas_imagens (imagem_id, coordenadas)
            VALUES (?, ?)
            """,
            (imagem_id, coordenadas_str),
        )
        conn.commit()


def atualizar_vagas_imagem(imagem_id: int, coordenadas: list):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        coordenadas_str = json.dumps(coordenadas)
        # Verifica se já existe coordenadas salvas
        cursor.execute("SELECT id FROM vagas_imagens WHERE imagem_id = ?", (imagem_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE vagas_imagens SET coordenadas = ? WHERE imagem_id = ?",
                (coordenadas_str, imagem_id),
            )
        else:
            cursor.execute(
                "INSERT INTO vagas_imagens (imagem_id, coordenadas) VALUES (?, ?)",
                (imagem_id, coordenadas_str),
            )
        conn.commit()


def obter_vagas_imagem(imagem_id: int) -> list:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT coordenadas FROM vagas_imagens WHERE imagem_id = ?",
            (imagem_id,),
        )
        row = cursor.fetchone()
        return json.loads(row["coordenadas"]) if row else []


# Operações com Ground Truth (Gabarito para Benchmark/Avaliação)
def salvar_ground_truth(imagem_id: int, vagas_livres: list):
    with obter_conexao() as conn:
        cursor = conn.cursor()
        vagas_livres_str = json.dumps(vagas_livres)
        # Verifica se já existe
        cursor.execute("SELECT id FROM ground_truth WHERE imagem_id = ?", (imagem_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE ground_truth SET vagas_livres = ? WHERE imagem_id = ?",
                (vagas_livres_str, imagem_id),
            )
        else:
            cursor.execute(
                "INSERT INTO ground_truth (imagem_id, vagas_livres) VALUES (?, ?)",
                (imagem_id, vagas_livres_str),
            )
        conn.commit()


def obter_ground_truth(imagem_id: int) -> list:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vagas_livres FROM ground_truth WHERE imagem_id = ?",
            (imagem_id,),
        )
        row = cursor.fetchone()
        return json.loads(row["vagas_livres"]) if row else []


# Inicializa o banco de dados se for chamado diretamente
if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado em:", DB_PATH)
