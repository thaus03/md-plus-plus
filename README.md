# md++

Editor leve de arquivos Markdown para Windows, feito em Python.

Alternativa mais leve ao VS Code para quem só precisa visualizar e editar `.md`.

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
pyinstaller --noconfirm --onefile --windowed --name "md++" --paths src --collect-all customtkinter main.py
```

- `--onefile`: gera um único `md++.exe` em vez de uma pasta com vários arquivos.
- `--windowed`: não abre um console junto com a janela do app.
- `--paths src`: o `main.py` só adiciona `src/` ao `sys.path` em tempo de execução, mas o
  PyInstaller decide o que empacotar a partir de uma análise estática que roda *antes*
  disso — sem essa flag ele não enxerga o pacote `mdpp` e o `.exe` falha com
  `ModuleNotFoundError: No module named 'mdpp'`.
- `--collect-all customtkinter`: garante que os temas/assets do CustomTkinter (arquivos
  `.json` de tema) vão junto no pacote — sem isso o `.exe` roda mas quebra na hora de
  aplicar o tema.

O executável fica em `dist/md++.exe`. As pastas `build/` e `dist/` geradas nesse processo
já estão no `.gitignore`, não sobem para o repositório.

Para adicionar um ícone customizado, inclua `--icon=caminho\para\icone.ico` no comando.

## Versionamento

Gestão de mudanças e versionamento: neste repositório GitHub.
