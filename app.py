import streamlit as st
import pandas as pd
import os
import datetime

# 设置页面配置
st.set_page_config(page_title="TD结构选股扫描器", layout="wide")

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
                
                results_list.append({
                    'Ticker': ticker,
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
