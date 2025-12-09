import ccxt.async_support as ccxt  # 异步版 CCXT
import pandas as pd
import websockets
import json
import asyncio
from config import PROXY


class AsyncDataFetcher:
    def __init__(self):
        # 初始化异步交易所实例
        self.exchange = ccxt.binance({
            'proxies': {'http': PROXY, 'https': PROXY},
            'timeout': 30000,
            'enableRateLimit': False,  # WS模式下不需要限制HTTP频率
            'options': {'defaultType': 'future'}
        })
        self.history_cache = {}  # 用于绘图的历史 K 线缓存
        self.baseline_volume = {}  # 用于计算量比的基准

    async def close(self):
        await self.exchange.close()

    async def init_baseline(self, watchlist):
        """ 预热：拉取历史数据，建立基准 """
        print("🔥 [系统预热] 正在拉取历史 K 线...")
        tasks = [self._fetch_single_history(symbol) for symbol in watchlist]
        await asyncio.gather(*tasks)
        print("✅ 预热完成，基准线已建立。")

    async def _fetch_single_history(self, symbol):
        try:
            # 这里的 symbol 需要是大写带斜杠 (BTC/USDT)
            std_symbol = symbol.upper().replace('USDT', '/USDT')
            ohlcv = await self.exchange.fetch_ohlcv(std_symbol, '1m', limit=100)
            if not ohlcv: return

            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            df['ts'] = pd.to_datetime(df['ts'], unit='ms') + pd.Timedelta(hours=8)
            df.set_index('ts', inplace=True)

            # 存入缓存
            self.history_cache[symbol] = df
            self.baseline_volume[symbol] = df['v'].mean()
        except Exception as e:
            print(f"❌ 初始化失败 {symbol}: {e}")

    async def start_stream(self, watchlist, callback):
        """ 启动 WebSocket 监听 """
        # 构造订阅流: btcusdt@kline_1m
        streams = "/".join([f"{s.lower()}@kline_1m" for s in watchlist])
        url = f"wss://fstream.binance.com/stream?streams={streams}"

        print(f"🦅 连接全网资金流: {url} ...")

        async with websockets.connect(url) as ws:
            print("✅ WebSocket 连接成功！正在监听市场心跳...")
            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # 收到数据后，立刻调用回调函数处理
                    await callback(data)
                except Exception as e:
                    print(f"⚠️ 流中断: {e}")
                    break