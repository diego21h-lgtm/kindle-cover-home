# Pesquisa de compatibilidade

## Identificação e evidências

Fontes públicas consultadas durante esta implementação (URLs de branches móveis;
revalide e fixe commits antes de incorporar dependências). Nenhum código dessas
fontes é distribuído pelo projeto; as referências orientam a investigação.

- [FBInk: identificação](https://github.com/NiLuJe/FBInk/blob/master/fbink_device_id.c):
  `case 0x23` identifica **K4b**, Sauza, Yoshi, `isKindleLegacy = true`.
  O rótulo interno K5 nesse código designa **Touch**, não o Basic B023.
- [KOReader: dispositivo Kindle](https://github.com/koreader/koreader/blob/master/frontend/device/kindle/device.lua):
  conjunto `k4_set = {"0E", "23"}`; `Kindle4:init()` usa
  `ffi/framebuffer_einkfb`, enquanto Kindle Touch usa `framebuffer_mxcfb`.
  Portanto, não aplicar indiscriminadamente ioctls EPDC/MXCFB de modelos touch.
- [Mapa K4](https://github.com/koreader/koreader/blob/master/frontend/device/kindle/event_map_kindle4.lua):
  documentado para FW 3.x/4.x, com direcionais 103/108/105/106, centro 194,
  Home 102, Back 158, Menu 139; paginação 104/191 e 109/193.
  São candidatos técnicos, **não medições deste aparelho**. O mapa contém ainda
  teclas de K3: não supor que todas existam fisicamente no Basic.
- [FBInk README](https://github.com/NiLuJe/FBInk/blob/master/README.md): framebuffer,
  imagens e texto, menção a `eips`, targets Kindle e toolchain própria.
  Isso sustenta uma investigação nativa; não certifica um binário recente no FW 4.1.4.
  FBInk é GPLv3+; eventual distribuição exige observar sua licença.
- [Exemplo KUAL config.xml](https://github.com/koreader/koreader/blob/master/platform/kindle/extensions/koreader/config.xml)
  e [menu.json](https://github.com/koreader/koreader/blob/master/platform/kindle/extensions/koreader/menu.json):
  estrutura `<extension>`, menu JSON e ações. O payload segue essa estrutura;
  aceitação no KUAL-KDK instalado ainda requer teste real.

## Interfaces e decisão nesta etapa

| Recurso | Candidato | Evidência / limitação | Uso nesta versão |
| --- | --- | --- | --- |
| Menu | KUAL XML + JSON + shell | Exemplo público; versão local não ensaiada | Implementado, pendente hardware |
| Texto simples | `eips` | Ferramenta Kindle referenciada no FBInk; sintaxe/capacidade variam | Só presença |
| Capas e refresh | framebuffer legado + FBInk apropriado | B023 marcado legado; KOReader usa einkfb | Não escreve pixels nem envia ioctl |
| Botões | Linux evdev `/dev/input/event*` | KOReader usa descoberta; fallback event0/event1 | Só inventário via proc/sysfs |
| Abertura no leitor Amazon | investigar associação de documento e IPC do framework 4.x | Nenhum método comprovado no B023/4.1.4 nesta pesquisa | Não implementado |
| KDK Kindlet | Outra via possível para desenho/entrada sob framework | KUAL existente demonstra execução de seu Kindlet, não autorização/API para um novo | Não escolhido sem SDK/assinatura e teste |
| HTML | Nenhum host validado | Navegador não é um runtime de extensões garantido | Não adotado |

LIPC/D-Bus são hipóteses de investigação para abrir documentos; presença dos
executáveis não estabelece nomes de serviços, propriedades, URI, escaping ou
semântica no firmware 4.x. Não copiar `com.lab126.appmgr`/`start` de guias 5.x como
se funcionassem aqui. Não invocar IPC exploratório com efeitos colaterais nesta etapa.

O diagnóstico deliberadamente não executa `eips`, `fbink`, `lipc-set-prop`, não
abre `/dev/fb0`, não captura evdev e não suspende o framework. Shell e ferramentas
BusyBox são uma escolha conservadora, mas precisam passar pelo roteiro do aparelho.
A resolução 600 × 800 foi fornecida pelo usuário; não medida na nuvem.
