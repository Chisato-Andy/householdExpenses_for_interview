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

# costTypeテーブルのデータ取得
def get_cost_types():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT costType_id, costType_name FROM costType")
    cost_types = cursor.fetchall()
    cursor.close()
    connection.close()
    return cost_types


def update_expense_list(treeview, cost_types):
    # 古いデータを削除
    for item in treeview.get_children():
        treeview.delete(item)

    connection = None
    cursor = None
    try:
        # データベース接続
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = "SELECT expense_id, expense_name, costType_id FROM expense"
        cursor.execute(query)
        expense_list = cursor.fetchall()

        # ユーザー一覧を Treeview に追加
        for expense_id, expense_name, costType_id in expense_list:
            # costType_id に一致する costType_name を検索
            cost_type = next((costType_name for ct_id, costType_name in cost_types if ct_id == costType_id))
            treeview.insert("", tk.END, values=(expense_id, expense_name, cost_type))

    except mysql.connector.Error as err:
        messagebox.showerror("エラー", f"データベースエラー: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# 収支項目登録タブ作成用関数
def create_expense_tab(notebook):
    tab = ttk.Frame(notebook) #　新しいタブ作成
    notebook.add(tab, text="収支項目登録") #引数の　notebook を利用

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    # 入力欄作成
    tk.Label(tab, text="項目名:").grid(row=2, column=0, sticky="e", pady=(50, 0))
    expense_entry = tk.Entry(tab)
    expense_entry.grid(row=2, column=1, sticky="w", pady=(50, 0))

    # ラジオボタン作成
    tk.Label(tab, text="区分:").grid(row=3, column=0, sticky="e", pady=(10, 0))
    cost_types = get_cost_types()
    selected_cost_type = tk.StringVar() # 選択した値を保持する　tk.StringVar(): StringVarオブジェクトを作成
    cost_type_radios = []
    for costType_id, costType_name in cost_types:
        radio = tk.Radiobutton(tab, text=costType_name, variable=selected_cost_type, value=costType_id)
        radio.grid(row=3, column=1, sticky="w", padx=((costType_id-1)*65, 0), pady=(10, 0))
        cost_type_radios.append(radio)
    if cost_type_radios:
        cost_type_radios[0].select()

    def add_expense():
        expense = expense_entry.get()
        if not expense:
            messagebox.showerror("エラー", "収支項目を入力してください")
            return

        if len(expense) > 30:
            messagebox.showerror("エラー", "収支項目は30文字以内で入力してください")
            return

        selected_cost_type_id = selected_cost_type.get()
        if not selected_cost_type_id:
            messagebox.showerror("エラー", "コストタイプを選択してください")
            return

        connection = None
        cursor = None
        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor() # データベースにSQLクエリを実行するためのカーソルオブジェクト

            query = "INSERT INTO expense (expense_name, costType_id) VALUES (%s, %s)"
            cursor.execute(query, (expense,selected_cost_type_id))
            connection.commit()

            messagebox.showinfo("成功", f"'{expense}' を追加しました")
            expense_entry.delete(0, tk.END) #入力欄クリア
            update_expense_list(treeview, cost_types)
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    tk.Button(tab, text="登録", command=add_expense).grid(row=4, column=0, columnspan=2, pady=10)

    # ユーザ一覧
    treeview = ttk.Treeview(tab, columns=("ID", "固定費/変動費", "項目名"), show="headings")
    treeview.heading("ID", text="ID")
    treeview.heading("固定費/変動費", text="固定費/変動費")
    treeview.heading("項目名", text="項目名")
    treeview.grid(row=5, column=0, columnspan=2, pady=10)

    update_expense_list(treeview, cost_types)

    return tab
