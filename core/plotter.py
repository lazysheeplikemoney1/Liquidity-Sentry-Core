import mplfinance as mpf
import matplotlib

# ⚠️ 关键：强制后台模式，防止在无显示器的服务器上报错
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as patches
import matplotlib.lines as mlines
import io
import os
import time

# 假设 config.py 在上一级目录，或者你需要根据实际路径调整导入
# 这里为了模块独立性，我把字体加载逻辑内置在 plotter 里，
# 但最好的做法是从 config 导入路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_CN_PATH = os.path.join(BASE_DIR, 'assets', 'simhei.ttf')
FONT_EN_PATH = os.path.join(BASE_DIR, 'assets', 'consola.ttf')


# --- 资源预加载 (只加载一次，提升性能) ---
def load_fonts():
    f_cn = fm.FontProperties(fname=FONT_CN_PATH, size=22, weight='bold') if os.path.exists(FONT_CN_PATH) else None
    f_en = fm.FontProperties(fname=FONT_EN_PATH, size=12) if os.path.exists(FONT_EN_PATH) else None
    f_en_bold = fm.FontProperties(fname=FONT_EN_PATH, size=12, weight='bold') if os.path.exists(FONT_EN_PATH) else None
    f_watermark = fm.FontProperties(fname=FONT_EN_PATH, size=70, weight='bold') if os.path.exists(
        FONT_EN_PATH) else None
    return f_cn, f_en, f_en_bold, f_watermark


FONT_CN, FONT_EN, FONT_EN_BOLD, FONT_WATERMARK = load_fonts()


def generate_chart(df, symbol, title, status, color, vol_ratio, price):
    """
    核心绘图函数
    :param df: 包含 OHLCV 数据的 DataFrame
    :param symbol: 币种名称 (e.g. BTC/USDT)
    :param title: 标题文案
    :param status: 状态文案 (e.g. STRONG BUY)
    :param color: 信号颜色 (Hex)
    :param vol_ratio: 量比数值
    :param price: 当前价格
    :return: BytesIO 对象 (图片的内存二进制流)
    """
    try:
        # --- 🛡️ 新增：数据完整性校验 ---
        # 1. 检查是否为空
        if df is None or df.empty:
            print(f"⚠️ {symbol} 绘图数据为空，跳过")
            return None

        # 2. 检查必须的列是否存在 (防止 KeyError: 'high')
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"⚠️ {symbol} 数据格式错误，缺少列: {df.columns}")
            return None

        # 3. 检查数据长度 (太短画不出图)
        if len(df) < 10:
            print(f"⚠️ {symbol} K线数据不足 ({len(df)}根)，跳过")
            return None

        # 1. 数据准备
        plot_df = df.tail(35)  # 只画最后 35 根，保证视觉冲击力
        max_val = plot_df['high'].max()
        min_val = plot_df['low'].min()

        # 辅助线配置
        lines_config = dict(
            hlines=[max_val, min_val, price],
            colors=['#FF3030', '#00FF7F', 'white'],  # 阻力红，支撑绿，现价白
            linestyle=['--', '--', '-'],
            linewidths=[0.8, 0.8, 0.8],
            alpha=0.8
        )

        # 2. 样式配置 (无边框黑客风)
        my_style = mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            marketcolors=mpf.make_marketcolors(
                up='#00FF7F', down='#FF3030',  # 霓虹红绿
                edge='inherit', wick='inherit', volume='in'
            ),
            gridstyle=':', gridcolor='#1A1A1A',
            facecolor='#050505',  # 极深黑背景
            rc={
                'axes.spines.top': False, 'axes.spines.right': False,
                'axes.spines.left': False, 'axes.spines.bottom': True,  # 只留底边
                'axes.edgecolor': '#333333',
                'xtick.color': '#555555', 'ytick.color': '#555555',
                'axes.labelcolor': '#555555',
                'font.family': 'Consolas'  # 强制坐标轴用等宽字体
            }
        )

        # 3. 创建画布与布局
        fig = mpf.figure(style=my_style, figsize=(16, 9))
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
        # 压缩顶部空间，给 HUD 留位
        fig.subplots_adjust(top=0.82, bottom=0.05, hspace=0)

        # 4. 绘制 K 线与成交量
        mpf.plot(
            plot_df, type='candle', ax=ax1, volume=ax2,
            hlines=lines_config, style=my_style,
            datetime_format='%H:%M',
            scale_width_adjustment=dict(volume=0.6, candle=1.2),  # 加粗 K 线
            show_nontrading=False,
            xrotation=0  # 时间轴水平显示
        )

        # --- 5. 绘制 HUD (Head-Up Display) ---

        # A. 侧边状态条 (极细激光线)
        rect = patches.Rectangle((0, 0), 0.005, 1, transform=fig.transFigure,
                                 facecolor=color, edgecolor='none', zorder=10)
        fig.add_artist(rect)

        if FONT_CN and FONT_EN_BOLD:
            # B. 标题区
            fig.text(0.03, 0.92, "EVENT | ", fontproperties=FONT_EN_BOLD,
                     ha='left', va='center', color='#666666', fontsize=16)
            # 标题内容 (支持中文)
            fig.text(0.10, 0.92, title, fontproperties=FONT_CN,
                     ha='left', va='center', color='white', fontsize=22)

            # C. 数据仪表盘
            y_data = 0.86
            # Signal
            fig.text(0.03, y_data, "STATUS:", fontproperties=FONT_EN_BOLD, color='#666666', fontsize=12)
            fig.text(0.08, y_data, status, fontproperties=FONT_EN_BOLD, color=color, fontsize=16)
            # Vol Ratio
            fig.text(0.20, y_data, "VOL_DEV:", fontproperties=FONT_EN_BOLD, color='#666666', fontsize=12)
            fig.text(0.26, y_data, f"{vol_ratio:.2f}x", fontproperties=FONT_EN_BOLD, color=color, fontsize=16)
            # Price
            fig.text(0.34, y_data, "PRICE:", fontproperties=FONT_EN_BOLD, color='#666666', fontsize=12)
            fig.text(0.39, y_data, f"{price}", fontproperties=FONT_EN_BOLD, color='white', fontsize=16)

            # D. 页脚元数据
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            brand_text = "ALPHA RADAR | @LiquidityEye | SOURCE: BINANCE FUTURES"
            fig.text(0.98, 0.01, f"{brand_text} | {current_time} UTC", fontproperties=FONT_EN,
                     ha='right', va='bottom', color='#444444', fontsize=10)

        # E. 分割线 (隐形灰)
        line = mlines.Line2D([0, 1], [0.82, 0.82], transform=fig.transFigure,
                             color='#1A1A1A', linewidth=0.5)
        fig.add_artist(line)

        # F. 价格标签 (右侧高亮箭头)
        ax1.annotate(f'{price}', xy=(len(plot_df) - 1, price), xytext=(len(plot_df) + 1, price),
                     color='white', fontsize=11, weight='bold', fontproperties=FONT_EN_BOLD,
                     arrowprops=dict(facecolor=color, shrink=0.05, headwidth=6, headlength=6),
                     bbox=dict(boxstyle="square,pad=0.3", fc=color, ec="none", alpha=1.0))

        # G. 战术标记 (支撑/压力)
        ax1.text(0.01, max_val, f"RES: {max_val}", color='#FF3030', fontsize=8, va='bottom', fontproperties=FONT_EN)
        ax1.text(0.01, min_val, f"SUP: {min_val}", color='#00FF7F', fontsize=8, va='top', fontproperties=FONT_EN)

        # H. 背景水印
        if FONT_WATERMARK:
            # 确定水印文案
            wm_text = "ACCUMULATION" if "BUY" in status else "DISTRIBUTION"
            if "WEAK" in status: wm_text = "LOW LIQUIDITY"

            ax1.text(0.5, 0.55, wm_text, transform=ax1.transAxes,
                     color=color, alpha=0.05,  # 极淡
                     ha='center', va='center', rotation=0,
                     fontproperties=FONT_WATERMARK)

        # 6. 保存到内存
        buf = io.BytesIO()
        # --- 🔴 错误代码 (导致你报错的那行) ---
        # plt.savefig(buf, format='jpg', dpi=120, bbox_inches='tight', facecolor='#050505', quality=80)

        # --- 🟢 修正代码 (删掉了 quality 参数) ---
        try:
            fig.patch.set_facecolor('#050505')

            # ⚠️ 关键修改：只保留核心参数，删掉 quality
            plt.savefig(buf, format='jpg', dpi=120, bbox_inches='tight', facecolor='#050505')

            buf.seek(0)
        except Exception as e:
            print(f"❌ 绘图失败: {e}")
            return None
        finally:
            plt.close(fig)
            plt.close('all')

        return buf

    except Exception as e:
        print(f"❌ 绘图模块报错: {e}")
        return None