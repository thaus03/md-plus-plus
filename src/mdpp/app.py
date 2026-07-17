import os
from tkinter import filedialog, messagebox

import customtkinter as ctk
import markdown
from tkhtmlview import HTMLScrolledText

APP_TITLE = "md++"
FILETYPES = [("Markdown", "*.md *.markdown"), ("Todos os arquivos", "*.*")]
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "sane_lists"]


class MdPlusPlusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_path: str | None = None
        self.dirty = False
        self.mode = "edit"  # "edit" | "preview"

        self.title(APP_TITLE)
        self.geometry("900x650")

        self._build_menu()
        self._build_editor()
        self._update_title()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_menu(self):
        toolbar = ctk.CTkFrame(self, height=36)
        toolbar.pack(side="top", fill="x")

        ctk.CTkButton(toolbar, text="Abrir", width=90, command=self.open_file).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(toolbar, text="Salvar", width=90, command=self.save_file).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(toolbar, text="Salvar como", width=110, command=self.save_file_as).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(toolbar, text="Novo", width=90, command=self.new_file).pack(side="left", padx=4, pady=4)

        self.mode_button = ctk.CTkButton(toolbar, text="Visualizar", width=100, command=self.toggle_mode)
        self.mode_button.pack(side="left", padx=4, pady=4)

    def _build_editor(self):
        self.editor_container = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_container.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 8))

        self.textbox = ctk.CTkTextbox(self.editor_container, wrap="word", font=("Consolas", 13))
        self.textbox.pack(side="top", fill="both", expand=True)
        self.textbox.bind("<<Modified>>", self._on_modified)

        self.preview = HTMLScrolledText(self.editor_container, html="")

        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-n>", lambda e: self.new_file())

    def toggle_mode(self):
        if self.mode == "edit":
            self._show_preview()
        else:
            self._show_editor()

    def _show_preview(self):
        content = self.textbox.get("1.0", "end-1c")
        html = markdown.markdown(content, extensions=MARKDOWN_EXTENSIONS)
        self.preview.set_html(html)
        self.textbox.pack_forget()
        self.preview.pack(side="top", fill="both", expand=True)
        self.mode = "preview"
        self.mode_button.configure(text="Editar")

    def _show_editor(self):
        self.preview.pack_forget()
        self.textbox.pack(side="top", fill="both", expand=True)
        self.mode = "edit"
        self.mode_button.configure(text="Visualizar")
        self.textbox.focus_set()

    def _refresh_preview_if_active(self):
        if self.mode == "preview":
            content = self.textbox.get("1.0", "end-1c")
            html = markdown.markdown(content, extensions=MARKDOWN_EXTENSIONS)
            self.preview.set_html(html)

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

    def new_file(self):
        if not self._confirm_discard_changes():
            return
        self.textbox.delete("1.0", "end")
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
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)
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
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
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
    app.mainloop()


if __name__ == "__main__":
    main()
