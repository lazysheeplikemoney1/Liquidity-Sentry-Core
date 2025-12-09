import asyncio
import time
import os
from functools import partial

# 引入模块
from config import WATCH_LIST, VOL_THRESHOLD, CHANGE_THRESHOLD
from core.data_fetcher import AsyncDataFetcher
from core.plotter import generate_chart
from core.notifier import send_alert_async

# 冷却池
ALERT_COOLDOWN = {}


class AlphaCommander:
    def __init__(self):
        self.fetcher = AsyncDataFetcher()

    async def handle_stream_message(self, msg):
        """ 处理每一条 WS 推送过来的数据 """
        # 解析数据
        if 'data' not in msg: return
        data = msg['data']
        k = data['k']
        symbol = data['s'].lower()  # 交易对

        # 实时数据
        current_vol = float(k['v'])
        close_price = float(k['c'])
        open_price = float(k['o'])

        # 1. 拿到基准均量
        avg_vol = self.fetcher.baseline_volume.get(symbol, 0)
        if avg_vol == 0: return  # 尚未预热完成或死币

        # 2. 计算指标
        vol_ratio = current_vol / avg_vol
        change_pct = (close_price - open_price) / open_price * 100

        # 3. 触发判定
        signal_tier = None
        if vol_ratio > VOL_THRESHOLD:
            signal_tier = 'S'  # 简化逻辑，过阈值就是干

        # 必须有波动才报警
        if signal_tier and abs(change_pct) > CHANGE_THRESHOLD:
            # 冷却检查 (60s)
            now = time.time()
            if now - ALERT_COOLDOWN.get(symbol, 0) < 60: return

            print(f"\n🚀 [秒级捕获] {symbol.upper()} | Vol: {vol_ratio:.2f}x | Chg: {change_pct:.2f}%")

            # 更新冷却
            ALERT_COOLDOWN[symbol] = now

            # 4. 执行绘图 + 推送
            # ⚠️ 关键：这里不能阻塞！要开一个 Task 去做后台任务
            asyncio.create_task(self.execute_alert_pipeline(symbol, change_pct, vol_ratio, close_price))

    async def execute_alert_pipeline(self, symbol, change_pct, vol_ratio, price):
        """ 后台流水线：画图 -> 推送 """
        try:
            # 准备绘图数据 (把当前这根没走完的K线拼接到历史里，画出最新状态)
            hist_df = self.fetcher.history_cache.get(symbol).copy()
            # ... (此处省略拼接最后一行数据的逻辑，直接用历史数据画也可以，误差不大) ...

            direction = "PUMP" if change_pct > 0 else "DUMP"
            status = "STRONG BUY" if change_pct > 0 else "PANIC SELL"
            color = "#00FF7F" if change_pct > 0 else "#FF3030"
            title = f"WHALE ALERT: {symbol.upper()}"

            # ⚠️ 关键：绘图是 CPU 密集型，必须扔到线程池，否则会卡死 WS 心跳！
            loop = asyncio.get_running_loop()
            # 使用 partial 包装参数
            p_func = partial(generate_chart, hist_df, symbol.upper(), title, status, color, vol_ratio, price)

            print(f"🎨 正在后台绘制 {symbol} ...")
            # run_in_executor(None) 默认使用 ThreadPool
            img_buf = await loop.run_in_executor(None, p_func)

            if img_buf:
                # 异步推送
                await send_alert_async(img_buf, symbol, status, vol_ratio, price)

        except Exception as e:
            print(f"❌ 流水线报错: {e}")

    async def run(self):
        print(f"🦅 ALPHA SENTRY [ASYNC CORE] 启动 | PID: {os.getpid()}")

        try:
            # 1. 初始化数据
            await self.fetcher.init_baseline(WATCH_LIST)

            # 2. 启动 WS 监听
            await self.fetcher.start_stream(WATCH_LIST, self.handle_stream_message)

        except KeyboardInterrupt:
            print("🛑 停止运行")
        finally:
            await self.fetcher.close()


if __name__ == "__main__":
    commander = AlphaCommander()
    asyncio.run(commander.run())