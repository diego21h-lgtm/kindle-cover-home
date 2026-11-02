# Validação no B023 / 4.1.4 — pendente

Nenhuma linha abaixo está marcada como executada no aparelho. O resultado esperado
é critério de teste, não evidência de aprovação.

1. Faça backup da extensão 0.1.0 e saídas no PC. Confirme Home, livro de teste e KUAL
   funcionando antes da atualização. Instale 0.2.0 conforme README.
2. Abra KUAL e execute diagnóstico novo; reconecte USB e verifique log novo em
   `coverhome/logs/session.log`, com modo e conclusão. Registre versão real, resolução
   reportada, bpp, presença de eips/awk e comportamento de erros. Não compartilhe
   serial ou catálogo pessoal sem revisar.
3. Execute scanner e demo originais pelo menu. Compare catálogo e hashes de livros
   antes/depois. A informação de início e conclusão deve corresponder ao comando
   escolhido; `previous.log` guarda a execução anterior. Valide LF, shell e duração.
4. Verifique a ajuda local de `/usr/sbin/eips`, por shell já disponível, se houver;
   `eips -h` é consulta de ajuda, não prova capacidade. Registre a saída no PC e
   confirme explicitamente `-g`, imagem PNG e comportamento conhecido de refresh.
   Se ferramenta/ajuda não estiverem disponíveis ou houver ambiguidade, **não
   habilite renderização**. Não instalar binários de origem desconhecida.
5. Após confirmar o candidato, crie o marcador vazio `coverhome/enable-eips` via USB.
   Ejete e execute Mostrar demonstracao pelo KUAL. Observe desenho, orientação,
   integridade, grayscale, refresh, ghosting, tempo e se o framework repinta.
   Compare com `docs/preview-0.2.0.png`. Registre foto ou relato; retorno zero sozinho
   não valida a tela. Erro fica em `coverhome/logs/session.log`.
6. Se o KUAL perder legibilidade por causa da imagem, **não navegue às cegas**.
   Use Back/Home para solicitar redesenho normal. Confirme recuperação, remova o
   marcador e considere o experimento reprovado para uma GUI utilizável. Não pare
   framework nem use captura global como correção improvisada.
7. Somente se houver convivência utilizável, experimente ações do menu KUAL de
   movimento e páginas. Não esperar direcional ou botões laterais diretamente na
   grade. O centro continua selecionando itens do KUAL, não livros na imagem.
   O comando Selecionar da extensão só registra índice, sem abrir o leitor.
8. Encerrar sessão, voltar pelo KUAL, suspender/retomar e abrir livro normalmente
   pela Home. Sem processo permanente ou evento capturado. Para biblioteca real,
   preparar imagens no PC e repetir; testar catálogo vazio e sete livros para páginas.
9. Remover extensão; confirmar KUAL, Home e livros intactos. Reinstalar 0.1.0 do ZIP
   antigo se necessário; nenhum arquivo de firmware foi alterado.

Registrar por passo: modelo/firmware, versão do pacote, resultado, log/foto,
limitação e recuperação. Permanecem pendentes: foco exclusivo, disponibilidade e
comportamento real do eips, refresh e coexistência Amazon, códigos físicos, captura
segura e abertura nativa. Esses itens não podem ser certificados pelo teste de PC.
