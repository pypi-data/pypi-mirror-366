# uwatermelon/__init__.py

def スタート():
    print("🍉 うぉーたーめろん スタート！")

def ダイアログ(アイコン=None):
    if アイコン:
        print(f"（ダイアログ表示 - アイコン: {アイコン}）")
    else:
        print("（ダイアログ表示）")

def メッセージ(text):
    print(f"メッセージ：{text}")

def ネット(url):
    print(f"ネット画面を表示: {url}")

def 繰り返し(count, func):
    for _ in range(count):
        func()
