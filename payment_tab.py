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

# 支払方法追加タブ作成用関数
def create_payment_tab(notebook):
    tab = ttk.Frame(notebook) #　新しいタブ作成
    notebook.add(tab, text="支払方法追加") #引数の　notebook を利用

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)
    tk.Label(tab, text="支払方法:").grid(row=2, column=0, sticky="e", pady=(50, 0))
    payment_entry = tk.Entry(tab) #　入力欄作成
    payment_entry.grid(row=2, column=1, sticky="w", pady=(50, 0))

    def add_payment():
        payment = payment_entry.get()
        if not payment:
            messagebox.showerror("エラー", "支払方法を入力してください")
            return

        if len(payment) > 10:
            messagebox.showerror("エラー", "支払方法は10文字以内で入力してください")
            return

        connection = None
        cursor = None

        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor() # データベースにSQLクエリを実行するためのカーソルオブジェクト

            query = "INSERT INTO paymentType (paymentType_method) VALUES (%s)"
            cursor.execute(query, (payment,))
            connection.commit()

            messagebox.showinfo("成功", f"'{payment}' を追加しました")
            payment_entry.delete(0, tk.END) #入力欄クリア
            update_payment_list()
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    tk.Button(tab, text="支払追加", command=add_payment).grid(row=3, column=0, columnspan=2, pady=10)

    # ユーザ一覧
    treeview = ttk.Treeview(tab, columns=("ID", "支払方法"), show="headings")
    treeview.heading("ID", text="ID")
    treeview.heading("支払方法", text="支払方法")
    treeview.grid(row=4, column=0, columnspan=2, pady=10)

    def update_payment_list():
        # 古いデータを削除
        for item in treeview.get_children():
            treeview.delete(item)

        connection = None
        cursor = None
        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            query = "SELECT paymentType_id, paymentType_method FROM paymentType"
            cursor.execute(query)
            payment_list = cursor.fetchall()

            # ユーザー一覧を Treeview に追加
            for payment in payment_list:
                treeview.insert("", tk.END, values=payment)

        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    update_payment_list()

    return tab
