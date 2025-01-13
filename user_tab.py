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

# ユーザー登録タブ作成用関数
def create_user_tab(notebook):
    tab = ttk.Frame(notebook) #　新しいタブ作成
    notebook.add(tab, text="ユーザー登録") #引数の　notebook を利用

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)
    tk.Label(tab, text="ユーザー名:").grid(row=2, column=0, sticky="e", pady=(50, 0))
    user_entry = tk.Entry(tab) #　入力欄作成
    user_entry.grid(row=2, column=1, sticky="w", pady=(50, 0))

    def add_user():
        user = user_entry.get()
        if not user:
            messagebox.showerror("エラー", "ユーザー名を入力してください")
            return

        if len(user) > 30:
            messagebox.showerror("エラー", "ユーザー名は30文字以内で入力してください")
            return

        connection = None
        cursor = None
        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor() # データベースにSQLクエリを実行するためのカーソルオブジェクト

            query = "INSERT INTO user (user_name) VALUES (%s)"
            cursor.execute(query, (user,)) # (user,): タプル 複数の値を一つの変数に格納するためのデータ構造
            connection.commit()

            messagebox.showinfo("成功", f"'{user}' をユーザーとして追加しました")
            user_entry.delete(0, tk.END) #入力欄クリア
            update_user_list()
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    tk.Button(tab, text="ユーザー登録", command=add_user).grid(row=3, column=0, columnspan=2, pady=10)

    # ユーザ一覧
    treeview = ttk.Treeview(tab, columns=("ID", "ユーザー名"), show="headings")
    treeview.heading("ID", text="ID")
    treeview.heading("ユーザー名", text="ユーザー名")
    treeview.column("ID", width=100, anchor="center")
    treeview.column("ユーザー名", width=150, anchor="center")
    treeview.grid(row=4, column=0, columnspan=2, pady=10)

    def update_user_list():
        # 古いデータを削除
        for item in treeview.get_children():
            treeview.delete(item)

        connection = None
        cursor = None
        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            query = "SELECT user_id, user_name FROM user"
            cursor.execute(query)
            users = cursor.fetchall()

            # ユーザー一覧を Treeview に追加
            for user in users:
                treeview.insert("", tk.END, values=user)

        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    update_user_list()

    return tab
