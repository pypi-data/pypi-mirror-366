import tkinter as tk
from tkinter import messagebox

_モード = {"ダイアログ": False}

def ダイアログ():
    _モード["ダイアログ"] = True

def メッセージ(内容):
    if _モード.get("ダイアログ", False):
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("うぉーたーめろん", 内容)
    else:
        print(内容)