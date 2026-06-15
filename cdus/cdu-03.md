# CDU-03: Tela de Processamento de Imagem

1. A tela `Processamento de Imagem` conterá os seguintes componentes:

    1.1 - Título: `Processamento da imagem: [nome_do_arquivoImg]`.

    1.2 - Barra de Ações Rápidas:
        * Dropdown de `Pipelines Pré-definidos` para alternar rapidamente entre diferentes combinações de filtros (ex: "Configuração Padrão", "Suavização Intensa", "Sem Morfologia", etc.).
        * Botão `Salvar Pipeline Atual` para armazenar a combinação de filtros e seus parâmetros configurados pelo usuário.

    1.3 - Painel de Filtros e Configurações: Abaixo do título, haverá um painel expansível contendo a lista de filtros disponíveis no pipeline clássico (Escala de Cinza, Gaussian Blur, Median Blur, Adaptive Threshold, Operações Morfológicas de Dilatação/Erosão). Ao lado de cada filtro, haverá inputs numéricos e sliders para ajustar seus parâmetros (ex: tamanho do kernel, constante C, etc.), contendo placeholders explicativos com exemplos de valores típicos.

<<<<<<< HEAD
    1.4 - Seção "Pipeline Utilizado": Um indicador visual linear mostrando a sequência exata de filtros que estão ativos (ex: `Original ➔ Cinza ➔ Gaussian Blur ➔ Adaptive Threshold ➔ Median Blur ➔ Dilatação ➔ Classificação`), deixando explícito o fluxo aplicado.

    1.5 - Botão: `Iniciar Processamento`.

2. Ao clicar no botão `Iniciar Processamento`, será executada a cadeia de filtros sobre a imagem. Para cada filtro ativo, será exibido um `card` contendo a imagem resultante daquela etapa específica e o respectivo nome do filtro.
    * **Fluxo Visual dos Cards:** Do lado de cada card será desenhada uma seta indicativa (➔) apontando a direção do fluxo. Se o card alcançar a margem direita da tela, o fluxo continuará na linha de baixo (indicando uma seta para baixo e, em seguida, apontando para o sentido contrário, criando um zigue-zague ou simplesmente quebrando a linha mantendo a coesão de leitura).
    * **Card de Resultado Final:** O último card exibirá a imagem final do estacionamento com a marcação das vagas (Verde para livre, Vermelho para ocupado) e as seguintes métricas da imagem ativa (caso possua anotação/gabarito de teste):
        * Total de Vagas: X
        * Vagas Livres Detectadas: Y
        * Vagas Livres Esperadas (Ground Truth): Z
        * Taxa de Acerto Local: W%

3. No final da tela, haverá um botão `Voltar` que redirecionará o usuário de volta para a tela de Imagem ([CDU-02](cdu-02.md)).
=======
2. Ao clicar no botão `Iniciar processamento`, dara inicio ao processamento dos `filtros`. Para cada `filtro` sera mostrado um `card` a onde nele tera a `imagem` resultante da aplicação do `filtro` da imagem, nesse `card` tambem ira conter o `nome` do `filtro`. Do lado de cada card deve ser mostrado uma seta para direitar informando que teve uma mudança de estado, se o card tiver chegado no limite da margem do layout a direita deve ser mostrado uma seta para baixo, por conta disso a seta que mostra a mudança de estado passa a ser para esquerda. O utimo `card` deve ser ao processo final a onde mostra a `imagem` do estacionamento já com as contabilização das vagas.

3. No final do sistema deve conter um botão `Voltar`, ele sera responsavel por voltar para o [CDU-02](cdu-02.md).
>>>>>>> 6a36dd167d38919bba20493daa7197dab96edc64
