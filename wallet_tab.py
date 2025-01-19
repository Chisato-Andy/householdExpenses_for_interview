import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

# データベース接続情報
DB_CONFIG = {
    "host": "localhost",        # データベースのホスト名
    "user": "root",             # データベースのユーザー名
    "password": "root",     # ユーザーのパスワード
    "database": "householdexpenses"    # 使用するデータベース名
}

# 一覧タブ作成用関数
def create_wallet_tab(notebook):
    tab = ttk.Frame(notebook)  # 新しいタブ作成
    notebook.add(tab, text="お財布")  # 引数の　notebook を利用

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    treeview = ttk.Treeview(tab, columns=("ユーザー名", "現状収支", "財布"), show="headings")
    treeview.heading("ユーザー名", text="ユーザー名")
    treeview.heading("現状収支", text="現状収支")
    treeview.heading("財布", text="財布")
    treeview.column("ユーザー名", width=80, anchor="center")
    treeview.column("現状収支", width=100, anchor="center")
    treeview.column("財布", width=100, anchor="center")
    treeview.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

    def update_user_list():
        for item in treeview.get_children():
            treeview.delete(item)

        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            query = "SELECT user_name, user_tempValue, user_wallet FROM user"
            cursor.execute(query)
            users = cursor.fetchall()

            for user in users:
                treeview.insert("", tk.END, values=user)
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    tk.Button(tab, text="更新", command=update_user_list).grid(row=5, column=0, columnspan=2, pady=10)

    update_user_list()
    return tab