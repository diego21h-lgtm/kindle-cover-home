# Plano técnico — etapa 2

## Portões de compatibilidade antes da GUI

1. Executar o roteiro da etapa 1 no B023/4.1.4 e registrar versão real, arquitetura,
   framebuffer (resolução, bpp, stride e API de atualização), utilitários e dispositivos.
   Não inferir ABI/libc apenas de `uname`. Conferir ELF/toolchain em ambiente de build
   e compatibilidade com libc/kernel antigos antes de levar qualquer binário ao Kindle.
2. Preparar ensaio **separado e explicitamente iniciado** de renderização: binário
   mínimo para backend legado, limites verificados, branco/preto e retângulo pequeno.
   Validar refresh completo/parcial, ghosting e recuperação. Não basta escrever pixels:
   painel E Ink exige atualização compatível. Não começar por ioctls de Paperwhite.
3. Comparar FBInk compilado para o alvo e backend einkfb mínimo; preferir backend
   mantido se houver build compatível e obrigações de licença atendidas. Não distribuir
   FBInk moderno ou bibliotecas dinâmicas até executar no FW 4.1.4. `eips` só serve
   para ensaio se seus recursos efetivos forem confirmados, não como renderizador
   de capas presumido. Nenhuma instalação em `/usr` ou no firmware.
4. Fazer capturador evdev dedicado, de duração limitada, em sessão de teste futura.
   Identificar nós por capacidades e nomes de `/proc/bus/input/devices`; medir press,
   release e repetição para cada botão. Confirmar tamanhos de `struct input_event` da
   ABI ARM; não decodificar com layout do computador. Não usar `EVIOCGRAB` inicialmente.
5. Resolver convivência com a Home: sem exclusão de entrada, o framework pode reagir
   às mesmas teclas e repintar a tela. Testar foco e ciclo de vida controlado; se não
   houver caminho seguro sem modificar firmware/serviço permanente, **não liberar
   GUI**. Não adotar `stop framework` como pré-requisito. Ensaiar saída voluntária,
   erro, suspensão/retomada e retorno ao KUAL/Home antes de renderizar a biblioteca.

## Layout e dados após aprovação dos portões

Canvas 600 × 800 em retrato; margens 12 px; cabeçalho 44 px; rodapé 28 px;
conteúdo y=56..760 (704 px). Duas colunas de 282 px, separadas por 12 px.
Três linhas de 226 px com intervalos de 12 px, deixando 2 px de folga inferior.
Dentro de cada célula: caixa de capa proporcional, título em até duas linhas e
borda forte para seleção. Esses números são proposta, não imagem já validada.
Testar legibilidade real, contraste e ghosting sem depender de cor ou touchscreen.

Primeiro renderizar placeholders numerados a partir de `demo.tsv`, sem abrir livros.
Direcionais movem seleção; centro confirma; paginação troca seis entradas; Back sai.
Definir limites em página incompleta e repetição; Home deve continuar oferecendo
retorno seguro. Confirmar os códigos no aparelho antes de fixar mapeamentos.

Depois, gerar capas no computador ou com extrator compatível, fora de `documents`:
cache dedicado na área de dados, escala com preservação de proporção e tons de cinza,
limites de tamanho/memória, placeholder para erro. Não contornar DRM. Metadados reais
podem ser extraídos de documentos sem proteção com parser delimitado e testado;
separar título inferido de título confirmado, e associação de capa de mero candidato.
Ordenação e paginação precisam ser determinísticas nesta próxima etapa.

## Abertura de livros: portão independente

Não confundir renderizar capa com abrir o leitor Amazon. Investigar interfaces 4.x
com documentação e inventário somente leitura, depois testar um documento de teste
criado para isso, nunca um livro pessoal como primeira experiência. Validar paths
com espaços/Unicode, URI se aplicável, retorno, estado de leitura e ausência de
alterações indesejadas. Não montar comandos shell concatenando caminhos do catálogo.
Se a interface nativa não for comprovada, manter confirmação indisponível e acesso
normal pela Home; não apresentar abertura como funcional. Medir memória/latência
com seis capas e livro grande. Encerrar todos os descritores/processos ao sair,
sem daemon, alteração de init ou substituição da Home.
