# CVE - Contabilização de Vagas de Estacionamento

Este é um sistema de visão computacional voltado para a monitoração e contagem de vagas em estacionamentos por meio de técnicas clássicas de **Processamento Digital de Imagens (PDI)** utilizando a biblioteca **OpenCV**. 

O projeto foi remodelado de scripts de terminal básicos para uma aplicação desktop consolidada com **Interface Gráfica (GUI) moderna** e **Banco de Dados SQLite** integrado, atendendo aos requisitos e feedbacks acadêmicos.

---

## 🚀 Módulos do Sistema

O sistema está dividido em três módulos principais acessíveis a partir da tela inicial:

1.  **Módulo Imagem (CDU-02 e CDU-03)**:
    *   **Importação**: Permite carregar imagens avulsas ou pastas de lote de testes para o banco de dados.
    *   **Calibração de Filtros**: Sliders interativos para calibrar parâmetros do pipeline (Gaussian Blur, Adaptive Threshold, Median Blur, Dilatação).
    *   **Visualização de Etapas**: Cards mostrando os resultados intermediários de cada etapa do pipeline clássico de PDI.
    *   **Marcação e Gabaritos**: Ferramenta integrada com clique de mouse em OpenCV para demarcar retângulos de vagas (ROIs) e definir o Ground Truth (gabarito) de quais vagas estão fisicamente livres.
2.  **Módulo Vídeo (CDU-04)**:
    *   **Player Integrado**: Reproduz o vídeo `carPark.mp4` em tempo real aplicando o pipeline de processamento selecionado.
    *   **Controles**: Play, Pause, Timeline deslizante e seleção de velocidade de reprodução (0.5x a 2.0x).
    *   **Visualizações**: Alternância rápida entre a imagem original demarcada e o vídeo binário (filtrado).
3.  **Módulo Avaliação e Benchmark (CDU-05)**:
    *   **Avaliação em Lote**: Executa o pipeline selecionado contra um lote de pelo menos 30 imagens de teste com gabarito no banco.
    *   **Métricas Acadêmicas**: Calcula a **Acurácia**, **Recall de Vagas Vazias (Taxa de acerto)**, **Precisão** e **F1-Score**.
    *   **Matriz de Confusão**: Renderiza um gráfico estatístico em tempo real (Heatmap 2x2) com Matplotlib.
    *   **Comparador**: Tabela comparativa confrontando o desempenho de todos os pipelines configurados no banco de dados.
    *   **Exportação**: Gera um relatório acadêmico detalhado em Markdown (`resultados/relatorio_avaliacao.md`) para entrega.

---

## 🛠️ O que foi Desenvolvido até agora

*   **Banco de Dados (`src/db.py`)**: Inicializador SQLite (`cve.db`) persistindo configurações de pipelines de filtros, imagens cadastradas, suas vagas demarcadas e ground truths.
*   **Processador Dinâmico (`src/detector.py`)**: Core unificado que aplica dinamicamente o pipeline baseado nos parâmetros em JSON extraídos do banco de dados.
*   **Interface Gráfica (`src/app.py` e `src/telas/*`)**: Estrutura modular em `customtkinter` com visual premium (Tema Dark).
*   **Massa de Testes Realística (`scratch/populador.py`)**: Script que extrai 30 frames diferentes do vídeo original e aplica modificações climáticas clássicas via OpenCV (Sol, Nublado, Pôr do Sol, Chuva e Noturno), gerando 30 imagens exclusivas com a mesma perspectiva física para testar o benchmark de avaliação.

---

## 📋 Pré-requisitos e Dependências

Para executar o sistema, você precisará ter o **Python 3.12+** instalado no seu computador. As bibliotecas necessárias são:

*   `customtkinter` (Interface Gráfica Moderna)
*   `opencv-python` (OpenCV - Processamento de Imagem e Vídeo)
*   `numpy` (Cálculos de matrizes da imagem)
*   `matplotlib` (Gráficos e Matriz de Confusão)
*   `Pillow` (Tratamento de imagens para exibição na GUI)
*   `packaging` (Dependência auxiliar)

---

## 💻 Como Rodar a Aplicação

### Passo 1: Instalar Dependências
Abra um terminal (PowerShell ou Prompt de Comando) na raiz do projeto e instale as bibliotecas listadas no `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Passo 2: Inicializar/Popular o Banco de Dados com Testes
Antes da primeira execução, rode o populador para extrair os frames climáticos de teste do vídeo e cadastrar as vagas e gabaritos no SQLite:
```powershell
python C:\Users\prome\.gemini\antigravity\brain\1516b7cd-351b-419a-8358-7aad047e2f14\scratch\populador.py
```
*(Nota: Esse comando criará o lote de 30 imagens em `data/importadas/` e inicializará o banco `data/cve.db` com o Ground Truth).*

### Passo 3: Executar a Aplicação
Inicie a aplicação gráfica em desenvolvimento:
```powershell
python src/app.py
```

---

## 📦 Como Gerar o Executável (`cve.exe`)

Se quiser gerar o arquivo executável consolidado para entrega, você pode empacotar a aplicação usando o **PyInstaller**:

1.  Instale o PyInstaller:
    ```powershell
    pip install pyinstaller
    ```
2.  Gere o executável no modo standalone (ocultando console preto de fundo):
    ```powershell
    pyinstaller --noconsole --onefile --name cve src/app.py
    ```
3.  O executável final `cve.exe` será gerado dentro da pasta **`dist/`** na raiz do projeto.
