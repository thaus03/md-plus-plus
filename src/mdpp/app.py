import os
import sys
import webbrowser
from tkinter import filedialog, messagebox

# Builds com --windowed não têm console: sys.stdout/stderr ficam None e qualquer
# write (ex: aviso do customtkinter durante o import) derruba o app. Redireciona
# para um arquivo de log em vez de descartar — tracebacks em produção precisam
# sobreviver em algum lugar pra dar pra diagnosticar depois.
if sys.stdout is None or sys.stderr is None:
    _log_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "mdpp")
    os.makedirs(_log_dir, exist_ok=True)
    _log = open(os.path.join(_log_dir, "mdpp.log"), "a", buffering=1, encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = _log
    if sys.stderr is None:
        sys.stderr = _log

import tkinter as tk

import customtkinter as ctk
import markdown
from PIL import Image
from tkinterweb import HtmlFrame

from mdpp import __version__

APP_TITLE = "md++"
REPO_URL = "https://github.com/thaus03/md-plus-plus"
WIKI_URL = "https://github.com/thaus03/md-plus-plus/wiki"
FILETYPES = [("Markdown", "*.md *.markdown"), ("Todos os arquivos", "*.*")]
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "sane_lists"]

PREVIEW_PALETTES = {
    "dark": {
        "bg": "#1e1e1e", "fg": "#dcdcdc", "heading": "#ffffff",
        "border": "#3a3a3a", "code_bg": "#2d2d2d", "code_fg": "#d4d4d4",
        "th_bg": "#2a2a2a", "link": "#4ea1ff",
        "quote_border": "#4a4a4a", "quote_fg": "#b0b0b0",
    },
    "light": {
        "bg": "#ffffff", "fg": "#1f1f1f", "heading": "#000000",
        "border": "#d0d7de", "code_bg": "#f6f8fa", "code_fg": "#1f2328",
        "th_bg": "#f0f1f2", "link": "#0969da",
        "quote_border": "#d0d7de", "quote_fg": "#59636e",
    },
}

PREVIEW_STYLE_TEMPLATE = """
body {{
    background-color: {bg};
    color: {fg};
    font-family: "Segoe UI", Calibri, sans-serif;
    font-size: 14px;
    line-height: 1.55;
    padding: 4px 18px 18px 18px;
}}
h1, h2, h3, h4, h5, h6 {{ color: {heading}; }}
h1 {{ border-bottom: 1px solid {border}; padding-bottom: 6px; }}
code {{
    font-family: Consolas, "Courier New", monospace;
    background-color: {code_bg};
    color: {code_fg};
    padding: 1px 4px;
}}
pre {{ background-color: {code_bg}; padding: 10px; }}
pre code {{ background-color: transparent; padding: 0; }}
table {{ border-collapse: collapse; margin: 10px 0; }}
th, td {{ border: 1px solid {border}; padding: 6px 12px; text-align: left; }}
th {{ background-color: {th_bg}; }}
a {{ color: {link}; }}
blockquote {{
    border-left: 3px solid {quote_border};
    margin-left: 0;
    padding-left: 12px;
    color: {quote_fg};
}}
"""


def build_preview_style(appearance_mode: str) -> str:
    """Monta o CSS do preview para o modo de aparência atual ("Dark"/"Light")."""
    key = "dark" if appearance_mode.lower() == "dark" else "light"
    return PREVIEW_STYLE_TEMPLATE.format(**PREVIEW_PALETTES[key])


def asset_path(name: str) -> str:
    # No .exe os assets são incluídos via --add-data "src/mdpp/assets;mdpp/assets"
    # e ficam sob sys._MEIPASS; em desenvolvimento, ao lado deste arquivo.
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "mdpp", "assets", name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", name)


def load_icon(name: str, size: int = 18) -> ctk.CTkImage:
    """Ícone da toolbar com variante para cada tema (sufixos _l/_d dos PNGs)."""
    return ctk.CTkImage(
        light_image=Image.open(asset_path(f"{name}_l.png")),
        dark_image=Image.open(asset_path(f"{name}_d.png")),
        size=(size, size),
    )


def read_text(path: str) -> str:
    """Lê o arquivo tentando UTF-8 (com ou sem BOM) e caindo para CP1252,
    encoding comum em .md antigos salvos no Windows."""
    with open(path, "rb") as f:
        raw = f.read()
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


class MdPlusPlusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_path: str | None = None
        self.dirty = False
        self.mode = "edit"  # "edit" | "preview"

        self.title(APP_TITLE)
        self.geometry("900x650")
        # wm_iconbitmap (não o alias iconbitmap): o alias estático do tkinter pula o
        # override do CTk, que então trocaria nosso ícone pelo dele ~200ms depois.
        self.wm_iconbitmap(asset_path("mdpp.ico"))

        self._build_menubar()
        self._build_toolbar()
        self._build_editor()
        self._build_context_menu()
        self._update_title()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_menubar(self):
        menubar = tk.Menu(self)

        arquivo = tk.Menu(menubar, tearoff=0)
        arquivo.add_command(label="Novo", accelerator="Ctrl+N", command=self.new_file)
        arquivo.add_command(label="Abrir...", accelerator="Ctrl+O", command=self.open_file)
        arquivo.add_separator()
        arquivo.add_command(label="Salvar", accelerator="Ctrl+S", command=self.save_file)
        arquivo.add_command(label="Salvar como...", command=self.save_file_as)
        arquivo.add_separator()
        arquivo.add_command(label="Sair", command=self.on_close)
        menubar.add_cascade(label="Arquivo", menu=arquivo)

        exibir = tk.Menu(menubar, tearoff=0)
        exibir.add_command(
            label="Alternar edição/visualização", accelerator="Ctrl+E", command=self.toggle_mode
        )
        tema = tk.Menu(exibir, tearoff=0)
        for choice in ("Sistema", "Claro", "Escuro"):
            tema.add_command(label=choice, command=lambda c=choice: self._select_theme(c))
        exibir.add_cascade(label="Tema", menu=tema)
        menubar.add_cascade(label="Exibir", menu=exibir)

        ajuda = tk.Menu(menubar, tearoff=0)
        ajuda.add_command(label="Wiki no GitHub", command=lambda: webbrowser.open(WIKI_URL))
        ajuda.add_command(label="Repositório", command=lambda: webbrowser.open(REPO_URL))
        ajuda.add_separator()
        ajuda.add_command(
            label="Sobre o md++",
            command=lambda: messagebox.showinfo(
                APP_TITLE, f"md++ {__version__}\nEditor leve de Markdown para Windows.\n{REPO_URL}"
            ),
        )
        menubar.add_cascade(label="Ajuda", menu=ajuda)

        self.config(menu=menubar)

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=36)
        toolbar.pack(side="top", fill="x")

        buttons = [
            ("Novo", "new", self.new_file),
            ("Abrir", "open", self.open_file),
            ("Salvar", "save", self.save_file),
            ("Salvar como", "save_as", self.save_file_as),
        ]
        for text, icon, command in buttons:
            ctk.CTkButton(
                toolbar, text=text, image=load_icon(icon), compound="left", width=110, command=command
            ).pack(side="left", padx=4, pady=4)

        self._icon_preview = load_icon("preview")
        self._icon_edit = load_icon("edit")
        self.mode_button = ctk.CTkButton(
            toolbar, text="Visualizar", image=self._icon_preview, compound="left", width=120,
            command=self.toggle_mode,
        )
        self.mode_button.pack(side="left", padx=4, pady=4)

        self.theme_menu = ctk.CTkOptionMenu(
            toolbar, values=["Sistema", "Claro", "Escuro"], width=110, command=self._on_theme_change
        )
        self.theme_menu.pack(side="right", padx=4, pady=4)

    def _build_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Desfazer", accelerator="Ctrl+Z", command=lambda: self._text_event("<<Undo>>"))
        self.context_menu.add_command(label="Refazer", accelerator="Ctrl+Y", command=lambda: self._text_event("<<Redo>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Recortar", accelerator="Ctrl+X", command=lambda: self._text_event("<<Cut>>"))
        self.context_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self._text_event("<<Copy>>"))
        self.context_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self._text_event("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Selecionar tudo", accelerator="Ctrl+A", command=lambda: self._text_event("<<SelectAll>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Alternar edição/visualização", accelerator="Ctrl+E", command=self.toggle_mode)
        self.textbox.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _text_event(self, event_name: str):
        try:
            self.textbox._textbox.event_generate(event_name)
        except tk.TclError:
            pass  # ex: Desfazer sem nada na pilha de undo

    def _select_theme(self, choice: str):
        self.theme_menu.set(choice)
        self._on_theme_change(choice)

    def _build_editor(self):
        self.editor_container = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_container.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 8))

        self.textbox = ctk.CTkTextbox(self.editor_container, wrap="word", font=("Consolas", 13), undo=True)
        self.textbox.pack(side="top", fill="both", expand=True)
        self.textbox.bind("<<Modified>>", self._on_modified)

        self.preview = HtmlFrame(
            self.editor_container,
            messages_enabled=False,
            javascript_enabled=False,
            on_link_click=self._on_preview_link_click,
        )

        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-e>", lambda e: self.toggle_mode())

    def toggle_mode(self):
        if self.mode == "edit":
            self._show_preview()
        else:
            self._show_editor()

    def _show_preview(self):
        self._render_preview()
        self.textbox.pack_forget()
        self.preview.pack(side="top", fill="both", expand=True)
        self.mode = "preview"
        self.mode_button.configure(text="Editar", image=self._icon_edit)

    def _show_editor(self):
        self.preview.pack_forget()
        self.textbox.pack(side="top", fill="both", expand=True)
        self.mode = "edit"
        self.mode_button.configure(text="Visualizar", image=self._icon_preview)
        self.textbox.focus_set()

    def _refresh_preview_if_active(self):
        if self.mode == "preview":
            self._render_preview()

    def _on_preview_link_click(self, url: str):
        # Sem este callback o default do tkinterweb é load_url: o próprio widget
        # navega e tenta renderizar a página externa dentro do preview.
        if url.startswith(("http://", "https://")):
            webbrowser.open(url)

    def _on_theme_change(self, choice: str):
        modes = {"Sistema": "system", "Claro": "light", "Escuro": "dark"}
        ctk.set_appearance_mode(modes[choice])
        self._refresh_preview_if_active()

    def _render_preview(self):
        content = self.textbox.get("1.0", "end-1c")
        body = markdown.markdown(content, extensions=MARKDOWN_EXTENSIONS)
        style = build_preview_style(ctk.get_appearance_mode())
        self.preview.load_html(f"<style>{style}</style>{body}")

    def _on_modified(self, _event=None):
        widget = self.textbox._textbox
        if widget.edit_modified():
            self.dirty = True
            self._update_title()
            widget.edit_modified(False)

    def _update_title(self):
        name = os.path.abspath(self.current_path) if self.current_path else "sem título"
        marker = "*" if self.dirty else ""
        self.title(f"{marker}{name} — {APP_TITLE}")

    def _confirm_discard_changes(self) -> bool:
        if not self.dirty:
            return True
        return messagebox.askyesno(
            APP_TITLE, "Há alterações não salvas. Deseja descartá-las?"
        )

    def _set_content(self, content: str):
        self.textbox.delete("1.0", "end")
        if content:
            self.textbox.insert("1.0", content)
        widget = self.textbox._textbox
        # delete/insert programáticos também disparam <<Modified>>, e o evento é
        # processado depois deste método — sem zerar o flag aqui, todo arquivo
        # recém-aberto nasceria marcado como modificado (asterisco no título).
        widget.edit_modified(False)
        widget.edit_reset()

    def new_file(self):
        if not self._confirm_discard_changes():
            return
        self._set_content("")
        self.current_path = None
        self.dirty = False
        self._update_title()
        self._refresh_preview_if_active()

    def open_file(self):
        if not self._confirm_discard_changes():
            return
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if not path:
            return
        self.load_file(path)

    def load_file(self, path: str):
        try:
            content = read_text(path)
        except OSError as exc:
            messagebox.showerror(APP_TITLE, f"Não foi possível abrir o arquivo:\n{exc}")
            return
        self._set_content(content)
        self.current_path = path
        self.dirty = False
        self._update_title()
        self._refresh_preview_if_active()

    def save_file(self):
        if self.current_path is None:
            self.save_file_as()
            return
        self._write_to(self.current_path)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=FILETYPES)
        if not path:
            return
        self._write_to(path)

    def _write_to(self, path: str):
        content = self.textbox.get("1.0", "end-1c")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as exc:
            messagebox.showerror(APP_TITLE, f"Não foi possível salvar o arquivo:\n{exc}")
            return
        self.current_path = path
        self.dirty = False
        self._update_title()

    def on_close(self):
        if self._confirm_discard_changes():
            self.destroy()


def main():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = MdPlusPlusApp()
    # Arquivo passado por argumento (ex: "Abrir com" do Windows / md++.exe arquivo.md)
    if len(sys.argv) > 1:
        app.load_file(sys.argv[1])
    app.mainloop()


if __name__ == "__main__":
    main()
