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