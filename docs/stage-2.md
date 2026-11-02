# Etapa 2: escolha técnica, evidências e limites

## Revisão da Etapa 1

`bin/start.sh`, `common.sh`, `catalog-entry.sh`, `diagnose.sh` e `demo.tsv` permanecem
byte a byte como na 0.1.0. O menu passa pelo wrapper `launch.sh`, que registra modo,
início, diagnóstico e conclusão em `/mnt/us/coverhome/logs/session.log`. Os caminhos
e formatos antigos continuam disponíveis. O diagnóstico standalone original ainda
escreve stdout; o comando KUAL novo garante o log no destino solicitado.

Revisão: scripts POSIX `sh`, sem bash arrays, Python/Node no alvo, scripts chamados
via `sh`, dados USB com caminhos entre aspas, TSV escapado, `find -exec` sem `eval`,
sem alterações de firmware, serviços ou partições. Sintaxe e execução foram testadas
com `/bin/sh` do computador, **não com o BusyBox do Kindle**. A opção `cd --` e as
variantes dos utilitários ainda precisam passar pelo teste real. Sem isso, a
integração KUAL não está validada.

## Evidência para renderização

A [pesquisa da Etapa 1](compatibility.md) identifica 0x23 como K4b/legado no FBInk e
backend `framebuffer_einkfb` no KOReader. Framebuffer direto exigiria ABI/ioctls e
política de refresh corretas; escrita isolada pode disputar tela com o framework.
Não foi escolhido sem esse ensaio. FBInk é alternativa promissora, mas não há binário
incluído: compatibilidade de compilação/ABI no 4.1.4 não foi provada. KDK/Kindlet
poderia fornecer foco/ciclo de vida mais adequado, mas exigiria SDK e validação de
assinatura/permissões. Não se pressupõe runtime HTML.

O [README do FBInk](https://github.com/NiLuJe/FBInk/blob/master/README.md) menciona
`eips` como ferramenta nativa Kindle; sua [documentação CLI](https://github.com/NiLuJe/FBInk/blob/master/CLI.md)
refere atualização de imagem pelo eips. Isso sustenta investigar `eips`, mas **não
prova o suporte `-g PNG` deste firmware**. O módulo escolhe esse mecanismo como
candidato mínimo, só após verificação local do executável `/usr/sbin/eips`, ajuda
e observação real. Não há evidência obtida do aparelho nesta entrega.

O executável real recebe uma imagem PNG grayscale pré-gerada. Não é uma simulação
HTML; o caminho está implementado em shell e não depende de bibliotecas modernas
no Kindle. Até confirmação real, descrevemos como **ensaio gráfico executável,
compatibilidade pendente**, não como biblioteca operacional. Não tentamos obter
controle da tela, limpar framebuffer, pausar framework, chamar IPC ou travar input.
KUAL/Amazon podem repintar imediatamente: se isso impedir uso, a abordagem falha
para GUI interativa e o próximo trabalho deve resolver foco/ciclo de vida por uma
API comprovada antes de adicionar funcionalidades.

## Separação dos módulos

- `tools/library_model.py`: entrada do catálogo legado; dados nunca viram código.
- `tools/covers.py`: sidecars e EPUB sem DRM no PC; conversão para grayscale.
- `tools/render_library.py`: páginas PNG 600 × 800, grade 2 × 3, placeholder, título,
  seleção e vazio. Sem rede. Fonte DejaVu com licença em `tools/fonts`.
- `bin/navigation.awk`: redutor de estado testável; não conhece hardware.
- `bin/library.sh`: sessão KUAL curta, bloqueio e seleção de PNG por índices limitados.
- `bin/render.sh`: única invocação gráfica; saída desativada até marcador explícito.

A biblioteca pessoal é um snapshot preparado no PC do catálogo read-only. Mudar
livros/capas exige nova preparação; não há atualização dinâmica das imagens no
Kindle. Caminhos da capa são remapeados apenas dentro da unidade indicada; EPUB
usa membros ZIP em memória com limite de 4 MiB por item e limite de pixels na
imagem. Não se extrai ZIP para `documents`. MOBI/AZW usam somente sidecars. Não
há parser EXTH nem tentativa de ler documentos protegidos.

## Botões e abertura

Os códigos candidatos do mapa K4 estão documentados em `compatibility.md`. Não foi
possível demonstrar captura segura e foco exclusivo sem aparelho. Portanto não há
leitura de `/dev/input/event*`, `EVIOCGRAB` ou processo em background. Direções,
páginas, seleção e saída são ações **do menu KUAL**; o redutor fica disponível para
um futuro adaptador. Paginação lateral direta e direcional sobre a imagem permanecem
pendentes. Um comando de seleção registra índice e não abre nada; nenhum comando
interno não validado é emitido para o leitor original.

O plano original anterior à implementação foi preservado em
[stage-2-original-plan.md](stage-2-original-plan.md). A próxima decisão depende dos
resultados do [roteiro real](device-validation-0.2.md), não de expandir a GUI na nuvem.
