# md++

Editor leve de Markdown para Windows, em Python. Alternativa ao VS Code para quem só
precisa visualizar/editar `.md` sem o peso de uma IDE completa.

## Stack e restrições (fixas — não reabrir sem pedido explícito do usuário)

- Python 3.11+, GUI com **CustomTkinter** (escolhido sobre PySide6/Qt por ser mais leve;
  sobre Tkinter puro por ter widgets/tema modernos prontos).
- **Windows é a única plataforma alvo.** Não adicionar abstrações cross-platform,
  detecção de SO, ou paths POSIX "só por garantia".
- Sem dependências pesadas. Antes de adicionar uma lib, considerar se dá para resolver
  com stdlib ou com o que já está em `requirements.txt`.

## Estrutura

```
main.py            # launcher fino
src/mdpp/app.py    # janela principal (CTk), toda a lógica da UI hoje mora aqui
src/mdpp/assets/   # ícones da toolbar (PNG _l/_d por tema) e mdpp.ico do app
```

Assets entram no `.exe` via `--add-data "src/mdpp/assets;mdpp/assets"` (resolvidos em
runtime por `asset_path()`, que trata dev vs congelado). Ícones novos: gerar PNG 64px em
par claro/escuro seguindo o padrão `nome_l.png`/`nome_d.png`.

Enquanto o app for pequeno, não dividir em mais módulos/camadas do que o necessário.

## Roadmap (não implementar até ser pedido)

- Busca dentro do arquivo
- Atalhos de teclado adicionais

Já implementado: alternância edição/preview (Ctrl+E, renderiza com `markdown` +
`tkinterweb`, motor Tkhtml3 — trocado do `tkhtmlview` inicial por falta de suporte real a
CSS/tabelas; links externos abrem no navegador via `on_link_click`), caminho absoluto na
barra de título, undo, abertura por argumento de linha de comando, tema
Sistema/Claro/Escuro (seletor na toolbar + menu Exibir; CSS do preview acompanha via
`build_preview_style`), menubar nativa `tk.Menu` (Arquivo/Exibir/Ajuda), menu de contexto
no botão direito e toolbar com ícones (`CTkImage` claro/escuro).

## Versionamento

Todo o histórico de mudanças vive no GitHub — **não crie arquivos de changelog/notas de
release no repo**, o log de commits e PRs é a fonte da verdade.

- Repo: https://github.com/thaus03/md-plus-plus
- Commits: Conventional Commits, corpo em português (`feat(preview): adiciona busca no
  editor`) — convenção geral em `~/.claude/CLAUDE.md`, não repetir aqui.
- Não fazer commit/push sem o usuário pedir explicitamente nesta sessão.
- Não criar arquivos de documentação de produto/arquitetura soltos neste repo; esse
  contexto é mantido fora daqui.
- Doc de build do executável vive na Wiki do GitHub (página "Gerar executável
  (Windows)"), não no README — mudanças no processo de build atualizam a Wiki.
