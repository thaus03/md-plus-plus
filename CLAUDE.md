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
```

Enquanto o app for pequeno, não dividir em mais módulos/camadas do que o necessário.

## Roadmap (não implementar até ser pedido)

- Busca dentro do arquivo
- Atalhos de teclado adicionais
- Preview renderizado de Markdown (hoje é só edição de texto puro)

## Versionamento

Todo o histórico de mudanças vive no GitHub — **não crie arquivos de changelog/notas de
release no repo**, o log de commits e PRs é a fonte da verdade.

- Repo: https://github.com/thaus03/md-plus-plus
- Commits em português, mensagens curtas no imperativo (ex: "Adiciona busca no editor").
- Não fazer commit/push sem o usuário pedir explicitamente nesta sessão.
- Não criar arquivos de documentação de produto/arquitetura soltos neste repo; esse
  contexto é mantido fora daqui.
