# CDU-05: Tela de Avaliação e Benchmark (Métricas)

1. Após o usuário ter clicado no botão `Avaliação/Benchmark` no menu inicial de acordo com o [CDU-01](cdu-01.md), a tela de Avaliação será exibida contendo os seguintes componentes:

    1.1 - Título: `Avaliação de Desempenho e Métricas (Benchmark)`.

    1.2 - Painel de Entrada de Dados:
        * Seletor de `Diretório do Lote de Teste` para importar a pasta que contém as imagens de teste (mínimo de 30 imagens).
        * Seletor de `Arquivo de Ground Truth` contendo o gabarito de anotações reais do estado de cada vaga (livre/ocupada) para as imagens de teste.

    1.3 - Painel de Configuração da Avaliação:
        * Dropdown de `Pipeline Ativo` para selecionar o pipeline a ser testado.
        * Lista de seleção múltipla `Comparar Pipelines` para marcar outras configurações de pipelines salvas e gerar tabelas comparativas.
        * Botão `Executar Avaliação em Lote`.

    1.4 - Painel de Métricas Resultantes (exibido após a conclusão do processamento das imagens):
        * **Métricas Globais:**
            * Taxa de Acerto Geral (Acurácia).
            * **Taxa de Acerto de Vagas Vazias (Recall/Sensibilidade)**: porcentagem de vagas vazias reais que foram detectadas corretamente como vazias.
            * Precisão: porcentagem das detecções de vagas vazias que estavam realmente vazias.
            * F1-Score.
        * **Matriz de Confusão Interativa:** Gráfico de calor de 2x2 mostrando:
            * Verdadeiros Positivos (vagas vazias classificadas como vazias).
            * Falsos Positivos (vagas ocupadas classificadas como vazias).
            * Falsos Negativos (vagas vazias classificadas como ocupadas).
            * Verdadeiros Negativos (vagas ocupadas classificadas como ocupadas).
        * **Tabela Comparativa de Combinações de Pipelines:** Exibe uma tabela comparando os resultados estatísticos de diferentes pipelines testados sobre o mesmo lote de imagens.
        * **Galeria de Evidências:** Grade de cards exibindo cada uma das 30+ imagens com um indicador de taxa de acerto individual (ex: 95% de acerto). Ao clicar em uma imagem da grade, abre-se uma tela detalhada indicando em que vagas houve erro de classificação (falso positivo ou falso negativo).

    1.5 - Ações de Exportação:
        * Botão `Exportar Relatório Acadêmico` para gerar um arquivo PDF ou Markdown formatado com todas as tabelas de comparação, matriz de confusão e gráficos para ser entregue ao professor.

2. Se o usuário clicar em `Executar Avaliação em Lote`, o sistema processará de forma otimizada as 30+ imagens em segundo plano e, após a finalização, preencherá o Painel de Métricas Resultantes.

3. No final da tela, haverá um botão `Voltar` que redirecionará o usuário de volta para o menu inicial ([CDU-01](cdu-01.md)).
