import os

# --- 网络配置 ---
PROXY = "http://127.0.0.1:7897" # 注意：异步库通常只需要字符串格式
WS_URL = "wss://fstream.binance.com/stream?streams=" # 币安合约 WS 地址

# --- 策略阈值 ---
VOL_THRESHOLD = 2.0
CHANGE_THRESHOLD = 0.2

# --- 目标池 (这些是初始目标，后续可动态更新) ---
WATCH_LIST = [
    'btcusdt', 'ethusdt', 'solusdt',
    'dogeusdt', 'pepeusdt', 'xrpusdt'
]

# Telegram
TG_BOT_TOKEN = "8423267931:AAH9xFrjvcOxMbQX4SmOtpj6PGr00j6-CW4"
TG_CHAT_ID = "@WhaleSentry_AI"

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_CN = os.path.join(BASE_DIR, 'assets', 'simhei.ttf')
FONT_EN = os.path.join(BASE_DIR, 'assets', 'consola.ttf')