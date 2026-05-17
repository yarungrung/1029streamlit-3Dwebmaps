# --- 確保所有必需的函式庫已在檔案頂部匯入 ---
import rioxarray as rxr
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import rasterio
import numpy as np
import os
st.title("Plotly 3D 地圖 (DEM Surface)")
st.header("廬山溫泉一帶 DEM 3D 模型")


# --- 1. 讀取 DEM 檔案 ---
tif_filename = 'dem5m.tif'

# 建立完整的相對路徑
tif_path = os.path.join(os.path.dirname(__file__),tif_filename) 

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
        title="**廬山溫泉一帶 3D 地形圖 (Plotly Interactive)**",
        
        width=600,
        height=600,
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


#旋轉圖
import imageio.v2 as imageio

st.title("3D 地形動態旋轉展示")

# 1. 讀取你的 DEM 檔案 (沿用之前的成功設定)
tif_filename = 'dem5m.tif'
tif_path = os.path.join(os.path.dirname(__file__), tif_filename)

if not os.path.exists(tif_path):
    st.error(f"找不到檔案：{tif_path}")
    st.stop()

# 讀取並適度降採樣（避免資料量太大跑不動，[::5] 代表每5個點抽1個）
data = rxr.open_rasterio(tif_path, masked=True).squeeze()
z_values = data.values[::5, ::5] 

# 2. 建立 Plotly 3D 地形圖
fig = go.Figure(data=[go.Surface(z=z_values, colorscale='Terrain')])

# 設定基礎視覺樣式（隱藏座標軸，讓畫面乾淨）
fig.update_layout(
    title='DEM 3D 旋轉動畫生成中...',
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectratio=dict(x=1, y=1, z=0.3) # 調整 Z 軸可改變地形起伏立體感
    ),
    width=800,
    height=600
)

# 3. 自動生成旋轉畫面並匯出 GIF
output_gif = "dem_rotation.gif"

with st.spinner("正在繪製各角度地圖並合成為 GIF，請稍候..."):
    frames = []
    temp_files = []
    
    # 建立 36 個角度（每 10 度一張，共 360 度完美循環）
    angles = np.arange(0, 360, 10)
    
    for i, angle in enumerate(angles):
        # 將角度轉換為弧度，計算相機的 X, Y 位置實現繞圈旋轉
        rad = np.radians(angle)
        x_eye = 1.5 * np.cos(rad)
        y_eye = 1.5 * np.sin(rad)
        
        # 更新 Plotly 的相機視角 (Camera View)
        fig.update_layout(scene_camera=dict(eye=dict(x=x_eye, y=y_eye, z=1.2)))
        
        # 儲存當前角度的臨時圖片
        temp_filename = f"temp_frame_{i}.png"
        fig.write_image(temp_filename, format="png")
        temp_files.append(temp_filename)
        
        # 讀取圖片存入陣列
        frames.append(imageio.imread(temp_filename))

    # 使用 imageio 將所有圖片打包成 GIF 
    # duration=100 代表每張圖停 100 毫秒（數字越小轉越快），loop=0 代表無限重複撥放
    imageio.mimsave(output_gif, frames, duration=100, loop=0)

    # 清除剛剛產生的幾十張暫存 PNG 圖片，保持資料夾乾淨
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

st.success("🎉 動態 GIF 產出成功！")

# 4. 在 Streamlit 網頁上呈現結果
st.image(output_gif, caption="北北基桃 3D 地形不間斷旋轉圖", use_container_width=True)

# 提供下載按鈕，讓你可以把 GIF 下載回電腦
with open(output_gif, "rb") as file:
    st.download_button(
        label="💾 下載動態 GIF 檔案",
        data=file,
        file_name="mountain_3d_dem.gif",
        mime="image/gif"
    )