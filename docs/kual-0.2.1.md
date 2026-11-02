# Investigação KUAL-KDK e diagnóstico 0.2.1

Fonte original consultado: https://bitbucket.org/ixtab/kindlelauncher
commit `fcb45b51f4a70a3222a21b5f185fd1b30b3aa89d`.
O README desse projeto associa K2/K3/K4 a `KUAL-KDK-1.0.azw2` e documenta que
normalmente selecionar uma ação encerra o Kindlet.

`src/com/mobileread/ixtab/kindlelauncher/KualKindlet.java`:
- Sem opção `e` (gerada por `exitmenu:false`), a ação fica em `commandToRunOnExit`;
  o menu encerra e executa em `onStop`. Logo, **voltar à Home não prova falha**.
- Com `exitmenu:false`, chama execute sem encerrar o menu.
- execute usa o diretório da extensão e `/bin/sh` em launcher temporário;
  createLauncherScript monta `{ comando ; }` e redireciona stderr para `/var/tmp/KUAL.log`.

`resources/parse-commented.awk` combina action + params. Há versões da função que
normalizam caminhos e corrigem argumentos misturados em action. Caminhos relativos
normalmente têm o diretório da extensão como base; **não foi provado que o cwd causou
a falha observada**. Não presumir que o KUAL instalado seja idêntico ao commit lido.

A 0.2.1 elimina ambiguidades: `action: /bin/sh`, `params` separados com paths
absolutos USB e `exitmenu: false` em todas as ações. Não usa executabilidade FAT,
PATH para localizar shell nem diretório corrente para localizar o primeiro script.
Os rótulos JSON são ASCII para evitar a limitação de caracteres >127 descrita no parser legado.
O bootstrap usa pwd somente para registrar evidência e cd explícito sem `--`.
Os scripts legados permanecem iguais e são executados como filhos, com status registrado.

## Interpretação dos testes no aparelho

| Evidência nova | Interpretação / próximo passo |
| --- | --- |
| Teste 0 não gera `coverhome-kual-dispatch.txt` | Falha antes de qualquer script do projeto: ação/parser/cache do menu, shell ou escrita no USB. Verificar menu novo e espaço/acesso; isso sozinho não identifica qual deles. |
| Teste 0 funciona, básico não gera `coverhome-kual-test.txt` | Foco em caminho absoluto do script básico, arquivo ausente/ilegível, CRLF/BOM ou erro de interpretação. |
| Básico funciona, bootstrap não gera `coverhome-bootstrap.log` | Foco em caminho/sintaxe do bootstrap, segurança de caminho ou abertura do trace. Ainda não chegou aos logs da aplicação. |
| `BOOTSTRAP_ENTERED`, `SHELL_STARTED` | Shell e primeiro arquivo realmente executaram; INITIAL_CWD mostra o cwd observado. |
| `ROOT_UNAVAILABLE` / `SCRIPT_UNREADABLE` | Caminho esperado indisponível, link simbólico recusado ou script ausente/ilegível. |
| `SHELL_SYNTAX_FAILED` | `/bin/sh -n` rejeitou o script filho; conferir erro imediatamente anterior e integridade/LF dos arquivos. |
| `CWD_READY`, depois `LOG_DIRECTORY_FAILED` | A criação de coverhome/logs falhou; pode haver arquivo no lugar de diretório ou problema de escrita. Não apagar dados pessoais para corrigir. |
| `LOG_WRITE_FAILED` | Diretório preparado, mas não foi possível gravar o arquivo de prova. |
| `LOG_WRITE_OK` + `PROBE_COMPLETED` | Caminhos, shell e criação/escrita dos logs passaram neste teste. |
| `CHILD_START`, `CHILD_EXIT` diferente de zero | Entrada foi acionada; ver erro no bootstrap antes do redirecionamento ou session.log depois dele. O código é preservado. |
| `CHILD_EXIT=0`, `BOOTSTRAP_EXIT=0` + `completed mode=...` | Execução confirmada independentemente de qual tela ficou visível. |

Os traces são substituídos a cada ação; session.log preserva uma execução anterior.
Copie-os antes do próximo teste. Evite ações simultâneas e USB enquanto comandos rodam.
O teste direto escreve apenas um arquivo na raiz USB; o básico usa só builtins sh.
Os demais testes não ativam eips, IPC, framebuffer ou captura de entrada.

A suite de computador reproduz montagem de comando shell do fonte consultado, mas
não emula o parser Java/AWK completo, lifecycle, privilégios ou cache do KUAL real.
A causa específica da ausência de logs em 0.2.0 continua dependente desses resultados;
a correção de configuração não deve ser relatada como validada no B023 antes disso.
