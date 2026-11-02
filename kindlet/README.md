# Protótipo Kindlet — build e limites

Arquitetura KDK 1.x, `AbstractKindlet`, superfície KComponent/AWT e KindleKeyCodes.
Usa o framebuffer **somente através do desenho gerenciado do framework**, sem
abrir /dev/fb0, ioctl, eips ou dispositivos de input. O framework gerencia foco,
suspensão e Home. create/start/stop/destroy e KeyListener estão implementados.

O runtime é o que já executa KUAL no Kindle. Não há Python/Node/JVM adicional.
As classes geradas usam Java 1.4, major version 48. Isso comprova o formato legado,
não a compatibilidade completa das APIs no aparelho. SDK usado: Kindlet-1.3.

## Build no computador

Entradas externas explícitas (não distribuídas como SDK/segredos no pacote):

- SDK jar do ambiente de desenvolvimento compatível com KDK 1.x. Referência técnica
  inspecionada: pepijndevos/KindleTerm commit e8761fced830b7772ef165d370fc33171e4ce0f7.
  SHA256 do jar usado: `4eb6b54e9a714a65286fb66aac4f805e70b23d31de55288ba0d5b0ef6a5305b2`.
- ECJ 3.37.0 de Maven Central, SHA256 `cde026ff966b48b5e5f148b6f041ceff3cf4f85cf75155f4ec0f40e4ee14b545`.
- Keystore **público de testes** do fonte KUAL, commit
  fcb45b51f4a70a3222a21b5f185fd1b30b3aa89d. Aliases dktest/ditest/dntest,
  certificados RSA 2048 válidos de 1999 a 2099. Chaves de teste públicas não são
  identidade de produção. Nenhuma chave privada é incluída no repositório/ZIP.

Configure `KCH_SIGN_STOREPASS` localmente e execute:

```sh
python3 tools/build_kindlet.py --sdk /caminho/Kindlet-1.3.jar --ecj /caminho/ecj.jar --keystore /caminho/developer.keystore
```

O script usa Java para ECJ e jarsigner do módulo jdk.jartool. Assina com SHA256withRSA
+ SHA-256, como o build.xml atual do KUAL. Verificação realizada com jarsigner
`-verify -strict` e o keystore de referência, sem desativar TLS ou algoritmos de
verificação. A confiança instalada no B023 pode ser diferente: só teste real prova
aceitação. Não se instala certificado ou modifica truststore neste projeto.

## Dependência MKK e permissões

`vendor/jailbreak.jar` é o adaptador binário não modificado incluído pelo projeto
KUAL no commit citado. SHA256 `f21d7e519cb998dc0e49729e88d21d785c346d520b7f26737679573d82d5534c`.
Proveniência: https://bitbucket.org/ixtab/kindlelauncher/src/fcb45b51f4a70a3222a21b5f185fd1b30b3aa89d/lib/jailbreak.jar
Crédito ao autor ixtab e projeto KUAL; não é código autoral deste projeto.
O pacote inclui suas classes necessárias, não o SDK Amazon. O adaptador se comunica
com o MKK existente; não o instala, não modifica arquivos de firmware e não inicia
serviços. O objeto Access solicita apenas FilePermission para documents (leitura),
TSV (leitura) e log específico (leitura/escrita), **não AllPermission**. A permissão é
associada a este aplicativo; a biblioteca desabilita seu contexto no stop.

Se MKK/permissões falharem, o Kindlet mantém a demonstração e mostra erro de acesso;
não chama shell nem tenta contornar com alterações de firmware. Dados privados e
log de fallback ficam em getHomeDirectory, gerenciado pelo KDK. Sidecars e MOBI/EXTH
são lidos dentro dos limites descritos no README; não contorna DRM. A extração de
MOBI é um parser limitado, não suporte universal a todos os arquivos AZW/KF8.

Não há API pública de abrir outro livro no KindletContext examinado. Por isso não
foi implementado shell/LIPC/D-Bus para abrir o leitor nem para abrir o Kindlet a
partir do KUAL. Para testar: preparar pelo KUAL e abrir o AZW2 pela Home, manualmente.

## Evidência disponível

- Compilação contra SDK 1.x e inspeção major 48 de todas as classes.
- Assinaturas verificadas contra o keystore de referência.
- Testes Java do núcleo: navegação/páginas, catálogo, TSV legado, MOBI/EXTH sintético,
  capa decodificável, arquivo protegido ignorado, fallback de erro e renderizador.
- Esses testes não executam lifecycle KDK, adaptador MKK, teclado ou painel E Ink.
  Todos permanecem pendentes de ensaio real. Não afirmar que a GUI está validada.
