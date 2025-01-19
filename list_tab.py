import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# データベース接続情報
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "householdexpenses"
}

def create_list_tab(notebook):
    # アイテム一覧タブ
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="詳細一覧")

    tab.columnconfigure(0, weight=1)
    tab.columnconfigure(1, weight=1)

    # 年を選択するドロップダウンを作成
    tk.Label(tab, text="年:").grid(row=3, column=0, sticky="w", padx=(100, 0), pady=(10, 0))
    current_year = datetime.now().year
    years = [str(year) for year in range(current_year - 10, current_year + 1)]  # 過去10年分を表示
    year_combobox = ttk.Combobox(tab, values=years, state="readonly")
    year_combobox.set(current_year)  # 現在の年をデフォルトに設定
    year_combobox.grid(row=3, column=0, sticky="w", padx=(130, 0), pady=(10, 0))
    # 月を選択するドロップダウンを作成
    tk.Label(tab, text="月:").grid(row=3, column=0, sticky="w", padx=(280, 0), pady=(10, 0))
    months = [str(month).zfill(2) for month in range(1, 13)]  # 1～12月
    month_combobox = ttk.Combobox(tab, values=months, state="readonly")
    month_combobox.set(datetime.now().strftime("%m"))  # 現在の月をデフォルトに設定
    month_combobox.grid(row=3, column=0, sticky="w", padx=(310, 0), pady=(10, 0))
    # ユーザー選択用プルダウン
    user_dict = {} # ユーザ名とIDの対応付け辞書
    tk.Label(tab, text="ユーザー:").grid(row=3, column=0, sticky="w", padx=(460, 0), pady=(10, 0))
    user_combobox = ttk.Combobox(tab, state="readonly")
    user_combobox.grid(row=3, column=0, sticky="w", padx=(520, 0), pady=(10, 0))
    def populate_user_combobox():
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            query = "SELECT user_id, user_name FROM user"
            cursor.execute(query)
            users = cursor.fetchall()

            # ユーザ辞書にIDと名前を登録
            for user_id, user_name in users:
                user_dict[user_name] = user_id
            # プルダウンに名前のみを表示
            user_combobox["values"] = list(user_dict.keys())
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    populate_user_combobox()

    # 詳細リスト
    tk.Label(tab, text="詳細", font=("Arial", 10)).grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="w", padx=10)
    treeview = ttk.Treeview(tab, columns=("日付", "収支区分", "費用区分", "収支項目", "支払方法", "値", "メモ"), show="headings")
    treeview.heading("日付", text="日付")
    treeview.heading("収支区分", text="収支区分")
    treeview.heading("費用区分", text="費用区分")
    treeview.heading("収支項目", text="収支区分項目")
    treeview.heading("支払方法", text="支払方法")
    treeview.heading("値", text="値")
    treeview.heading("メモ", text="メモ")
    treeview.column("日付", width=80, anchor="center")
    treeview.column("収支区分", width=80, anchor="center")
    treeview.column("費用区分", width=100, anchor="center")
    treeview.column("収支項目", width=100, anchor="center")
    treeview.column("支払方法", width=100, anchor="center")
    treeview.column("値", width=80, anchor="center")
    treeview.column("メモ", width=200, anchor="center")
    treeview.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")

    # 一時的合計リスト
    tk.Label(tab, text="合計", font=("Arial", 10)).grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="w",padx=10)
    sum_treeview = ttk.Treeview(tab, columns=("収支項目", "値"), show="headings")
    sum_treeview.heading("収支項目", text="収支項目")
    sum_treeview.heading("値", text="合計")
    sum_treeview.column("収支項目", width=150, anchor="center")
    sum_treeview.column("値", width=100, anchor="center")
    sum_treeview.grid(row=8, column=0, columnspan=2, pady=10, sticky="nsew")
    # 子リスト表示管理用
    expanded_rows = {}  # 押下された行の状態を管理

    # 月全体の合計値表示用ラベル
    month_total_label = tk.Label(tab, text="月全体の合計: ¥0", font=("Arial", 10), anchor="w")
    month_total_label.grid(row=9, column=0, columnspan=2, pady=(10, 0), sticky="w", padx=10)

    def filter_items():
        selected_year = year_combobox.get()
        selected_month = month_combobox.get()
        selected_user = user_combobox.get()

        if not selected_year or not selected_month:
            messagebox.showerror("エラー", "年と月を選択してください")
            return

        if not selected_user:
            messagebox.showerror("エラー", "ユーザーを選択してください")
            return

        # 辞書から選択されたユーザ名に対応するIDを取得
        user_id = user_dict.get(selected_user)

        for item in treeview.get_children():
            treeview.delete(item)
        for result in sum_treeview.get_children():
            sum_treeview.delete(result)

        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            # 詳細用
            list_query = """SELECT i.item_date, b.budget_type, ct.costType_name, e.expense_name, pt.paymentType_method, i.item_value, i.item_memo FROM item i
                    LEFT JOIN budget b ON i.budget_id = b.budget_id
                    LEFT JOIN expense e ON i.expense_id = e.expense_id
                    LEFT JOIN costType ct ON e.costType_id = ct.costType_id
                    LEFT JOIN paymentType pt ON i.paymentType_id = pt.paymentType_id
                    WHERE i.user_id = %s AND YEAR(i.item_date) = %s AND MONTH(i.item_date) = %s order by item_date ASC;"""
            cursor.execute(list_query, (user_id, selected_year, selected_month))
            items = cursor.fetchall()
            for item in items:
                treeview.insert("", tk.END, values=item)

            # 合計用
            sum_query = """SELECT e.expense_name, SUM(i.item_value) AS total_value 
                    FROM item i
                    LEFT JOIN expense e ON i.expense_id = e.expense_id
                    WHERE i.user_id = %s AND YEAR(i.item_date) = %s AND MONTH(i.item_date) = %s
                    GROUP BY e.expense_id order by e.expense_id asc"""
            cursor.execute(sum_query, (user_id, selected_year, selected_month))
            results = cursor.fetchall()
            for result in results:
                sum_treeview.insert("", tk.END, values=result)

             # 月全体の合計値を更新
            update_month_total(user_id, selected_year, selected_month)

        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def display_child_treeview(parent_item):
        """選択された行の真下に子リストを表示"""
        # 親アイテム情報を取得
        item_data = sum_treeview.item(parent_item)["values"] # 押下した行のデータを取得
        if not item_data:
            return
        expense_name = item_data[0]  # 収支区分

        # 年と月をドロップダウンから取得
        selected_year = year_combobox.get()
        selected_month = month_combobox.get()

        # 子リストがすでに展開されている場合は削除
        if expanded_rows.get(parent_item):
            for child_item in expanded_rows[parent_item]:
                sum_treeview.delete(child_item) # 子リストの1行ずつを削除
            del expanded_rows[parent_item] # 子リストを表示してる本リストの行情報を削除
            return

        # データベース接続
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # 支払方法ごとの合計を取得するクエリ
            payment_query = """
                SELECT pt.paymentType_method, SUM(i.item_value) AS total_value
                FROM item i
                LEFT JOIN expense e ON i.expense_id = e.expense_id
                LEFT JOIN paymentType pt ON i.paymentType_id = pt.paymentType_id
                WHERE e.expense_name = %s
                AND YEAR(i.item_date) = %s
                AND MONTH(i.item_date) = %s
                GROUP BY pt.paymentType_id
                ORDER BY pt.paymentType_id ASC;
            """
            cursor.execute(payment_query, (expense_name, selected_year, selected_month))
            payment_totals = cursor.fetchall()

            # 子リストを追加
            child_items = []
            for payment_method, total_value in payment_totals:
                child_item = sum_treeview.insert(
                    parent_item,
                    "end", # "end"は「親アイテムの最後」に挿入することを意味
                    values=(payment_method, total_value),
                    tags=("child",)
                )
                child_items.append(child_item)

            # 展開された子アイテムを記録(展開されている子リストの情報を追加)
            expanded_rows[parent_item] = child_items
            sum_treeview.tag_configure("child", background="#F0F8FF")

        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def on_row_click(event):
        """行クリック時の処理"""
        selected_item = sum_treeview.selection() # 選択されている要素を返す
        if not selected_item:
            return
        display_child_treeview(selected_item[0])

    def update_month_total(user_id, year, month):
        """月全体の合計値を計算してラベルに表示"""
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # 月全体の合計値を取得するクエリ
            total_query = """
                SELECT SUM(i.item_value) AS month_total
                FROM item i
                WHERE i.user_id = %s AND YEAR(i.item_date) = %s AND MONTH(i.item_date) = %s
            """
            cursor.execute(total_query, (user_id, year, month))
            result = cursor.fetchone()
            month_total = result[0] if result[0] else 0

            # ラベルに表示を更新
            month_total_label.config(text=f"月全体の合計: ¥{month_total:,}")
        except mysql.connector.Error as err:
            messagebox.showerror("エラー", f"データベースエラー: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    tk.Button(tab, text="検索", command=filter_items).grid(row=3, column=0, columnspan=2, padx=(630, 0), pady=(10, 0))

    # 合計欄の行が押下されたときのイベントをバインド
    sum_treeview.bind("<ButtonRelease-1>", on_row_click)

    return tab