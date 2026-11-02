# Roteiro no Kindle real — ainda não executado

Antes: faça backup dos documentos e registre a Home funcional. Instale por USB,
ejete e confirme abertura normal do KUAL já existente. Não é necessário rede.

1. Verifique os dois comandos da extensão. Execute o lançamento normal; ele deve
   terminar e deixar o KUAL utilizável. Reconecte por USB e confira diagnóstico e
   catálogo; ausência de arquivo não é sucesso. Registre erros exibidos pelo KUAL.
2. Confirme firmware 4.1.4 no diagnóstico quando a fonte estiver disponível; compare
   hardware B023 nas informações já conhecidas do dispositivo. O script não certifica
   automaticamente o modelo. Se utilitários faltarem, preserve o erro e interrompa
   o portão da GUI para adaptar o scanner, sem instalar pacotes de Linux moderno.
3. Compare o catálogo com alguns arquivos existentes sem alterá-los. Confira nomes
   com espaços/acentos; autor deve ser desconhecido. Capas são apenas candidatas.
   Registre a duração. Verifique que livros continuam abrindo normalmente pela Home.
4. Execute demonstração. Confira exatamente seis linhas de dados em `demo.tsv`,
   todos os caminhos `demo://`, sem novos livros em `documents`. O catálogo real
   deve permanecer disponível e separado.
5. Execute novamente para avaliar repetibilidade e bloqueio. Após retorno normal
   não deve restar `.lock`. Compare hashes de livros antes/depois no computador
   se desejar uma verificação independente de preservação.
6. Remova a extensão; confira desaparecimento do menu, KUAL e Home funcionais e
   livros preservados. Dados permanecem para inspeção; apague-os só se desejar.

Anote modelo/firmware, versão do pacote, resultado de cada passo e falhas. Não
anexe catálogo pessoal publicamente sem revisão. Não considere renderização,
botões ou abertura pela extensão aprovados: esta versão não os exercita.
