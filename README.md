# Kindle Cover Home 0.2.1 — pacote único de teste no B023

Esta entrega corrige o acionamento da extensão e inclui **um aplicativo Kindlet
compilado e assinado**, com desenho e controles próprios, sem usar eips ou framebuffer
direto. A GUI é executada no Kindle; não depende de gerar PNG no computador.

**Ainda não testado no B023/4.1.4.** Não confundir compilação, assinatura verificada
e testes de desktop com funcionamento real. Também não está pronto o lançamento
direto do aplicativo pelo KUAL nem a abertura de livros pelo leitor Amazon.
Essas integrações não usam comandos internos presumidos.

## Instalação Windows (atualizar 0.2.0)

1. Baixe `dist/kindle-cover-home-0.2.1.zip` da branch `development` e extraia no PC.
2. Conecte o Kindle. Aqui `X:` é a unidade que contém `documents`.
3. Faça backup **no PC** de `X:\extensions\kindlecoverhome` e remova somente essa
   pasta da unidade. Preserve livros, KUAL, outras extensões e dados antigos.
4. Copie `extensions\kindlecoverhome` do pacote para
   `X:\extensions\kindlecoverhome` (sem mesclar versões).
5. Copie **somente** `documents\KindleCoverHome-0.2.1.azw2` do pacote para
   `X:\documents\KindleCoverHome-0.2.1.azw2`. Se já existir, faça backup antes.
   Não substitua o KUAL. Não é necessário copiar `tools`, `kindlet` ou `tests`.
6. Ejete com segurança. Abra o KUAL e siga os três testes rápidos abaixo.
   Reabra o KUAL ou recarregue o menu se continuar vendo rótulos antigos.

Não instalar certificados, firmware, SSH, Python ou Node no aparelho. O AZW2 usa as
chaves públicas de desenvolvimento do fonte atual do KUAL; o aparelho pode ter um
conjunto diferente. Se houver rejeição de assinatura/autorização, registre a mensagem
e não altere as chaves do dispositivo para forçar a execução.

## Teste KUAL: arquivos exatos para verificar

Antes de cada ensaio, copie os resultados anteriores para o PC ou renomeie-os por
USB, para não interpretar um arquivo antigo como execução nova. Espere a ação terminar
antes de conectar USB; não importa se o KUAL ficou aberto ou voltou à Home.

| Comando no KUAL | Verificar na unidade USB | Evidência esperada |
| --- | --- | --- |
| Teste 0 - acionamento direto KUAL | `X:\coverhome-kual-dispatch.txt` | `KUAL_DISPATCH_0.2.1` |
| Teste basico KUAL | `X:\coverhome-kual-test.txt` | `BASIC_SCRIPT_ENTERED` e `BASIC_SCRIPT_COMPLETED` |
| Teste progressivo - caminhos e logs | `X:\coverhome-bootstrap.log` e `X:\coverhome\logs\bootstrap-probe.txt` | `PROBE_COMPLETED`, `BOOTSTRAP_EXIT=0` e `LOG_WRITE_OK` |
| Iniciar Kindle Cover Home | `X:\coverhome-bootstrap.log`, `X:\coverhome\logs\session.log`, `X:\kindle-cover-home-data\catalog.tsv` | `CHILD_EXIT=0`, `BOOTSTRAP_EXIT=0`, `completed mode=scan` e catálogo |
| Gerar catálogo de demonstração | mesmos logs e `X:\kindle-cover-home-data\demo.tsv` | `completed mode=demo` e seis entradas fictícias |
| Diagnostico 0.2.1 | mesmos logs | `completed mode=diagnose`, kernel, ferramentas e entrada |

Os rótulos antigos sem acentos de alguns itens foram mantidos no menu por compatibilidade.
Se algum teste falhar, veja a [tabela de diagnóstico](docs/kual-0.2.1.md). O primeiro
comando não precisa sequer da pasta `bin`; o segundo depende só de seu arquivo shell.
Não é necessário SSH para nenhum desses testes.

## Testar o aplicativo visual no Kindle

Depois de executar Iniciar pelo KUAL para atualizar o catálogo, pressione Home e
abra **Kindle Cover Home** na biblioteca Amazon (o AZW2 novo). **Este passo pela Home
é manual**: não foi encontrada uma API pública comprovada para um atalho KUAL → Kindlet.
O comando Iniciar do menu continua sendo o scanner legado, não é um lançador da GUI.

O Kindlet tenta habilitar, pelo mecanismo MKK já usado pelo KUAL, permissões **desta
aplicação** para ler `documents`, ler o catálogo e escrever seu log. Não pede
AllPermission, não instala nem modifica o MKK, não toca no firmware e não captura evdev.
Se não conseguir, a tela informa a falta de acesso. Use Menu → Demonstracao para testar
o desenho e os botões independentemente da leitura dos livros.

A tela possui grade 2 × 3, seis capas por página, título/autor, seleção e rodapé.
Adapta-se à área útil fornecida pelo framework; barras Amazon podem reduzir os
600 × 800 físicos. Direcional move seleção, centro confirma apenas a seleção,
laterais trocam página. Voltar **não é consumido** e Home permanece com o framework.
Menu oferece demonstração e recarregamento de catálogo. Não há daemon nem processo
nativo sobrevivendo ao encerramento.

Capas reais: sidecars JPG/PNG e leitura limitada de MOBI/AZW/PRC/AZW3 compatíveis com
PalmDB + cabeçalho MOBI/EXTH, **sem DRM**. Lê autor, título e imagem indicada pelo
EXTH; falhas usam nome de arquivo e placeholder. Converte imagens para grayscale
no próprio aplicativo. EPUB/PDF têm sidecars/placeholder no Kindlet; a extração
EPUB do PC continua preservada, mas não é requisito para esta experiência.

Usa o TSV da Etapa 1 quando disponível, validando caminhos dentro de `documents`;
na ausência do TSV faz varredura local somente leitura. Para atualizar uma lista
existente, execute o scanner KUAL novamente e recarregue o catálogo no Kindlet.
Limite de 600 livros e seis imagens em memória; capa comprimida até 1 MiB e até
1.048.576 pixels decodificados, reduzidos para ate 180 × 230 por capa em cache. Inicialização e troca de página podem demorar no
hardware antigo; não há medição real ainda. Sem rede ou alteração dos livros.

## Validação objetiva e limites

1. Confirmar que o AZW2 abre, sem erro de assinatura ou permissão. Se não abrir,
   anotar mensagem exata; o pacote não deve ser chamado operacional nesse aparelho.
2. Menu → Demonstracao: conferir seis células, seleção, direcionais e paginação
   com biblioteca pessoal de sete ou mais livros. Com somente seis livros não há
   segunda página. Confirmar Back/Home sem navegação residual na Home.
3. Recarregar catálogo: comparar livros e capas reais com a Home original; confirmar
   que arquivo sem capa aparece com placeholder e nenhum livro foi modificado.
4. Centro: a seleção é exibida, **não abre livro**. Abra normalmente pela Home;
   voltar ao novo Kindlet pela Home é manual. Não há integração automática de retorno.
5. Suspender/retomar, sair e reabrir. Confirmar que a Home e o leitor original
   continuam funcionando. Se não, interromper o teste e remover somente o protótipo.

Log nativo preferido: `X:\coverhome\logs\kindlet.log`, após preparar logs pelo KUAL.
Se indisponível, procure `coverhome-kindlet.log` dentro da pasta de dados da aplicação
sob `X:\developer`; o caminho exato é fornecido pelo KDK e aparece no próprio log.
Registra CREATE/START/STOP/DESTROY, permissões e códigos de teclas recebidos **apenas
em foco**. Limite aproximado de 64 KiB. Não registra o conteúdo de livros. Ausência
desse log pode significar que a aplicação nem foi autorizada a iniciar.

## Remoção / reversão

Feche o aplicativo, conecte USB e remova apenas:

- `X:\documents\KindleCoverHome-0.2.1.azw2` (o aplicativo novo, não seus livros);
- `X:\extensions\kindlecoverhome` (extensão deste projeto).

Opcionalmente faça backup e remova `coverhome`, `kindle-cover-home-data`,
`coverhome-bootstrap.log`, `coverhome-kual-dispatch.txt`, `coverhome-kual-test.txt`
e os dados privados deste Kindlet em `developer`. Não apague toda a pasta developer.
Restaure a extensão 0.2.0 do backup se desejar. Nenhuma partição ou Home foi alterada.
O script `tools/uninstall.sh` continua removendo só a extensão; o AZW2 novo deve ser
removido manualmente. Isso evita que o script apague documentos.

## Código, testes e versões preservadas

A Etapa 1 e a interface PNG 0.2.0 foram preservadas. A GUI PNG continua desativada por
padrão; **não habilite eips para este ensaio**. O aplicativo novo não usa essa saída.
Veja [README anterior](docs/README-0.2.0.md), [pesquisa KUAL](docs/kual-0.2.1.md) e
[build Kindlet](kindlet/README.md). Código novo em `kindlet/src/coverhome`.

```sh
python3 -m pip install -r tools/requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 tools/package.py
```

A suite testa scripts legados, ações a partir de diretório arbitrário, falhas
progressivas, catálogo, capa MOBI sintética sem DRM, navegação e desenho Java.
O teste Java usa o JDK do **computador**; o dispositivo já tem o runtime de Kindlets.
A assinatura foi verificada contra o keystore público de referência, não contra as
chaves instaladas no seu aparelho. Os testes não certificam B023/4.1.4.
