import tkinter as tk
from tkinter import ttk
from item_tab import create_item_tab
from wallet_tab import create_wallet_tab
from list_tab import create_list_tab
from expense_tab import create_expense_tab
from payment_tab import create_payment_tab
from personal_notes_tab import create_personal_notes_tab
from shared_notes_tab import create_shared_notes_tab
from user_tab import create_user_tab

def main():
    # メインウィンドウの作成
    root = tk.Tk()
    root.title("家計簿")
    root.geometry("800x600")

    # Notebookウィジェット（タブの作成）
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # 各タブを作成
    create_item_tab(notebook)
    create_wallet_tab(notebook)
    create_list_tab(notebook)
    create_expense_tab(notebook)
    create_payment_tab(notebook)
    create_personal_notes_tab(notebook)
    create_shared_notes_tab(notebook)
    create_user_tab(notebook)

    # メインループ
    root.mainloop()

if __name__ == "__main__":
    main()
