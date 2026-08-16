import streamlit as st
import pandas as pd
import os
import datetime
import yfinance as yf

# 设置页面配置
st.set_page_config(page_title="TD结构选股扫描器", layout="wide")

TICKER_NAME_MAP = {
    "A": "安捷伦科技 (Agilent Technologies)",
    "AAPL": "苹果 (Apple)",
    "ABBV": "艾伯维 (AbbVie)",
    "ABNB": "爱彼迎 (Airbnb)",
    "ABT": "雅培 (Abbott Laboratories)",
    "ACN": "埃森哲 (Accenture)",
    "ADBE": "奥多比 (Adobe)",
    "ADI": "亚德诺半导体 (Analog Devices)",
    "ADM": "阿彻丹尼尔斯米德兰 (Archer-Daniels-Midland)",
    "ADP": "安德普翰 (Automatic Data Processing)",
    "ADSK": "欧特克 (Autodesk)",
    "AEP": "美国电力 (American Electric Power)",
    "AIG": "美国国际集团 (American International Group)",
    "AJG": "亚瑟加拉格尔 (Arthur J. Gallagher)",
    "AKAM": "阿卡迈 (Akamai Technologies)",
    "ALB": "雅宝 (Albemarle)",
    "ALGN": "爱齐科技 (Align Technology)",
    "ALL": "好事达 (Allstate)",
    "ALLE": "安朗杰 (Allegion)",
    "ALNY": "奥尼兰姆制药 (Alnylam Pharmaceuticals)",
    "AMAT": "应用材料 (Applied Materials)",
    "AMCR": "安姆科 (Amcor)",
    "AMD": "超威半导体 (Advanced Micro Devices)",
    "AME": "阿美特克 (AMETEK)",
    "AMGN": "安进 (Amgen)",
    "AMP": "美 Ameriprise 金融 (Ameriprise Financial)",
    "AMZN": "亚马逊 (Amazon.com)",
    "ANET": "阿丽斯塔网络 (Arista Networks)",
    "AON": "怡安集团 (Aon)",
    "APH": "安费诺 (Amphenol)",
    "APP": "AppLovin",
    "ARM": "安谋 (Arm Holdings)",
    "ASML": "阿斯麦 (ASML Holding)",
    "AVGO": "博通 (Broadcom)",
    "AWK": "美国水务 (American Water Works)",
    "AXON": "阿克森科技 (Axon Enterprise)",
    "AXP": "美国运通 (American Express)",
    "AZN": "阿斯利康 (AstraZeneca)",
    "AZO": "汽车地带 (AutoZone)",
    "BA": "波音 (Boeing)",
    "BABA": "阿里巴巴 (Alibaba Group)",
    "BAC": "美国银行 (Bank of America)",
    "BBWI": "Bath & Body Works",
    "BBY": "百思买 (Best Buy)",
    "BDX": "碧迪医疗 (Becton Dickinson)",
    "BEN": "富兰克林资源 (Franklin Resources)",
    "BHP": "必和必拓 (BHP Group)",
    "BIIB": "渤健 (Biogen)",
    "BK": "纽约梅隆银行 (Bank of New York Mellon)",
    "BKNG": "缤客 (Booking Holdings)",
    "BKR": "贝克休斯 (Baker Hughes)",
    "BLK": "贝莱德 (BlackRock)",
    "BP": "英国石油 (BP)",
    "BSX": "波士顿科学 (Boston Scientific)",
    "BTI": "英美烟草 (British American Tobacco)",
    "BUD": "百威英博 (Anheuser-Busch InBev)",
    "BXP": "波士顿地产 (BXP)",
    "C": "花旗集团 (Citigroup)",
    "CAG": "康尼格拉 (Conagra Brands)",
    "CAH": "卡地纳健康 (Cardinal Health)",
    "CAT": "卡特彼勒 (Caterpillar)",
    "CB": "安达保险 (Chubb)",
    "CBRE": "世邦魏理仕 (CBRE Group)",
    "CCI": "冠城国际 (Crown Castle)",
    "CCL": "嘉年华邮轮 (Carnival)",
    "CDNS": "楷登电子 (Cadence Design Systems)",
    "CDW": "CDW Corp",
    "CE": "塞拉尼斯 (Celanese)",
    "CF": "CF工业控股 (CF Industries)",
    "CFG": "公民金融集团 (Citizens Financial Group)",
    "CHD": "丘奇德怀特 (Church & Dwight)",
    "CHRW": "罗宾逊全球物流 (C.H. Robinson)",
    "CHTR": "特许通讯 (Charter Communications)",
    "CI": "信诺健康 (The Cigna Group)",
    "CL": "高露洁-棕榄 (Colgate-Palmolive)",
    "CLX": "高乐氏 (Clorox)",
    "CMA": "联信银行 (Comerica)",
    "CME": "芝加哥商业交易所 (CME Group)",
    "CMI": "康明斯 (Cummins)",
    "CNC": "森特恩 (Centene)",
    "CNQ": "加拿大自然资源 (Canadian Natural Resources)",
    "COF": "第一资本金融 (Capital One)",
    "COIN": "Coinbase Global",
    "COST": "开市客 / 好市多 (Costco Wholesale)",
    "CPB": "金宝汤 (The Campbell's Company)",
    "CPRT": "科帕特 (Copart)",
    "CPT": "卡姆登物业信托 (Camden Property Trust)",
    "CRL": "查尔斯河实验室 (Charles River Laboratories)",
    "CRM": "赛富时 (Salesforce)",
    "CRWD": "CrowdStrike Holdings",
    "CSCO": "思科 (Cisco Systems)",
    "CSGP": "科斯塔集团 (CoStar Group)",
    "CSX": "CSX运输 (CSX Corp)",
    "CTAS": "信塔斯 (Cintas)",
    "CTRA": "科特拉能源 (Coterra Energy)",
    "CTSH": "高知特 (Cognizant Technology Solutions)",
    "CTVA": "科迪华 (Corteva)",
    "CVS": "CVS健康 (CVS Health)",
    "CVX": "雪佛龙 (Chevron)",
    "CZR": "凯撒娱乐 (Caesars Entertainment)",
    "D": "道明尼能源 (Dominion Energy)",
    "DAL": "达美航空 (Delta Air Lines)",
    "DASH": "DoorDash",
    "DD": "杜邦 (DuPont de Nemours)",
    "DDOG": "Datadog",
    "DE": "迪尔公司 / 约翰迪尔 (Deere & Company)",
    "DELL": "戴尔科技 (Dell Technologies)",
    "DEO": "帝亚吉欧 (Diageo)",
    "DHI": "霍顿房屋 (D.R. Horton)",
    "DHR": "丹纳赫 (Danaher)",
    "DIS": "迪士尼 (Walt Disney)",
    "DKNG": "DraftKings",
    "DLR": "数字不动产信托 (Digital Realty Trust)",
    "DLTR": "美元树 (Dollar Tree)",
    "DOW": "陶氏化学 (Dow Inc.)",
    "DPZ": "达美乐披萨 (Domino's Pizza)",
    "DRI": "达登餐饮 (Darden Restaurants)",
    "DTE": "DTE能源 (DTE Energy)",
    "DXCM": "德康医疗 (DexCom)",
    "E": "埃尼石油 (Eni SpA)",
    "EA": "艺电 (Electronic Arts)",
    "EBAY": "亿贝 (eBay)",
    "ECL": "艺康 (Ecolab)",
    "ED": "爱迪生联合电气 (Consolidated Edison)",
    "EFX": "艾可飞 (Equifax)",
    "ELV": "Elevance Health",
    "EME": "EMCOR Group",
    "EMN": "伊士曼化工 (Eastman Chemical)",
    "EMR": "艾默生电气 (Emerson Electric)",
    "ENPH": "伊诺菲斯能源 (Enphase Energy)",
    "EOG": "EOG能源 (EOG Resources)",
    "EPAM": "易沛系统 (EPAM Systems)",
    "EQIX": "易昆尼克斯 (Equinix)",
    "EQR": "平等资产信托 (Equity Residential)",
    "ERIE": "伊利赔偿 (Erie Indemnity)",
    "ES": "永源能源 (Eversource Energy)",
    "ESS": "埃塞克斯房产信托 (Essex Property Trust)",
    "ETN": "伊顿 (Eaton)",
    "ETR": "安特吉 (Entergy)",
    "EVRG": "恒久能源 (Evergy)",
    "EW": "爱德华生命科学 (Edwards Lifesciences)",
    "EXC": "爱克斯龙 (Exelon)",
    "EXE": "Extendicare",
    "EXPD": "康捷国际物流 (Expeditors International)",
    "EXPE": "亿客行 (Expedia Group)",
    "F": "福特汽车 (Ford Motor)",
    "FANG": "响尾蛇能源 (Diamondback Energy)",
    "FAST": "快扣 (Fastenal)",
    "FCX": "自由港麦克莫兰 (Freeport-McMoRan)",
    "FDS": "慧甚 (FactSet Research Systems)",
    "FDX": "联邦快递 (FedEx)",
    "FE": "第一能源 (FirstEnergy)",
    "FER": "Ferroglobe",
    "FIS": "富达国民信息服务 (Fidelity National Information)",
    "FITB": "五三银行 (Fifth Third Bancorp)",
    "FMC": "富美实 (FMC Corp)",
    "FOX": "福克斯公司 B类 (Fox Corporation Class B)",
    "FOXA": "福克斯公司 A类 (Fox Corporation Class A)",
    "FRT": "联邦不动产投资信托 (Federal Realty Investment Trust)",
    "FSLR": "第一太阳能 (First Solar)",
    "FTNT": "飞塔信息 (Fortinet)",
    "FTV": "福迪威 (Fortive)",
    "GD": "通用动力 (General Dynamics)",
    "GE": "通用电气航天 (GE Aerospace)",
    "GEHC": "GE医疗 (GE HealthCare Technologies)",
    "GEN": "基恩科技 (Gen Digital)",
    "GEV": "GE Vernova",
    "GILD": "吉利德科学 (Gilead Sciences)",
    "GIS": "通用磨坊 (General Mills)",
    "GLW": "康宁 (Corning)",
    "GM": "通用汽车 (General Motors)",
    "GNRC": "捷诺克 (Generac Holdings)",
    "GOOG": "谷歌 C (Alphabet Class C)",
    "GOOGL": "谷歌 A (Alphabet Class A)",
    "GPN": "环球环球支付 (Global Payments)",
    "GS": "高盛 (Goldman Sachs)",
    "GSK": "葛兰素史克 (GSK plc)",
    "GWW": "固安捷 (W.W. Grainger)",
    "HAL": "哈里伯顿 (Halliburton)",
    "HAS": "孩之宝 (Hasbro)",
    "HBAN": "亨廷顿银行 (Huntington Bancshares)",
    "HCA": "HCA医疗 (HCA Healthcare)",
    "HD": "家得宝 (Home Depot)",
    "HDB": "HDFC银行 (HDFC Bank)",
    "HIG": "哈特福德金融 (Hartford Financial Services)",
    "HII": "亨廷顿英格尔斯工业 (Huntington Ingalls Industries)",
    "HOLX": "豪洛捷 (Hologic)",
    "HON": "霍尼韦尔 (Honeywell International)",
    "HOOD": "Robinhood Markets",
    "HPQ": "惠普 (HP Inc.)",
    "HRL": "荷美尔食品 (Hormel Foods)",
    "HSBC": "汇丰控股 (HSBC Holdings)",
    "HSIC": "亨利香恩 (Henry Schein)",
    "HST": "宿主酒店及度假村 (Host Hotels & Resorts)",
    "HUM": "哈门那 (Humana)",
    "HWM": "豪迈 (Howmet Aerospace)",
    "IBKR": "盈透证券 (Interactive Brokers)",
    "IBM": "国际商业机器 (IBM)",
    "ICE": "洲际交易所 (Intercontinental Exchange)",
    "IDXX": "爱德士检验 (IDEXX Laboratories)",
    "IEX": "艺达思 (IDEX Corp)",
    "IFF": "国际香精香料 (International Flavors & Fragrances)",
    "ILMN": "因美纳 (Illumina)",
    "INFY": "印孚瑟斯 (Infosys)",
    "INSM": "因斯梅德 (Insmed)",
    "INTC": "英特尔 (Intel)",
    "INTU": "财捷 (Intuit)",
    "IP": "国际纸业 (International Paper)",
    "IQV": "艾昆纬 (IQVIA Holdings)",
    "IRM": "铁山 (Iron Mountain)",
    "ISRG": "直觉外科 / 达芬奇手术机器人 (Intuitive Surgical)",
    "IT": "高德纳 (Gartner)",
    "ITW": "依利诺工具 (Illinois Tool Works)",
    "IVZ": "景顺 (Invesco)",
    "J": "雅各布工程 (Jacobs Solutions)",
    "JBHT": "亨特运输 (J.B. Hunt Transport Services)",
    "JD": "京东 (JD.com)",
    "JKHY": "杰克亨利 (Jack Henry & Associates)",
    "JNJ": "强生 (Johnson & Johnson)",
    "JPM": "摩根大通 (JPMorgan Chase)",
    "K": "Kellanova / 原家乐氏",
    "KDP": "Keurig Dr Pepper",
    "KEY": "科美奇银行 (KeyCorp)",
    "KEYS": "是德科技 (Keysight Technologies)",
    "KHC": "卡夫亨氏 (Kraft Heinz)",
    "KIM": "金科房产信托 (Kimco Realty)",
    "KLAC": "科磊 (KLA Corporation)",
    "KMB": "金佰利 (Kimberly-Clark)",
    "KMX": "车美仕 (CarMax)",
    "KR": "克罗格 (Kroger)",
    "KVUE": "科赴 (Kenvue)",
    "L": "洛士 (Loews)",
    "LDOS": "利多斯 (Leidos Holdings)",
    "LEN": "莱纳房产 (Lennar)",
    "LHX": "L3哈里斯科技 (L3Harris Technologies)",
    "LIN": "林德 (Linde)",
    "LKQ": "LKQ Corp",
    "LLY": "礼来 (Eli Lilly)",
    "LMT": "洛克希德·马丁 (Lockheed Martin)",
    "LNC": "林肯国民 (Lincoln National)",
    "LNT": "联合能源 (Alliant Energy)",
    "LOW": "劳氏 (Lowe's Companies)",
    "LRCX": "拉姆研究 / 泛林半导体 (Lam Research)",
    "LRN": "Stride Inc",
    "LULU": "露露乐蒙 (Lululemon Athletica)",
    "LUV": "西南航空 (Southwest Airlines)",
    "LVS": "拉斯维加斯金沙 (Las Vegas Sands)",
    "LW": "蓝威斯顿 (Lamb Weston)",
    "LYB": "利安德巴塞尔 (LyondellBasell)",
    "LYV": "理想国演艺 (Live Nation Entertainment)",
    "MA": "万事达 (Mastercard)",
    "MAA": "中大西洋公寓社区 (Mid-America Apartment Communities)",
    "MAR": "万豪国际 (Marriott International)",
    "MARA": "马拉松数字控股 (MARA Holdings)",
    "MAS": "马斯科 (Masco)",
    "MCD": "麦当劳 (McDonald's)",
    "MCHP": "微芯科技 (Microchip Technology)",
    "MCK": "麦克森 (McKesson)",
    "MCO": "穆迪 (Moody's Corporation)",
    "MDB": "MongoDB",
    "MDLZ": "亿滋国际 (Mondelez International)",
    "MDT": "美敦力 (Medtronic)",
    "MELI": "美客多 (MercadoLibre)",
    "MET": "大都会人寿 (MetLife)",
    "META": "Meta Platforms",
    "MGM": "美高梅国际酒店 (MGM Resorts International)",
    "MHK": "莫霍克工业 (Mohawk Industries)",
    "MKC": "味好美 (McCormick & Company)",
    "MKTX": "MarketAxess Holdings",
    "MLM": "马丁-玛丽埃塔材料 (Martin Marietta Materials)",
    "MMC": "威达信 (Marsh & McLennan Companies)",
    "MNST": "怪兽饮料 (Monster Beverage)",
    "MO": "奥驰亚 (Altria Group)",
    "MOS": "美盛 (The Mosaic Company)",
    "MPC": "马拉松原油 (Marathon Petroleum)",
    "MPWR": "芯源系统 (Monolithic Power Systems)",
    "MRNA": "莫德纳 (Moderna)",
    "MRVL": "美满电子 (Marvell Technology)",
    "MS": "摩根士丹利 (Morgan Stanley)",
    "MSCI": "明晟 (MSCI Inc.)",
    "MSFT": "微软 (Microsoft)",
    "MSI": "摩托罗拉系统 (Motorola Solutions)",
    "MSTR": "微策投资 (MicroStrategy)",
    "MTB": "M&T银行 (M&T Bank)",
    "MTCH": "Match Group",
    "MTD": "梅特勒-托利多 (Mettler-Toledo)",
    "MU": "美光科技 (Micron Technology)",
    "MUFG": "三菱日联金融集团 (Mitsubishi UFJ Financial)",
    "NCLH": "诺唯真邮轮 (Norwegian Cruise Line)",
    "NDAQ": "纳斯达克公司 (Nasdaq Inc.)",
    "NDSN": "诺信 (Nordson)",
    "NEE": "新纪元能源 (NextEra Energy)",
    "NEM": "纽蒙特矿业 (Newmont)",
    "NET": "Cloudflare",
    "NFLX": "奈飞 (Netflix)",
    "NI": "尼索思 (NiSource)",
    "NKE": "耐克 (Nike)",
    "NOC": "诺斯洛普·格鲁门 (Northrop Grumman)",
    "NOW": "ServiceNow",
    "NRG": "NRG能源 (NRG Energy)",
    "NSC": "诺福克南方 (Norfolk Southern)",
    "NTRS": "北方信托 (Northern Trust)",
    "NUE": "纽柯钢铁 (Nucor)",
    "NVDA": "英伟达 (NVIDIA)",
    "NVO": "诺和诺德 (Novo Nordisk)",
    "NVR": "NVR Inc",
    "NVS": "诺华制药 (Novartis)",
    "NVT": "恩温特 (nVent Electric)",
    "NWL": "纽威尔 (Newell Brands)",
    "NWS": "新闻集团 B类 (News Corp Class B)",
    "NWSA": "新闻集团 A类 (News Corp Class A)",
    "NXPI": "恩智浦半导体 (NXP Semiconductors)",
    "O": "不动产收益公司 (Realty Income)",
    "ODFL": "奥德道明尼货运 (Old Dominion Freight Line)",
    "OMC": "宏盟集团 (Omnicom Group)",
    "ON": "安森美半导体 (ON Semiconductor)",
    "ORCL": "甲骨文 (Oracle)",
    "ORLY": "奥莱利汽车配件 (O'Reilly Automotive)",
    "OTIS": "奥的斯电梯 (Otis Worldwide)",
    "OXY": "西方石油 (Occidental Petroleum)",
    "PANW": "派拓网络 (Palo Alto Networks)",
    "PARA": "派拉蒙全球 (Paramount Global)",
    "PAYC": "Paycom Software",
    "PAYX": "沛齐 (Paychex)",
    "PBI": "必能宝 (Pitney Bowes)",
    "PCAR": "帕卡 (PACCAR)",
    "PCG": "太平洋煤电 (PG&E Corp)",
    "PDD": "拼多多 (PDD Holdings)",
    "PEG": "公共服务企业集团 (Public Service Enterprise Group)",
    "PENN": "佩恩娱乐 (PENN Entertainment)",
    "PEP": "百事 (PepsiCo)",
    "PFE": "辉瑞 (Pfizer)",
    "PG": "宝洁 (Procter & Gamble)",
    "PGR": "前进保险 (Progressive Corp)",
    "PH": "派克汉尼汾 (Parker-Hannifin)",
    "PINS": "Pinterest",
    "PKG": "包装公司 (Packaging Corp of America)",
    "PLD": "安 Prologis / 普洛斯 (Prologis)",
    "PLTR": "帕兰提尔 (Palantir Technologies)",
    "PM": "菲利普莫里斯国际 (Philip Morris International)",
    "PNC": "PNC金融服务 (PNC Financial Services)",
    "PNR": "滨特尔 (Pentair)",
    "PNW": "品纳克西方能源 (Pinnacle West Capital)",
    "POOL": "普尔 (Pool Corp)",
    "PPG": "PPG工业 (PPG Industries)",
    "PR": "Permian Resources",
    "PRU": "保德信金融 (Prudential Financial)",
    "PSA": "大众仓储 (Public Storage)",
    "PTC": "PTC Inc",
    "PVH": "PVH Corp (Calvin Klein / Tommy Hilfiger)",
    "PWR": "广达服务 (Quanta Services)",
    "PYPL": "贝宝 (PayPal Holdings)",
    "QCOM": "高通 (Qualcomm)",
    "QRVO": "威讯联合半导体 (Qorvo)",
    "RACE": "法拉利 (Ferrari)",
    "RBLX": "罗布乐思 (Roblox)",
    "REGN": "再生元制药 (Regeneron Pharmaceuticals)",
    "RELX": "励讯集团 (RELX plc)",
    "RF": "地区金融 (Regions Financial)",
    "RHI": "罗伯特半岛 (Robert Half)",
    "RIO": "力拓 (Rio Tinto)",
    "RJF": "雷蒙德詹姆斯金融 (Raymond James Financial)",
    "RL": "拉夫劳伦 (Ralph Lauren)",
    "RMD": "瑞思迈 (ResMed)",
    "ROK": "罗克韦尔自动化 (Rockwell Automation)",
    "ROL": "罗林斯 (Rollins)",
    "ROP": "罗珀科技 (Roper Technologies)",
    "ROST": "罗斯百货 (Ross Stores)",
    "RTX": "雷神技术 (RTX Corp)",
    "RVMD": "Revolution Medicines",
    "RVTY": "瑞威泰 (Revvity)",
    "RY": "加拿大皇家银行 (Royal Bank of Canada)",
    "SAP": "思爱普 (SAP SE)",
    "SBAC": "SBA通信 (SBA Communications)",
    "SBNY": "标志银行 (Signature Bank)",
    "SBUX": "星巴克 (Starbucks)",
    "SCCO": "南方铜业 (Southern Copper)",
    "SCHW": "嘉信理财 (Charles Schwab)",
    "SEDG": "极地太阳能 (SolarEdge Technologies)",
    "SEE": "希悦尔 (Sealed Air)",
    "SHEL": "壳牌 (Shell plc)",
    "SHOP": "Shopify",
    "SHW": "宣伟 (Sherwin-Williams)",
    "SJM": "斯马克 (The J.M. Smucker Company)",
    "SLB": "斯伦贝谢 (SLB)",
    "SNA": "实耐宝 (Snap-on)",
    "SNAP": "色拉布 (Snap Inc.)",
    "SNOW": "Snowflake",
    "SNPS": "新思科技 (Synopsys)",
    "SNX": "新聚思 (TD SYNNEX)",
    "SNY": "赛诺菲 (Sanofi)",
    "SO": "南方公司 (Southern Company)",
    "SONY": "索尼 (Sony Group)",
    "SPGI标": "标普全球 (S&P Global)",
    "SPGI": "标普全球 (S&P Global)",
    "SPOT": "声网 / 声田 (Spotify Technology)",
    "SRE": "桑普拉能源 (Sempra)",
    "STE": "斯特里斯 (STERIS)",
    "STLA": "斯泰兰蒂斯 (Stellantis)",
    "STT": "道富 (State Street)",
    "STX": "希捷科技 (Seagate Technology)",
    "STZ": "星座品牌 (Constellation Brands)",
    "SWK": "史丹利百得 (Stanley Black & Decker)",
    "SWKS": "思佳讯 (Skyworks Solutions)",
    "SYK": "史赛克 (Stryker)",
    "SYY": "西斯科 (Sysco)",
    "T": "美国电话电报 (AT&T)",
    "TAP": "摩森康胜 (Molson Coors Beverage)",
    "TD": "多伦多道明银行 (Toronto-Dominion Bank)",
    "TDG": "泛美达航空 (TransDigm Group)",
    "TEAM": "Atlassian",
    "TECH": "生物科技 (Bio-Techne)",
    "TEL": "泰科电子 (TE Connectivity)",
    "TER": "泰瑞达 (Teradyne)",
    "TFC": "楚斯特金融 (Truist Financial)",
    "TFX": "泰利福 (Teleflex)",
    "TGT": "塔吉特 (Target)",
    "TJX": "TJX公司 (TJX Companies)",
    "TKO": "TKO Holdings (WWE / UFC)",
    "TM": "丰田汽车 (Toyota Motor)",
    "TMO": "赛默飞世尔 (Thermo Fisher Scientific)",
    "TMUS": "T-Mobile US",
    "TOST": "Toast Inc",
    "TPR": "泰佩思琦 (Tapestry - Coach母公司)",
    "TRMB": "天宝导航 (Trimble)",
    "TROW": "普徕仕 (T. Rowe Price)",
    "TRV": "旅行家集团 (The Travelers Companies)",
    "TSLA": "特斯拉 (Tesla)",
    "TSM": "台积电 (Taiwan Semiconductor Manufacturing)",
    "TSN": "泰森食品 (Tyson Foods)",
    "TT": "特灵科技 (Trane Technologies)",
    "TTD": "The Trade Desk",
    "TTE": "道达尔能源 (TotalEnergies)",
    "TV": "Grupo Televisa",
    "TXN": "德州仪器 (Texas Instruments)",
    "TYL": "泰勒科技 (Tyler Technologies)",
    "UAL": "联合航空 (United Airlines Holdings)",
    "UBS": "瑞银集团 (UBS Group)",
    "UDR": "UDR Inc",
    "UHS": "联合健康服务 (Universal Health Services)",
    "UL": "联合利华 (Unilever)",
    "ULTA": "奥尔塔美妆 (Ulta Beauty)",
    "UNH": "联合健康 (UnitedHealth Group)",
    "UNM": "尤尼姆集团 (Unum Group)",
    "UNP": "联合太平洋 (Union Pacific)",
    "URI": "联合租赁 (United Rentals)",
    "USB": "美国合众银行 (U.S. Bancorp)",
    "V": "维萨 (Visa)",
    "VALE": "淡水河谷 (Vale S.A.)",
    "VFC": "威富集团 (V.F. Corp - Vans/The North Face)",
    "VICI": "VICI Properties",
    "VLO": "瓦莱罗能源 (Valero Energy)",
    "VMC": "火神材料 (Vulcan Materials)",
    "VNO": "沃纳多房产信托 (Vornado Realty Trust)",
    "VRSK": "威瑞斯克数据 (Verisk Analytics)",
    "VRSN": "威 sign (VeriSign)",
    "VRT": "维谛技术 (Vertiv Holdings)",
    "VRTX": "福泰制药 (Vertex Pharmaceuticals)",
    "VTR": "芬塔公司 (Ventas)",
    "VZ": "威瑞森电信 (Verizon Communications)",
    "WAB": "西屋制动 (Wabtec)",
    "WAT": "沃特世 (Waters Corp)",
    "WBD": "华纳兄弟探索 (Warner Bros. Discovery)",
    "WDC": "西部数据 (Western Digital)",
    "WEC": "WEC能源集团 (WEC Energy Group)",
    "WELL": "维尔塔房产信托 (Welltower)",
    "WFC": "富国银行 (Wells Fargo)",
    "WHR": "惠而浦 (Whirlpool)",
    "WM": "废物管理 (Waste Management)",
    "WMB": "威廉姆斯公司 (Williams Companies)",
    "WMT": "沃尔玛 (Walmart)",
    "WRB": "伯克利保险 (W.R. Berkley)",
    "WSM": "威廉姆斯索诺玛 (Williams-Sonoma)",
    "WST": "西氏医药包装 (West Pharmaceutical Services)",
    "WTW": "韦莱韬悦 (Willis Towers Watson)",
    "WY": "惠好 (Weyerhaeuser)",
    "WYNN": "永利度假村 (Wynn Resorts)",
    "XEL": "卓越能源 (Xcel Energy)",
    "XOM": "埃克森美孚 (Exxon Mobil)",
    "XRAY": "登士柏西诺德 (Dentsply Sirona)",
    "XYL": "赛莱默 (Xylem)",
    "XYZ": "Block / 原Square (XYZ代指)",
    "YUM": "百胜餐饮 (Yum! Brands)",
    "ZBH": "捷迈邦美 (Zimmer Biomet)",
    "ZBRA": "斑马技术 (Zebra Technologies)",
    "ZION": "齐昂银行 (Zions Bancorporation)",
    "ZS": "Zscaler",
    # 额外兼容带点的伯克希尔及其他常见变体
    "BRK.B": "伯克希尔·哈撒韦 (Berkshire Hathaway B)",
    "BRKB": "伯克希尔·哈撒韦 (Berkshire Hathaway B)",
    "LNI": "雷诺士国际 (Lennox International)",
    "CEG": "星座能源 (Constellation Energy)",
    "VST": "维斯达能源 (Vistra Corp)",
    "WDAY": "Workday"
}

def calculate_td_structure(df):
    """
    计算整个DataFrame的TD结构计数
    """
    close = df['Close']
    # 模拟通达信 BARSLASTCOUNT(CLOSE < REF(CLOSE, 4))
    condition = close < close.shift(4)
    # 这里的逻辑是：如果条件满足，累加计数；如果不满足，重置为0
    # Pandas vectorization trick:
    # 1. (condition != condition.shift()) 找出状态变化点
    # 2. cumsum() 给每一段连续的状态分配一个ID
    # 3. groupby().cumsum() 在每一段内累加
    td_count = condition.groupby((condition != condition.shift()).cumsum()).cumsum()
    return td_count

def scan_stocks(target_date, data_folder="data"):
    results_list = []
    
    # 检查文件夹是否存在
    if not os.path.exists(data_folder):
        st.error(f"找不到文件夹: {data_folder}，请确保在当前目录下创建该文件夹并放入CSV数据。")
        return []

    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(files)
    
    # 转换 target_date 为 datetime64[ns] 以便与 pandas 索引匹配
    target_ts = pd.Timestamp(target_date)

    for i, file in enumerate(files):
        # 更新进度条
        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"正在扫描: {file} ({i+1}/{total_files})")
        
        ticker = file.replace('.csv', '')
        file_path = os.path.join(data_folder, file)
        
        try:
            # 1. 读取数据
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            
            # 统一列名
            df.columns = [c.capitalize() for c in df.columns]
            
            # 确保按日期升序排列
            df = df.sort_index()

            # 2. 检查选定日期是否存在于数据中
            # 如果这一天是周末、假期或者停牌，数据中可能没有这一行
            if target_ts not in df.index:
                # 尝试找这一天之前最近的一个交易日? 
                # 这里为了严谨，如果指定日期没数据，则跳过
                continue
            
            # 获取目标日期在DataFrame中的整数位置
            loc_idx = df.index.get_loc(target_ts)
            
            # 如果数据历史太短，无法计算前置指标（至少需要前面4天+额外缓冲）
            if loc_idx < 5: 
                continue

            # 3. 截取需要的数据片段进行计算
            # 为了提高效率，我们不需要计算整个历史的TD，只需要计算目标日期附近的
            # 但是为了准确计算连续性，最好多取一些前置数据，比如前50天
            start_idx = max(0, loc_idx - 60)
            subset_df = df.iloc[start_idx : loc_idx + 1].copy()
            
            # 4. 计算指标
            close = subset_df['Close']
            high = subset_df['High']
            
            # 计算 TD 计数
            td_counts = calculate_td_structure(subset_df)
            
            # 获取目标日期的具体数值 (iloc[-1] 即为 target_date)
            last_td_count = td_counts.iloc[-1]
            curr_close = close.iloc[-1]
            prev_close = close.iloc[-2]  # REF(CLOSE, 1)
            
            # 获取 High 的引用
            # 注意：python list/iloc 切片逻辑
            # -1 是当前(target_date), -2 是昨天, -3 是前天(REF(High, 2)), -4 是大前天(REF(High, 3))
            high_ref_1 = high.iloc[-2] # REF(HIGH, 1)
            high_ref_2 = high.iloc[-3] # REF(HIGH, 2)
            high_ref_3 = high.iloc[-4] # REF(HIGH, 3)
            
            # 5. 买入条件判定 (逻辑与原代码保持一致)
            
            # HJ_31: 突破确认 
            # (注意：原逻辑好像没有直接用hj31做最终输出判定，这里保留计算逻辑)
            # hj31_signal = (curr_close > high_ref_2) and (prev_close <= high_ref_3)
            
            # TD 结构计数
            td_setup_9 = last_td_count >= 9 # 通常是等于9或者13时提示
            td_setup_13 = last_td_count >= 13
            # 如果你想要 >= 9，可以改回 >=
            
            # HJ_51 & HJ_54 信号 (13计数且突破昨天高点)
            hj51_54_signal = (last_td_count >= 13) and (curr_close > high_ref_1)

            # 6. 汇总判断 (根据原代码逻辑: 只要 TD>=9 或 TD>=13 就算发现)
            if (last_td_count >= 9):
                signal_type = "TD Setup"
                if last_td_count == 9: signal_type = "TD 9 Sequential"
                if last_td_count == 13: signal_type = "TD 13 Sequential"
                stock_name = TICKER_NAME_MAP.get(ticker, ticker)  # 查不到就默认显示 ticker 本身
                results_list.append({
                    'Ticker': ticker,
                    'Name': stock_name,
                    'Date': target_date.strftime('%Y-%m-%d'),
                    'Signal': signal_type,
                    'TD_Count': int(last_td_count),
                    'Close': round(curr_close, 2),
                    'Pct_Change': round((curr_close - prev_close)/prev_close * 100, 2)
                })

        except Exception as e:
            # 调试用，实际运行可以注释掉
            # print(f"Error processing {ticker}: {e}")
            continue
            
    status_text.text("扫描完成！")
    progress_bar.empty()
    
    return pd.DataFrame(results_list)

# --- Streamlit UI 部分 ---

st.title("📈 TD结构量化选股助手")
st.markdown("该工具基于 **TD Sequential** 策略扫描本地 CSV 数据。")

# 侧边栏配置
with st.sidebar:
    st.header("配置参数")
    
    # 1. 选择日期
    # 默认为今天
    default_date = datetime.date.today()
    selected_date = st.date_input("选择回测/选股日期", default_date)
    
    # 2. 数据文件夹
    data_folder = st.text_input("数据文件夹路径", value="data")
    
    # 3. 触发按钮
    start_btn = st.button("开始扫描", type="primary")

    st.info("""
    **逻辑说明：**
    1. TD Count >= 9
    2. 模拟通达信 BARSLASTCOUNT
    3. 比较逻辑：Close < Ref(Close, 4)
    """)

# 主界面逻辑
if start_btn:
    if not os.path.exists(data_folder):
        st.error(f"❌ 错误：找不到文件夹 '{data_folder}'。请确认路径正确。")
    else:
        st.write(f"正在扫描 **{selected_date}** 的数据...")
        
        # 执行耗时操作
        result_df = scan_stocks(selected_date, data_folder)
        
        if not result_df.empty:
            st.success(f"扫描完成！共发现 {len(result_df)} 只符合条件的股票。")
            
            # 格式化显示
            st.dataframe(
                result_df.style.map(
                    lambda x: 'color: green' if x == 'TD 9 Sequential' else ('color: red' if x == 'TD 13 Sequential' else ''), 
                    subset=['Signal']
                ),
                use_container_width=True
            )
            
            # CSV 下载按钮
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载结果 (CSV)",
                data=csv,
                file_name=f"td_scan_results_{selected_date}.csv",
                mime="text/csv",
            )
        else:
            st.warning(f"扫描完成，在 {selected_date} 没有发现符合买入条件的股票。")
            st.caption("可能原因：1. 当天无交易(周末/假期) 2. 数据未更新 3. 确实无信号")

else:
    st.write("👈 请在左侧选择日期并点击“开始扫描”。")
