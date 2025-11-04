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

# --- 1. 讀取 DEM ---
# 1. 定義檔案名稱：使用經過 QGIS 處理的、極小的、確認有效的 GeoTIFF 檔案
tif_filename = 'turtleisland.tif' 

# 2. 建立完整的相對路徑：確保 Streamlit Cloud 能正確找到位於 data/ 資料夾中的檔案
tif_path = os.path.join(os.path.dirname(__file__), "data", tif_filename)

# 3. 檢查檔案是否存在 (防止 Git 提交遺漏錯誤)
if not os.path.exists(tif_path):
    st.error(f"❌ 檔案遺失！請確認檔案 {tif_path} 已在 GitHub 倉庫的 data/ 資料夾中提交。")
    st.stop()

try:  # 讀取 GeoTIFF
    with rasterio.open(tif_path) as src:
        band1 = src.read(1)
        transform = src.transform

        st.write("Raster shape :", band1.shape)
        
        # 建立座標網格
        rows, cols = np.indices(band1.shape)
        # 座標計算
        xs, ys = rasterio.transform.xy(transform, rows, cols)
        x_coords = np.array(xs[0])
        y_coords = np.array([row[0] for row in ys])

    # 建立 Plotly 3D Surface
    fig = go.Figure(data=[
        go.Surface(
            z=band1,     # 海拔高度 
            x=x_coords,  # 經度
            y=y_coords,  # 緯度
            colorscale="Viridis"
        )
    ])

# --- 3. 調整 3D 視角和外觀 ---
# 使用 update_layout 方法來修改圖表的整體佈局和外觀設定
# 設定圖表的寬度和高度 (單位：像素)
    fig.update_layout(
        title="龜山島 3D 地形圖 ",
        width=900,
        height=750,
        scene=dict(
            xaxis_title="經度 (X)",
            yaxis_title="緯度 (Y)",
            zaxis_title="海拔 (Z)"
        )
    )

    # --- 4. 在 Streamlit 中顯示 ---
    st.plotly_chart(fig)

except rasterio.errors.RasterioIOError as e:
    # 如果這個錯誤再次出現，則表示 small_dem_final.tif 仍然是無效的 GeoTIFF
    st.error(f"⚠️ 檔案格式錯誤！無法開啟 GeoTIFF：{tif_path}\n詳細錯誤：{e}")
except Exception as e:
    st.error(f"⚠️ 發生未知錯誤：{e}")