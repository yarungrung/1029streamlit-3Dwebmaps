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
# --- 確保所有必需的函式庫已在檔案頂部匯入 ---
import rioxarray as rxr
st.title("Plotly 3D 地圖 (DEM Surface)")
st.header("互動式 龜山島DEM 3D 模型")


# --- 1. 讀取 DEM 檔案 ---
tif_filename = 'turtleisland.tif'

# 建立完整的相對路徑
tif_path = os.path.join(os.path.dirname(__file__), "data", tif_filename) 

# 檢查檔案是否存在
if not os.path.exists(tif_path): 
    st.error(f"❌ 檔案遺失！請確認檔案 {tif_path} 已在 data/ 資料夾中提交。")
    st.stop()
    
# 使用 rioxarray 讀取 DEM 影像 
try:
    data = rxr.open_rasterio(tif_path, masked=True).squeeze()
    st.info(f"成功讀取 DEM 檔案：{tif_filename}，網格尺寸：{data.shape}。")
    
except Exception as e:
    st.error(f"⚠️ 讀取檔案時發生錯誤：{e}")
    st.stop()

# --- 2. 3D 互動地圖視覺化 (Plotly) ---

try: 
    # 提取高程數據和坐標
    elevation_data = data.values
 
    x_coords = data.x.values
    y_coords = data.y.values

    # 建立 Plotly 3D Surface 圖表物件
    fig = go.Figure(data=[
        go.Surface(
            z=elevation_data, 
            x=x_coords, 
            y=y_coords,  
            colorscale="Viridis", 
            name="DEM Surface"
        )
    ])

    # 調整 3D 視角和外觀
    fig.update_layout(
        title="**🐢 龜山島 3D 地形圖 (Plotly Interactive)**",
        
        width=900,
        height=750,
        scene=dict(
            xaxis_title="X 坐標",
            yaxis_title="Y 坐標",
            zaxis_title="海拔 (Z, m)",
            aspectmode='data' 
        )
    )

    # 在 Streamlit 中顯示
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ 建立 Plotly 3D 圖時發生錯誤：{e}")

# --- 3. 清理資源 ---
try:
    data.close() 
    st.success("Plotly 3D 模型繪製完成，已關閉檔案資源。")
except NameError:
    pass