# md++

Editor leve de arquivos Markdown para Windows, feito em Python.

Alternativa mais leve ao VS Code para quem só precisa visualizar e editar `.md`.

## Funcionalidades

- Abrir, editar, salvar e criar arquivos `.md`.
- Botão **Visualizar/Editar** na barra de ferramentas para alternar entre o texto puro e
  o Markdown renderizado (títulos, negrito, itálico, listas, código, tabelas, links).
- Barra de título mostra o caminho absoluto do arquivo aberto.

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

## Gerar executável (Windows)

Usamos [PyInstaller](https://pyinstaller.org/) para empacotar o app em um `.exe` único,
sem precisar de Python instalado na máquina de destino.

```
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "md++" --paths src --collect-all customtkinter --collect-all markdown --collect-all tkhtmlview main.py
```

- Rode como `python -m PyInstaller`, não como o comando solto `pyinstaller`. Se você tiver
  mais de um Python instalado (ex: um global e um venv), `pyinstaller` no PATH pode
  resolver pra uma instalação diferente da que você usou pro `pip install -r
  requirements.txt` — aí ele empacota sem enxergar as libs do projeto, mesmo que elas
  estejam instaladas "em algum lugar". `python -m PyInstaller` garante que o empacotamento
  roda com o mesmo interpretador (e mesmo site-packages) que você já ativou.
- `--onefile`: gera um único `md++.exe` em vez de uma pasta com vários arquivos.
- `--windowed`: não abre um console junto com a janela do app.
- `--paths src`: o `main.py` só adiciona `src/` ao `sys.path` em tempo de execução, mas o
  PyInstaller decide o que empacotar a partir de uma análise estática que roda *antes*
  disso — sem essa flag ele não enxerga o pacote `mdpp` e o `.exe` falha com
  `ModuleNotFoundError: No module named 'mdpp'`.
- `--collect-all customtkinter`: garante que os temas/assets do CustomTkinter (arquivos
  `.json` de tema) vão junto no pacote — sem isso o `.exe` roda mas quebra na hora de
  aplicar o tema.
- `--collect-all markdown`: a lib `markdown` carrega suas extensões (`fenced_code`,
  `tables`, `sane_lists`) dinamicamente por nome de módulo, algo que a análise estática do
  PyInstaller não enxerga sozinha — sem essa flag o preview quebra com
  `ModuleNotFoundError: No module named 'markdown.extensions.fenced_code'`.
- `--collect-all tkhtmlview`: garantia extra para o widget de preview ser empacotado por
  completo (módulo, submódulos e eventuais dados).

O executável fica em `dist/md++.exe`. As pastas `build/` e `dist/` geradas nesse processo
já estão no `.gitignore`, não sobem para o repositório.

Para adicionar um ícone customizado, inclua `--icon=caminho\para\icone.ico` no comando.

### "ModuleNotFoundError" no .exe mesmo com a lib instalada

Sintoma: o app funciona com `python main.py` mas o `.exe` reclama de um módulo que você
tem certeza que instalou. Quase sempre é ambiente errado — confirme com:

```
python -c "import sys; print(sys.executable)"
python -m pip show tkhtmlview
```

Se o `sys.executable` não apontar pro Python do venv onde as libs estão instaladas, ative
o venv correto antes de rodar o `python -m PyInstaller ...`.

## Versionamento

Gestão de mudanças e versionamento: neste repositório GitHub.
