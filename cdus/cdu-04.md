# CDU-04: Tela de Vídeo

1. Após o usuário ter clicado no botão `Vídeo` no menu inicial de acordo com o [CDU-01](cdu-01.md), a tela de vídeo será exibida contendo os seguintes componentes:

    1.1 - Título: `Vídeo: [nome_do_arquivoVideo]`.

    1.2 - Barra de Controle do Vídeo:
        * Botão `Play / Pause` para iniciar ou interromper a execução do vídeo.
        * Barra de progresso deslizante (Timeline) que indica o frame atual e permite pular para qualquer ponto do vídeo.
        * Seletor de `Velocidade de Reprodução` (0.5x, 1.0x, 1.5x, 2.0x).

    1.3 - Configuração de Processamento:
        * Dropdown para selecionar o `Pipeline de Processamento` (as mesmas configurações e pipelines pré-definidos salvos no [CDU-03](cdu-03.md) podem ser aplicados ao vídeo).
        * Indicador textual resumido do pipeline ativo.

    1.4 - Área de Exibição Central (com botões de abas para alternar visualizações):
        * Aba `Resultado Final`: Exibe o vídeo em tempo real com as vagas delimitadas por retângulos coloridos (Verde para livre, Vermelho para ocupado) e um contador no canto superior indicando `Livres: X / Total`.
        * Aba `Filtro Aplicado`: Exibe o vídeo processado em tempo real na etapa final do pipeline (imagem binária resultante), útil para depurar ruídos e entender a binarização.

2. Se o usuário alterar as configurações de pipeline com o vídeo pausado ou em reprodução, o vídeo passará a processar os frames subsequentes aplicando a nova combinação de filtros instantaneamente.

3. No final da tela, haverá um botão `Voltar` que redirecionará o usuário de volta para o menu inicial ([CDU-01](cdu-01.md)).