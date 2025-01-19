import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime

# データベース接続情報
DB_CONFIG = {
    "host": "localhost",        # データベースのホスト名
    "user": "root",             # データベースのユーザー名
    "password": "root",     # ユーザーのパスワード
    "database": "householdexpenses"    # 使用するデータベース名
}

# MySQLデータベース接続とデータ取得
def get_data(query):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

# id取得用関数
def get_selected_user_id(user_var, user_values):
    selected_user_name = user_var.get()
    for user_id, user_name in user_values:
        if user_name == selected_user_name:
            return user_id
    return None  # 一致しない場合はNoneを返す

def get_selected_expense_id(expense_var, expense_values):
    selected_expense_name = expense_var.get()
    for expense_id, expense_name in expense_values:
        if expense_name == selected_expense_name:
            return expense_id
    return None  # 一致しない場合はNoneを返す

def get_selected_payment_id(payment_type_var, payment_type_values):
    selected_payment_type_method = payment_type_var.get()
    for paymentType_id, paymentType_method in payment_type_values:
        if paymentType_method == selected_payment_type_method:
            return paymentType_id
    return None  # 一致しない場合はNoneを返す

# 収支登録タブ作成用関数
def create_item_tab(notebook):
    tab = ttk.Frame(notebook) #　新しいタブ作成
    notebook.add(tab, text="収支登録") #引数の　notebook を利用

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    # ユーザー選択
    user_var = tk.StringVar()
    tk.Label(tab, text="User:").grid(row=3, column=0, sticky="e", pady=(50, 0))
    user_values = get_data("SELECT user_id, user_name FROM user")
    user_dropdown = ttk.Combobox(tab, textvariable=user_var, values=[f"{u[1]}" for u in user_values], state="readonly")
    user_dropdown.grid(row=3, column=1, sticky="w", pady=(50, 0))

    # 日付選択
    tk.Label(tab, text="日付:").grid(row=4, column=0, sticky="e", pady=(10, 0))
    date_entry = DateEntry(tab, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern="yyyy/mm/dd")
    date_entry.grid(row=4, column=1, sticky="w", pady=(10, 0))

    # 収支区分選択
    budget_var = tk.StringVar()
    tk.Label(tab, text="収支区分:").grid(row=5, column=0, sticky="e", pady=(10, 0))
    budget_values = get_data("SELECT budget_id, budget_Type FROM budget")
    budget_radios = []
    for budget_id, budget_Type in budget_values:
        radio = tk.Radiobutton(tab, text=budget_Type, variable=budget_var, value=budget_id)
        radio.grid(row=5, column=1, sticky="w", padx=((budget_id-1)*50, 0), pady=(10, 0))
        budget_radios.append(radio)
    if budget_radios:
        budget_radios[0].select()

    # 費用区分選択
    cost_type_var = tk.StringVar()
    tk.Label(tab, text="費用区分:").grid(row=6, column=0, sticky="e", pady=(10, 0))
    cost_type_values = get_data("SELECT costType_id, costType_name FROM costType")
    cost_type_radios = []
    for costType_id, costType_name in cost_type_values:
        radio = tk.Radiobutton(tab, text=costType_name, variable=cost_type_var, value=costType_id)
        radio.grid(row=6, column=1, sticky="w", padx=((costType_id-1)*65, 0), pady=(10, 0))
        cost_type_radios.append(radio)
    if cost_type_radios:
        cost_type_radios[0].select()

    # 収支項目選択
    expense_var = tk.StringVar()
    tk.Label(tab, text="収支項目:").grid(row=7, column=0, sticky="e", pady=(10, 0))
    # 初期表示用
    initial_cost_type_id = cost_type_values[0][0] if cost_type_values else 1
    expense_origin_values = get_data("SELECT expense_id, expense_name FROM expense")
    expense_values = get_data(f"SELECT expense_id, expense_name FROM expense WHERE costType_id={initial_cost_type_id}")
    expense_dropdown = ttk.Combobox(tab, textvariable=expense_var, values=[f"{p[1]}" for p in expense_values], state="readonly")
    expense_dropdown.grid(row=7, column=1, sticky="w", pady=(10, 0))
    # 収支項目を更新する関数
    def update_expense_dropdown(*args):
        selected_cost_type = cost_type_var.get()
        updated_expense_values = get_data(f"SELECT expense_id, expense_name FROM expense WHERE costType_id={selected_cost_type}")
        expense_dropdown['values'] = [f"{p[1]}" for p in updated_expense_values]
        if updated_expense_values:
            expense_var.set(f"{updated_expense_values[0][1]}")  # 最初の項目を選択
    # 費用区分ラジオボタンの選択が変更されたときに収支項目を更新
    cost_type_var.trace("w", update_expense_dropdown)

    # 支払い方法選択
    payment_type_var = tk.StringVar()
    tk.Label(tab, text="支払方法:").grid(row=8, column=0, sticky="e", pady=(10, 0))
    payment_type_values = get_data("SELECT paymentType_id, paymentType_method FROM paymentType")
    payment_type_dropdown = ttk.Combobox(tab, textvariable=payment_type_var, values=[f"{p[1]}" for p in payment_type_values], state="readonly")
    payment_type_dropdown.grid(row=8, column=1, sticky="w", pady=(10, 0))

    # 値段入力
    tk.Label(tab, text="金額:").grid(row=9, column=0, sticky="e", pady=(10, 0))
    value_entry = tk.Entry(tab)
    value_entry.grid(row=9, column=1, sticky="w", pady=(10, 0))

    # メモ入力
    tk.Label(tab, text="Memo:").grid(row=10, column=0, sticky="e", pady=(10, 0))
    memo_entry = tk.Entry(tab, width=50)
    memo_entry.grid(row=10, column=1, sticky="w", pady=(10, 0))

    # 入力フィールドのリセット
    def reset_fields():
        user_var.set("")
        #budget_var.set("")
        expense_var.set("")
        payment_type_var.set("")
        value_entry.delete(0, tk.END)
        memo_entry.delete(0, tk.END)

    # データ登録処理
    def add_item():
        selected_user_id = get_selected_user_id(user_var, user_values)
        selected_item_date = date_entry.get()
        selected_budget_id = budget_var.get()
        selected_expense_id = get_selected_expense_id(expense_var, expense_origin_values)
        selected_payment_type_id = get_selected_payment_id(payment_type_var, payment_type_values)
        item_value = value_entry.get()
        item_memo = memo_entry.get()

        if not all([selected_user_id, selected_item_date, selected_budget_id, selected_expense_id, selected_payment_type_id, item_value]):
            messagebox.showerror("Error", "すべての項目を入力してください。")
            return

        today = datetime.today().date()
        selected_item_date_obj = datetime.strptime(selected_item_date, "%Y/%m/%d").date()
        if selected_item_date_obj > today:
            messagebox.showerror("エラー", "選択された日付は今日より未来の日付です。")
            return

        try:
            item_value = int(item_value)
        except ValueError:
            messagebox.showerror("Error", "値段は数値で入力してください。")
            return

        if len(item_memo) > 50:
            messagebox.showerror("エラー", "メモは50文字以内で入力してください")
            return

        connection = None
        cursor = None
        try:
            # データベース接続
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor() # データベースにSQLクエリを実行するためのカーソルオブジェクト

            # 収支データ登録
            query = """INSERT INTO item(user_id, item_date, budget_id, expense_id, paymentType_id, item_value, item_memo) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (selected_user_id, selected_item_date, selected_budget_id, selected_expense_id, selected_payment_type_id, item_value, item_memo))

            # 計算結果更新
            cursor.execute("SELECT user_tempValue, user_wallet FROM user WHERE user_id=%s", (selected_user_id,))
            user_data = cursor.fetchone()
            if not user_data:
                messagebox.showerror("エラー", "ユーザーが見つかりません。")
                return
            temp_value = user_data[0]
            wallet = user_data[1]
            # 一時計算結果 & 財布
            if str(selected_budget_id) == '1':
                temp_value += item_value
                if str(selected_payment_type_id) == '1':
                    wallet += item_value
            elif selected_budget_id in ('2', '3'):
                temp_value -= item_value
                if str(selected_payment_type_id) == '1':
                    wallet -= item_value
            cursor.execute("""UPDATE user SET user_tempValue=%s, user_wallet=%s WHERE user_id=%s""",(temp_value, wallet, selected_user_id))
            connection.commit()

            messagebox.showinfo("Success", "データが登録されました。")
            reset_fields()
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    tk.Button(tab, text="登録", command=add_item).grid(row=11, column=0, columnspan=2, pady=10)

    return tab