# Kindle Cover Home — Etapa 1 (0.1.0)

Extensão experimental de **diagnóstico e catalogação**, destinada ao Kindle Basic
2012 B023, firmware 4.1.4, jailbreak e KUAL-KDK já instalados. Não desenha na tela,
não substitui a Home e não abre livros. **Não foi testada em hardware Kindle.**
Os testes de desktop não certificam BusyBox, KUAL ou firmware 4.1.4.

## Instalar no Windows por USB

1. Baixe `dist/kindle-cover-home-0.1.0.zip` da cópia do projeto (ou gere com
   `python tools/package.py` no computador). Extraia o ZIP no computador.
2. Conecte o Kindle por USB; identifique a unidade que contém `documents`.
3. Copie a pasta `extensions/kindlecoverhome` extraída para
   `X:\extensions\kindlecoverhome`. Crie `extensions` se necessário. Não copie
   a pasta inteira do projeto para dentro de `documents`.
4. Se já existir `kindlecoverhome`, preserve sua cópia e remova a versão anterior
   antes de instalar. Não mescle versões. Não é necessário substituir o KUAL.
5. Ejete com segurança, desconecte o cabo e abra o KUAL. Selecione
   **Iniciar Kindle Cover Home**. O menu de demonstração gera seis entradas fictícias.
6. Reconecte ao Windows e consulte `X:\kindle-cover-home-data`:
   `diagnostics.txt`, `catalog.tsv` e, após demonstração, `demo.tsv`.
   Leia TSV como UTF-8, com tabulações. Nenhuma grade aparece nesta etapa.

Os arquivos shell devem permanecer com finais de linha **LF**, sem BOM. Não edite
com ferramentas que convertam para CRLF. Os comandos KUAL chamam `sh`, dispensando
bits executáveis no armazenamento FAT. A descoberta do menu e sua execução precisam
ser verificadas no KUAL-KDK-1.0.azw2 do aparelho.

## Catálogo e limites

Busca recursiva em `/mnt/us/documents`, sem seguir links simbólicos. Reconhece por
extensão (sem distinguir maiúsculas): MOBI, AZW, AZW3, PRC, PDF e TXT. Extensão não
comprova o formato nem a compatibilidade do leitor original. EPUB, KFX e o próprio
AZW2 do KUAL não entram no catálogo. Não lê conteúdo de livros, DRM ou bancos Amazon.

Colunas: `title`, `author`, `format`, `path`, `cover_candidate`, `metadata_source`.
Título = nome do arquivo sem extensão; autor = `Desconhecido`; origem = `filename`.
Esses são **metadados provisórios**, não extraídos de EXTH, PDF ou conteúdo. Uma
capa candidata é somente um arquivo irmão de mesmo nome base com `.jpg`, `.jpeg`
ou `.png` (minúsculas); nenhuma imagem é validada ou extraída. Capa vazia significa
não encontrada. Não procura thumbnails proprietários nem presume associação por ASIN.
TSV codifica barra invertida como `\\`, tab como `\t`, CR como `\r`, LF como `\n`.
Não use o catálogo como script; caminhos nunca são avaliados como comandos.
A ordem de descoberta não é garantida e não é uma ordenação de biblioteca.

A demonstração tem seis títulos e autores inventados, caminhos `demo://` não
abríveis, sem capas reais. Serve como entrada de dados para o futuro layout;
não cria livros em `documents` nem substitui o catálogo real.

## Diagnóstico e erros

O lançamento grava o diagnóstico e depois gera o catálogo solicitado. `diagnostics.txt`
registra kernel, versão de firmware quando disponível, memória, nomes de dispositivos
de entrada, framebuffer e presença de ferramentas. Não lê serial completo, credenciais,
eventos de teclas ou pixels. O catálogo revela nomes e caminhos pessoais; revise-o
antes de compartilhar. A mera presença de `eips`, `fbink` ou LIPC não comprova operação.

Somente shell POSIX e utilitários básicos são requeridos: `awk`, `tr`, `find` com
`-exec`, `cat`, `date`, `uname`, `ls`, `mkdir`, `mv`, `rm`, `rmdir`, `dirname`.
Não requer Python, Node, rede, apt, bash, jq ou bibliotecas gráficas no Kindle.
Python 3 é usado apenas no computador para testes e empacotamento.

Para executar por um shell já disponível no Kindle (não exige instalar SSH):

```sh
sh /mnt/us/extensions/kindlecoverhome/bin/start.sh
sh /mnt/us/extensions/kindlecoverhome/bin/start.sh demo
sh /mnt/us/extensions/kindlecoverhome/bin/diagnose.sh > /mnt/us/kch-diagnostics-manual.txt
```

Há bloqueio contra execuções simultâneas e publicação do catálogo via renomeação;
falha antes da publicação conserva o catálogo anterior. Diagnóstico e catálogo não
formam uma transação conjunta. Resultados anteriores são substituídos na próxima
execução bem-sucedida, sem histórico ilimitado. Se houver queda de energia, confirme
que nenhum comando está rodando antes de apagar **somente** a pasta vazia
`kindle-cover-home-data/.lock` (ou seus temporários após inspeção). Execute novamente.
Bibliotecas muito grandes podem demorar: o scanner inicia um processo por arquivo.
Não há serviço persistente ou captura de botões nesta versão.

## Remover / reverter

Feche o KUAL, conecte por USB e apague apenas
`X:\extensions\kindlecoverhome`. Ejete e reabra o KUAL. Opcionalmente faça backup
e apague `X:\kindle-cover-home-data`, que contém apenas saídas desta extensão.
Preserve `documents`, KUAL e quaisquer outras extensões. A remoção não exige
reiniciar, reflash, comandos de partição ou restauração do firmware.

Em Linux/macOS/WSL, também há scripts reversíveis:

```sh
sh tools/install.sh /caminho/absoluto/da/unidade
sh tools/uninstall.sh /caminho/absoluto/da/unidade
```

O instalador recusa sobrescrever uma instalação. O desinstalador exige o marcador
de propriedade, remove somente arquivos distribuídos e mantém os dados. Se houver
arquivos extras, a remoção da pasta falha e esses arquivos são preservados.

## Desenvolvimento e validação

```sh
python3 -m unittest discover -s tests -v
python3 tools/package.py
```

Estrutura: `extensions/` = payload KUAL; `tools/` = instalação, remoção e pacote;
`tests/` = testes isolados com USB fictício; `docs/` = pesquisa e plano técnico;
`dist/` = ZIP gerado. Não há aplicação HTML ou binário ARM incluído.
Veja [compatibilidade](docs/compatibility.md), [etapa 2](docs/stage-2.md) e
[roteiro no aparelho](docs/device-validation.md). O objetivo da etapa 1 é obter
inventário suficiente para decidir a próxima experiência; a GUI permanece bloqueada
até a validação de renderização, entrada e retorno seguro ao sistema original.
