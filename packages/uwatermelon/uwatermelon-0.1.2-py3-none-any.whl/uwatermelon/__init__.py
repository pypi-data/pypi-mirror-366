# uwatermelon/__init__.py

import tkinter as tk
from tkinter import messagebox

def スタート():
    print("🍉 うぉーたーめろん スタート！")

def show_dialog(message="", icon=None):
    root = tk.Tk()
    root.withdraw()
    title = "うぉーたーめろん"
    if icon:
        title += f" [{icon}]"
    messagebox.showinfo(title, message)

def parse_script(lines):
    dialog_mode = False
    message_text = ""
    icon_text = None

    for line in lines:
        line = line.strip()
        if line == "ダイアログ":
            dialog_mode = True
            message_text = ""
            icon_text = None
        elif dialog_mode:
            if line.startswith("メッセージ "):
                message_text = line[len("メッセージ "):].strip().strip('"')
            elif line.startswith("アイコン "):
                icon_text = line[len("アイコン "):].strip().strip('"')
            elif line == "":
                # 空行は無視
                continue
            else:
                # ダイアログ終了とみなして表示
                if message_text:
                    show_dialog(message_text, icon_text)
                dialog_mode = False
                message_text = ""
                icon_text = None
        else:
            # 他コマンドなどあればここで処理可能
            pass

    # 最後のダイアログ表示
    if dialog_mode and message_text:
        show_dialog(message_text, icon_text)

def メッセージ(text):
    print(f"メッセージ：{text}")

def ネット(url):
    import webbrowser
    webbrowser.open(url)

def 繰り返し(count, func):
    for _ in range(count):
        func()
