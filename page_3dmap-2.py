import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import rasterio
import numpy as np
import os

file_path = "WID_Data_29102025-044042.csv"
st.title("Plotly 3D 地球 全球極端貧窮人口比例")

CSV_FILE = "WID_Data_29102025-044042.csv"
VALUE_COL = "Share of population in poverty ($3 a day, 2021 prices)"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)

    # 只保留 ISO3 國家代碼資料（排除地區）
    df = df[df["Code"].str.len() == 3]

    # 轉成整數年份（必需）
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    # 有數值的年份清單
    years = sorted(df.dropna(subset=[VALUE_COL])["Year"].unique(), reverse=True)

    return df, years


# --- 讀取資料 ---
df, years = load_data()
if df is None or len(years) == 0:
    st.error("資料讀取失敗")
    st.stop()

# --- 年份選單 ---
selected_year = st.selectbox("選擇年份", years)

# --- 篩選年份資料 ---
df_year = df[(df["Year"] == selected_year) & (df[VALUE_COL].notna())]

if df_year.empty:
    st.warning(f"{selected_year} 年沒有可用資料")
    st.stop()

# --- 2. 建立 3D 地理散點圖 (scatter_geo) ---
fig = px.scatter_geo(
    df_year,
    locations="Code",
    hover_name="Entity",
    color=VALUE_COL,
    size=VALUE_COL,
    projection="orthographic",
    color_continuous_scale=px.colors.sequential.YlOrRd,
    title=f"{selected_year} 年全球極端貧窮人口比例"
)
# --- 在 Streamlit 中顯示 ---
fig.update_layout(
    geo=dict(showland=True, landcolor="rgb(230,230,230)")
)

st.plotly_chart(fig, use_container_width=True)

# ---資料表 ---
st.subheader(f"{selected_year} 年資料表")
st.dataframe(df_year)


# "orthographic" 投影會將地球渲染成一個從太空中看到的球體，
# 從而產生類似 3D 地球儀的視覺效果。
# 其他常見投影如 "natural earth", "mercator" 等通常是 2D 平面地圖。


# ---------------------------------------------------------------------------------------

st.title("Plotly 3D 地圖 (DEM Surface)")
st.header("互動式 龜山島DEM 3D 模型")


# --- 讀取 DEM 檔案 ---
# 檔案路徑：假設 'turtleisland.tif' 位於 'data' 
tif_filename = 'turtleisland.tif'
file_path = "data/turtleisland.tif"

# 2. 檢查檔案是否存在
if not os.path.exists(tif_path):
    st.error(f"❌ 檔案遺失！請確認檔案 {tif_path} 已在 data/ 資料夾中提交。")
    st.stop()
    
# 3. 使用 rioxarray 讀取 DEM 影像 
try:
    # 讀取數據，並去除單一的 'band' 維度
    data = rxr.open_rasterio(tif_path, masked=True).squeeze()
    
    st.info(f"成功讀取 DEM 檔案：{tif_filename}，網格尺寸：{data.shape}。")
    
except Exception as e:
    st.error(f"⚠️ 讀取檔案時發生錯誤：{e}")
    # 確保在讀取失敗時停止執行後續的繪圖邏輯
    st.stop()

# --- 2. 3D 互動地圖視覺化 (Plotly) ---

try: 
    # 2.1 提取高程數據 (Z 軸)
    elevation_data = data.values
    
    # 2.2 從 xarray 數據中提取坐標 (X/Y 軸)
    # xarray/rioxarray 自動處理了地理坐標到數組的映射，方便提取
    x_coords = data.x.values
    y_coords = data.y.values

    # 2.3 建立 Plotly 3D Surface 圖表物件
    fig = go.Figure(data=[
        go.Surface(
            z=elevation_data, # 海拔高度 (Z 軸)
            x=x_coords,       # X 坐標 (東距/北距)
            y=y_coords,       # Y 坐標 (東距/北距)
            colorscale="Viridis", # 使用 Viridis 顏色圖 (可選 'Terrain', 'Electric' 等)
            name="DEM Surface"
        )
    ])

    # 2.4 調整 3D 視角和外觀
    fig.update_layout(
        title="**🐢 龜山島 3D 地形圖 (Plotly Interactive)**",
        # 設定寬度和高度
        width=900,
        height=750,
        scene=dict(
            xaxis_title="X 坐標 (東距, m)",
            yaxis_title="Y 坐標 (北距, m)",
            zaxis_title="海拔 (Z, m)",
            aspectmode='data' # 確保 X, Y, Z 的比例正確顯示
        )
    )

    # 2.5 在 Streamlit 中顯示
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ 建立 Plotly 3D 圖時發生錯誤：{e}")

# --- 3. 清理資源 ---
# 關閉檔案句柄
data.close() 
st.success("Plotly 3D 模型繪製完成，已關閉檔案資源。")
