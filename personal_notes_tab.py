import tkinter as tk
from tkinter import ttk

def create_personal_notes_tab(notebook):
    tab = ttk.Frame(notebook)  # 新しいタブ作成
    notebook.add(tab, text="personal_notes")  # "メモ" タブを追加

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    # memo書く
    label = tk.Label(tab, text="AAA", font=("Helvetica", 14), anchor="w")  # 文字列"AAA"を表示
    label.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # gridで配置

    return tab
