import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import time

def update_incremental_data(tickers, folder="data"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    today = datetime.now().strftime('%Y-%m-%d')
    success_count = 0
    
    for ticker in tickers:
        file_path = os.path.join(folder, f"{ticker}.csv")
        
        try:
            # --- 核心数据获取逻辑 ---
            if os.path.exists(file_path):
                # 1. 读取旧数据
                existing_df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                
                # 【修复步骤 A】: 确保旧数据列名干净 (首字母大写)
                existing_df.columns = [c.capitalize() for c in existing_df.columns]
                
                if not existing_df.empty:
                    last_date = existing_df.index[-1]
                    start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
                    
                    if start_date >= today:
                        print(f"✅ {ticker} 已经是最新，跳过。")
                        continue
                    
                    print(f"⏳ {ticker} 正在增量更新: {start_date} 至 {today}")
                    # 下载新数据
                    new_data = yf.download(ticker, start=start_date, progress=False, threads=False)
                else:
                    # 文件存在但为空，重新全量下载
                    new_data = yf.download(ticker, period="1y", progress=False, threads=False)
            else:
                # 2. 本地无数据，全量下载
                print(f"🆕 {ticker} 本地无数据，正在执行全量下载...")
                new_data = yf.download(ticker, period="1y", progress=False, threads=False)

            # --- 【核心修复步骤 B】：清洗新数据的列名 ---
            if not new_data.empty:
                # 1. 处理 MultiIndex (去除股票代码层级)
                # 如果列名是 ('Close', 'MSTR') 这种格式，只保留 'Close'
                if isinstance(new_data.columns, pd.MultiIndex):
                    new_data.columns = new_data.columns.get_level_values(0)
                
                # 2. 统一大小写 (确保 'close' 和 'Close' 能对上)
                new_data.columns = [c.capitalize() for c in new_data.columns]
                
                # 3. 移除可能产生的 'Adj close' (通常回测只用 Close)
                # 如果你想保留 Adj close，可以删掉这一行
                if 'Adj close' in new_data.columns:
                    new_data = new_data.drop(columns=['Adj close'])

                # --- 合并逻辑 ---
                if os.path.exists(file_path) and not existing_df.empty:
                    # 仅保留新数据中与旧数据列名一致的列，防止列不对齐
                    common_cols = existing_df.columns.intersection(new_data.columns)
                    if len(common_cols) > 0:
                        new_data = new_data[common_cols]
                        existing_df = existing_df[common_cols]
                        
                        combined_df = pd.concat([existing_df, new_data])
                        # 去重 (按索引日期)
                        combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
                    else:
                        print(f"⚠️ {ticker} 列名无法对齐，跳过合并。")
                        continue
                else:
                    combined_df = new_data

                # 保存
                combined_df.to_csv(file_path)
                success_count += 1
            else:
                print(f"ℹ️ {ticker} 没有新数据。")
            
            time.sleep(1) # 防限流

        except Exception as e:
            print(f"❌ {ticker} 更新失败: {e}")
            continue

    print(f"\n✨ 更新完成！成功同步 {success_count} 只股票。")

# ⚠️ 注意：
# 由于你之前的 MSTR.csv 已经被污染了（有了很多乱七八糟的列），
# 建议先手动删除那个已经损坏的 MSTR.csv 文件，让程序重新下载一次干净的。
# 或者使用下面的清洗代码修复现有文件。

my_tickers = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "BRK.B", "AVGO", "TSLA",
    "LLY", "JPM", "WMT", "V", "MA", "XOM", "UNH", "ORCL", "COST", "PG",
    "HD", "JNJ", "ABBV", "BAC", "CRM", "NFLX", "AMD", "CVX", "ADBE", "LIN",
    "PEP", "TMUS", "TMO", "WFC", "PLTR", "CSCO", "ACN", "PM", "ABT", "GE",
    "MCD", "DIS", "DHR", "INTU", "VZ", "CAT", "TXN", "QCOM", "PFE", "AXP",
    "AMAT", "NEE", "MS", "IBM", "RTX", "UNP", "AMGN", "LOW", "ISRG", "HON",
    "SYK", "SPGI", "GS", "INTC", "BKNG", "TJX", "VRTX", "LMT", "ETN", "BSX",
    "REGN", "BLK", "NOW", "MU", "SCHW", "MDLZ", "C", "ADI", "CI", "ANET",
    "MMC", "T", "DE", "GILD", "PANW", "LRCX", "BA", "CB", "PLD", "ADP",
    "ZTS", "MDT", "WM", "APP", "CL", "VLO", "HOOD", "HCA", "ICE",
    "SNPS", "CME", "CDNS", "MO", "SHW", "PH", "EQIX", "TDG", "EOG", "WELL",
    "CRWD", "MAR", "MCK", "FDX", "APH", "EMR", "ITW", "CTAS", "KLAC", "ECL",
    "NOC", "BDX", "CSX", "PYPL", "BSX", "COF", "MCO", "USB", "PGR", "ORLY",
    "ROP", "DASH", "COIN", "TTD", "XYZ", "IBKR", "EME", "TKO", "WSM", "EXE",
    "NSC", "AON", "GD", "ADSK", "FCX", "TGT", "PCAR", "D", "KMB", "EW",
    "F", "MSI", "MCHP", "O", "MET", "AJG", "SRE", "TRV", "STZ", "AIG",
    "CHTR", "DLR", "MARA", "PSA", "DOW", "PEG", "ALL", "KDP", "AZO", "CPRT",
    "PAYX", "NEM", "GM", "GEV", "MNST", "GWW", "BKR", "OTIS", "VRSK", "MPC",
    "HWM", "KHC", "OXY", "A", "CCI", "VICI", "ADM", "CMI", "ELV", "CTVA",
    "IDXX", "WBD", "GIS", "LULU", "AEP", "E", "HPQ", "BBY", "KVUE", "SYY",
    "DLTR", "KR", "CSGP", "DXCM", "FTNT", "K", "DHI", "CNC", "LUV", "BK",
    "PRU", "IQV", "EXC", "LEN", "STT", "HUM", "LHX", "TEL", "DD",
    "AME", "DAL", "FIS", "ON", "FAST", "MTD", "KEYS", "FSLR", "VTR",
    "ED", "ROK", "WST", "DTE", "PPG", "GLW", "AMP", "AWK", "ES", "YUM",
    "SBAC", "CBRE", "CTSH", "EFX", "FE", "FITB", "GPN", "HIG",
    "HRL", "HST", "IEX", "IFF", "IT", "IVZ", "JBHT", "JKHY", "KIM", "L",
    "LDOS", "LKQ", "LRN", "LVS", "MAS", "MGM", "MHK", "MKC", "MLM", "MOS",
    "MPWR", "MRNA", "MSCI", "MTB", "NDAQ", "NI", "NKE", "NTRS", "NUE", "NVT",
    "NWL", "NWSA", "NWS", "OMC", "PARA", "PAYC", "PBI", "PCG", "PENN", "PNC",
    "PNR", "PNW", "POOL", "PTC", "PWR", "RF", "RHI", "RJF", "RL", "RMD",
    "ROL", "SEE", "SJM", "SLB", "SNA", "SNX", "SO", "STE", "STX", "SWK",
    "SWKS", "TFC", "TFX", "TPR", "TRMB", "TROW", "TT", "TV", "TYL", "UAL",
    "UDR", "UHS", "ULTA", "URI", "VFC", "VMC", "VNO", "VRSN", "VRT", "VTR",
    "WAB", "WAT", "WEC", "WHR", "WY", "WYNN", "XEL", "XRAY", "XYL", "YUM",
    "ZBH", "ZION", "ZTS", "AKAM", "ALB", "ALGN", "ALLE", "AMCR", "BBWI", "BEN",
    "BXP", "CAH", "CCL", "CE", "CF", "CFG", "CHD", "CHRW", "CLX", "CMA",
    "CAG", "CPB", "CPT", "CRL", "CTRA", "CVS", "CZR", "DPZ", "DRI",
    "EBAY", "EMN", "ENPH", "EPAM", "EQR", "ERIE", "ESS", "ETR", "EVRG", "EXPD",
    "EXPE", "FANG", "FDS", "FMC", "FOXA", "FOX", "FRT", "FTV", "GEN", "GNRC",
    "HAL", "HAS", "HBAN", "HII", "HOLX", "HSIC", "IXX", "IP", "IRM",
    "IVZ", "J", "KEY", "KMX", "LNC", "LNT", "LW", "LYB", "LYV",
    "MAA", "MKTX", "MTCH", "NCLH", "NDSN", "NVR", "NRG", "PARA",
    "PENN", "PKG", "PR", "PVH", "QRVO", "RE",  "RVTY",
    "RVMD", "SBNY", "SEDG", "SEE", "SNA", "STX", "TAP", "TECH", "TER",
    "TFX", "TGT", "TJX", "TMO", "TROW", "TRV", "TSN", "TYL", "UHS",
    "UNM", "VFC", "VLO", "VMC", "VNO", "VRSN", "VRSK", "VRTX", "VTR", "VZ",
    "WAB", "WAT", "WDC", "WEC", "WELL", "WFC", "WHR", "WM", "WMB",
    "WMT", "WRB", "WST", "WTW", "WY", "WYNN", "XEL", "XOM", "XRAY",
    "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS",
    "NVDA","AAPL","MSFT","AMZN","GOOG","GOOGL","META","AVGO","TSLA","TSM","COST","PEP","NFLX","ADBE","AMD",
    "QCOM","TMUS","TXN","INTU","AMAT","ISRG","AMGN","HON","VRTX","BKNG","PANW","LRCX","ADI","GILD","SBUX",
    "MU","REGN","MDLZ","KLAC","INTC","SNPS","CDNS","ASML","MELI","PYPL","MAR","CTAS","ORLY","ROP","CSX",
    "NXPI","PCAR","MNST","ADSK","CPRT","FTNT","PAYX","MCHP","KDP","KHC","AEP","GEHC","IDXX","EXC","ODFL",
    "BKR","LULU","MRVL","CTSH","EA","DASH","FAST","AZN","TTD","CDW","ROST","ON","CSCO","ABNB","TEAM",
    "PDD","BIIB","DXCM","ZS","ILMN","MRNA","ALNY","FER","INSM","MPWR","STX","WDC","AXON","MDB",
    "ARM","PLTR","APP","SNOW","DDOG","MSTR","VRT","FSLR","CRWD",
    "ARM",   # Arm Holdings (英国芯片巨头)
    "MELI",  # MercadoLibre (拉美电商巨头)
    "SHOP",  # Shopify (加拿大电商SaaS)
    "TTD",   # The Trade Desk (广告科技，未入选标普的遗珠)
    "COIN",  # Coinbase (加密货币交易所)
    "DASH",  # DoorDash (外卖配送)
    "SQ",    # Block/Square (金融科技)
    "SNOW",  # Snowflake (云数据)
    "TEAM",  # Atlassian (Jira母公司，澳洲)
    "SPOT",  # Spotify (流媒体，卢森堡)
    "MSTR",  # MicroStrategy (比特币概念)
    "NET",   # Cloudflare (网络安全/CDN)
    "RBLX",  # Roblox (元宇宙/游戏)
    "PINS",  # Pinterest (社交媒体)
    "SNAP",  # Snap Inc. (社交媒体)
    "DKNG",  # DraftKings (博彩)
    "HOOD",  # Robinhood (互联网券商)
    "APP",   # AppLovin (移动营销)
    "TOST",  # Toast (餐饮SaaS)
    "DDOG",  # Datadog (监控SaaS)

    # --- 全球核心资产 ADR (Global Giants) ---
    # 这些公司市值极高，但因不是美国公司而不在标普500
    "TSM",   # 台积电 (半导体)
    "NVO",   # 诺和诺德 (减肥药双雄之一)
    "ASML",  # 阿斯麦 (光刻机)
    "SAP",   # SAP (德国软件巨头)
    "AZN",   # 阿斯利康 (制药)
    "NVS",   # 诺华制药 (制药)
    "TM",    # 丰田汽车 (汽车)
    "BABA",  # 阿里巴巴 (中国电商)
    "PDD",   # 拼多多 (中国电商)
    "JD",    # 京东 (中国电商)
    "SHEL",  # 壳牌 (能源)
    "TTE",   # 达道尔能源 (能源)
    "HSBC",  # 汇丰控股 (银行)
    "HDB",   # HDFC Bank (印度最大私营银行)
    "UL",    # 联合利华 (消费品)
    "SNY",   # 赛诺菲 (制药)
    "BP",    # 英国石油 (能源)
    "RY",    # 皇家银行 (加拿大银行)
    "TD",    # 多伦多道明银行 (加拿大银行)
    "MUFG",  # 三菱日联金融 (日本银行)
    "SONY",  # 索尼 (日本综合)
    "RELX",  # RELX PLC (数据分析)
    "RACE",  # 法拉利 (豪华车)
    "STLA",  # Stellantis (汽车)
    "DEO",   # 帝亚吉欧 (酒业)
    "RIO",   # 力拓 (矿业)
    "VALE",  # 淡水河谷 (矿业)
    "BHP",   # 必和必拓 (矿业)
    "INFY",  # Infosys (印度IT)
    "UBS",   # 瑞银集团 (银行)
    "GSK",   # 葛兰素史克 (制药)
    "BTI",   # 英美烟草 (烟草)
    "BUD",   # 百威英博 (啤酒)
    "CNQ",   # 加拿大自然资源 (能源)
    "SCCO"  # 南方铜业 (矿业)
]

# 使用方法
update_incremental_data(set(my_tickers))

