import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


st.title("Plotly 3D 地圖 (向量 - 地球儀)")

file_path = "WID_Data_29102025-044042.csv"
try:
    df_raw = pd.read_csv(file_path, encoding="utf-8", header=None)
except Exception as e:
    st.error(f"❌ 無法讀取資料檔案：{e}")
    st.stop()
# --- 1. 載入資料 ---
year_row_idx = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("2014").any(), axis=1)].index[0]
year_row = df_raw.iloc[year_row_idx]
df = df_raw.iloc[year_row_idx + 1:].copy()
df.columns = year_row


# 移除可能重複的 header 或非國家行
df = df[~df["Country"].astype(str).str.contains("pall", case=False, na=False)]

# --- 4️⃣ 轉長表格（melt）---
df_long = df.melt(id_vars=["Country"], var_name="Year", value_name="GDP_per_capita")

# 嘗試轉換數字型態
df_long["GDP_per_capita"] = pd.to_numeric(df_long["GDP_per_capita"], errors="coerce")
df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce")
df_long = df_long.dropna(subset=["Year", "GDP_per_capita"])

# --- 5️⃣ 下拉式選單選擇年份 ---
years = sorted(df_long["Year"].unique())
selected_year = st.selectbox("📅 選擇年份", years, index=len(years) - 1)

# --- 6️⃣ 篩選該年份的資料 ---
df_year = df_long[df_long["Year"] == selected_year]
 
# --- 2. 建立 3D 地理散點圖 (scatter_geo) ---
fig = px.scatter_geo(
    df_year,
    locations="Country",
    locationmode="country names",
    color="GDP_per_capita",
    size="GDP_per_capita",
    hover_name="Country",
    projection="orthographic",
    title=f"{int(selected_year)} 年全球人均 GDP 分佈"
)
# "orthographic" 投影會將地球渲染成一個從太空中看到的球體，
# 從而產生類似 3D 地球儀的視覺效果。
# 其他常見投影如 "natural earth", "mercator" 等通常是 2D 平面地圖。


# --- 3. 在 Streamlit 中顯示 ---
fig.update_layout(
    height=700,
    margin=dict(l=0, r=0, t=40, b=0),
    geo=dict(
        showland=True,
        landcolor="rgb(217, 217, 217)",
        showocean=True,
        oceancolor="rgb(200, 230, 255)",
        showcountries=True,
    )
)
st.plotly_chart(fig, use_container_width=True)
# use_container_width=True:當設定為 True 時，Streamlit 會忽略 Plotly 圖表物件本身可能設定的寬度，
# 並強制讓圖表的寬度自動延展，以填滿其所在的 Streamlit 容器 (例如，主頁面的寬度、某個欄位 (column) 的寬度，
# 或是一個展開器 (expander) 的寬度)。

st.title("Plotly 3D 地圖 (網格 - DEM 表面)")

# --- 1. 讀取範例 DEM 資料 ---
# Plotly 內建的 "volcano" (火山) DEM 數據 (儲存為 CSV)
# 這是一個 2D 陣列 (Grid)，每個格子的值就是海拔
z_data = pd.read_csv("C://內政部20公尺網格數值地形模型資料.csv")

# --- 2. 建立 3D Surface 圖 ---
# 建立一個 Plotly 的 Figure 物件，它是所有圖表元素的容器
fig = go.Figure(
    # data 參數接收一個包含所有 "trace" (圖形軌跡) 的列表。
    # 每個 trace 定義了一組數據以及如何繪製它。
    data=[
        # 建立一個 Surface (曲面) trace
        go.Surface(
            # *** 關鍵參數：z ***
            # z 參數需要一個 2D 陣列 (或列表的列表)，代表在 X-Y 平面上每個點的高度值。
            # z_data.values 會提取 pandas DataFrame 底層的 NumPy 2D 陣列。
            # Plotly 會根據這個 2D 陣列的結構來繪製 3D 曲面。
            z=z_data.values,

            # colorscale 參數指定用於根據 z 值 (高度) 對曲面進行著色的顏色映射方案。
            # "Viridis" 是 Plotly 提供的一個常用且視覺效果良好的顏色漸層。
            # 高度值較低和較高的點會有不同的顏色。
            colorscale="Viridis"
        )
    ] # data 列表結束
)

# --- 3. 調整 3D 視角和外觀 ---
# 使用 update_layout 方法來修改圖表的整體佈局和外觀設定
fig.update_layout(
    # 設定圖表的標題文字
    title="台灣 3D 地形圖 (可旋轉)",

    # 設定圖表的寬度和高度 (單位：像素)
    width=800,
    height=700,

    # scene 參數是一個字典，用於配置 3D 圖表的場景 (座標軸、攝影機視角等)
    scene=dict(
        # 設定 X, Y, Z 座標軸的標籤文字
        xaxis_title='經度 (X)',
        yaxis_title='緯度 (Y)',
        zaxis_title='海拔 (Z)'
        # 可以在 scene 字典中加入更多參數來控制攝影機初始位置、座標軸範圍等
    )
)

# 這段程式碼執行後，變數 `fig` 將包含一個設定好的 3D Surface Plotly 圖表物件。
# 你可以接著使用 fig.show() 或 st.plotly_chart(fig) 將其顯示出來。
# 這個圖表通常是互動式的，允許使用者用滑鼠旋轉、縮放和平移 3D 視角。

# --- 4. 在 Streamlit 中顯示 ---
st.plotly_chart(fig)