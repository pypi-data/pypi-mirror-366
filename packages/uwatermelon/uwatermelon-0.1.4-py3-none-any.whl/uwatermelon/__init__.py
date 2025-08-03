import os
import platform
import webbrowser
import threading
from flask import Flask, render_template
from tkinter import messagebox, Tk

# ダイアログ表示
def ダイアログ(メッセージ内容: str):
    ウィンドウ = Tk()
    ウィンドウ.withdraw()
    messagebox.showinfo("ダイアログ", メッセージ内容)
    ウィンドウ.destroy()

# ダイアログアイコン
def ダイアログアイコン(種類: str, メッセージ内容: str):
    ウィンドウ = Tk()
    ウィンドウ.withdraw()
    種類 = 種類.strip()
    if 種類 == "警告":
        messagebox.showwarning("警告", メッセージ内容)
    elif 種類 == "エラー":
        messagebox.showerror("エラー", メッセージ内容)
    elif 種類 == "注意":
        messagebox.showinfo("注意", メッセージ内容)
    elif 種類 == "情報":
        messagebox.showinfo("情報", メッセージ内容)
    elif 種類 == "管理者":
        messagebox.showinfo("管理者", メッセージ内容)
    else:
        messagebox.showinfo("ダイアログ", メッセージ内容)
    ウィンドウ.destroy()

# OS判断
def 判断(名前: str):
    現在のOS = platform.system()
    if "Windows" in 現在のOS:
        ダイアログ(f"{名前} は Windows です")
    elif "Linux" in 現在のOS:
        ダイアログ(f"{名前} は Linux です")
    elif "Darwin" in 現在のOS:
        ダイアログ(f"{名前} は macOS です")
    else:
        ダイアログ(f"{名前} は不明なシステムです")

# Flaskサーバー設定
アプリ = Flask(__name__, template_folder="テンプレ")

@アプリ.route("/")
def ホーム():
    return render_template("ホーム.html")

def サーバースタート(ポート: str):
    def 実行():
        アプリ.run(port=int(ポート), debug=False)
    threading.Thread(target=実行, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{ポート}")

# スタート関数
def スタート(関数):
    関数()

# 終了関数
def 終了():
    exit()
