import aiohttp
from config import TG_BOT_TOKEN, TG_CHAT_ID, PROXY


async def send_alert_async(image_buf, symbol, status, vol_ratio, price):
    """ 异步发送 Telegram 消息 """
    clean_ticker = symbol.upper().replace('USDT', '')
    emoji = "🟢" if "BUY" in status else "🔴"

    caption = f"""
{emoji} <b>WHALE ALERT: #{clean_ticker}</b>

<b>SIGNAL:</b> {status}
<b>VOL DEV:</b> <b>{vol_ratio:.2f}x</b> (Real-time)
<b>PRICE:</b> {price}

———————————
👉 <a href="https://www.binance.com/en/futures/{clean_ticker}USDT">Trade on Binance</a>
    """

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"

    # 重置指针
    image_buf.seek(0)

    # 构造异步表单
    data = aiohttp.FormData()
    data.add_field('chat_id', TG_CHAT_ID)
    data.add_field('caption', caption)
    data.add_field('parse_mode', 'HTML')
    data.add_field('photo', image_buf, filename='alert.jpg', content_type='image/jpeg')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, proxy=PROXY) as resp:
                if resp.status == 200:
                    print(f"✅ TG 推送成功: {clean_ticker}")
                else:
                    print(f"❌ TG 推送失败: {await resp.text()}")
    except Exception as e:
        print(f"❌ 网络错误: {e}")