# CDU-02: Tela de imagem

1. Após o usuário ter clicado no botão `Imagem` de acordo com o [CDU-01](cdu-01.md), a margem do layout da aplicação irá expandir para que seja possível a visualização da tela de `Imagem`. Com isso, conterá os seguintes componentes:

    1.1 - Título: `Imagem`.

    1.2 - Botão: `Importar` **(o botão `Importar` sempre será visível, mesmo já tendo imagens cadastradas, e deve permitir a importação de uma única imagem ou de uma pasta/lote contendo múltiplas imagens de uma vez)**.

2. Se existirem dados cadastrados no banco de dados, devem ser mostrados para o usuário **1 ou n** `cards` contendo as miniaturas das imagens que já foram importadas e seus respectivos nomes de arquivo.

3. Ao clicar em algum `card` de imagem, o usuário será redirecionado para a tela de processamento de imagem correspondente, descrita no [CDU-03](cdu-03.md).

4. No final do layout da tela, haverá um botão `Voltar`, que será responsável por redirecionar o usuário para a tela inicial descrita no [CDU-01](cdu-01.md).