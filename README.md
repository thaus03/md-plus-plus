# md++

Editor leve de arquivos Markdown para Windows, feito em Python.

Alternativa mais leve ao VS Code para quem só precisa visualizar e editar `.md`.

## Funcionalidades

- Abrir, editar, salvar e criar arquivos `.md`.
- Botão **Visualizar/Editar** (Ctrl+E) para alternar entre o texto puro e o Markdown
  renderizado (títulos, negrito, itálico, listas, código, tabelas, links — links abrem no
  navegador do sistema).
- Menu **Arquivo / Exibir / Ajuda**, menu de contexto no botão direito e toolbar com
  ícones.
- Tema **Sistema / Claro / Escuro**, com o preview acompanhando.
- Barra de título mostra o caminho absoluto do arquivo aberto.
- Desfazer/refazer no editor (Ctrl+Z / Ctrl+Y).
- Abre arquivo passado como argumento (`md++.exe caminho\arquivo.md`) — permite associar
  `.md` ao md++ no "Abrir com" do Windows.
- Aceita arquivos em UTF-8 (com ou sem BOM) e CP1252 (encoding comum em `.md` antigos
  do Windows); ao salvar, grava sempre em UTF-8.

## Requisitos

- Python 3.11+
- Windows

## Instalação

```
pip install -r requirements.txt
```

## Uso

```
python main.py
```

## Executável (Windows)

Baixe a versão pronta na [página de Releases](https://github.com/thaus03/md-plus-plus/releases)
— não precisa de Python instalado.

Para compilar você mesmo, o passo a passo completo (comando do PyInstaller, explicação de
cada flag e solução de problemas) está na
[Wiki: Gerar executável (Windows)](https://github.com/thaus03/md-plus-plus/wiki/Gerar-executável-Windows).
O mesmo build roda automaticamente no GitHub Actions a cada PR.

## Versionamento

Gestão de mudanças e versionamento: neste repositório GitHub.
