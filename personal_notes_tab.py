import tkinter as tk
from tkinter import ttk

def create_personal_notes_tab(notebook):
    tab = ttk.Frame(notebook)  # 新しいタブ作成
    notebook.add(tab, text="personal_notes")  # "メモ" タブを追加

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    text_widget = tk.Text(tab, wrap="word", font=("Helvetica", 12), bg="gray94", relief="flat", state="normal",  width=80, height=50)
    text_widget.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # マークダウンファイルを読み込んで表示する関数
    def load_markdown_file():
        filepath = "./memo/personal_memo.md"  # 同じ階層にあるファイル名を指定
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                md_content = file.read()
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, md_content)
                text_widget.config(state="disabled")
        except FileNotFoundError:
            text_widget.insert(tk.END, "Error: 'personal_memo.md' file not found.")

    # 起動時にマークダウンファイルをロード
    load_markdown_file()

    return tab
