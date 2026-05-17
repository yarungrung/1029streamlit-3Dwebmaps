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
st.title("Plotly 3D 地圖 (DEM Surface) - 動態旋轉展示")

# 1. 設定圖資路徑 (採用同目錄讀取法)
tif_filename = 'dem5m.tif'
tif_path = os.path.join(os.path.dirname(__file__), tif_filename)

# 檢查檔案是否存在
if not os.path.exists(tif_path):
    st.error(f"❌ 找不到 DEM 檔案，請確認 {tif_filename} 已上傳至 GitHub 根目錄。")
    st.stop()

try:
    # 2. 讀取 DEM 影像
    # 使用 masked=True 會自動將 NoData 轉為 NaN
    data = rxr.open_rasterio(tif_path, masked=True).squeeze()
    
    # 3. 數據降採樣與安全性清理 (防止 ValueError 的關鍵)
    # [::5, ::5] 代表每 5 個點抽樣 1 個，避免資料量過大導致記憶體溢出
    sampled_data = data.values[::5, ::5]
    
    # 確保資料為 2D 矩陣 (若為 3D 則取第一個波段)
    if len(sampled_data.shape) == 3:
        z_values = sampled_data[0, :, :]
    else:
        z_values = sampled_data
        
    # 將矩陣中的 NaN (空值/無資料區) 替換為 0.0，否則 Plotly 會崩潰
    z_values = np.nan_to_num(z_values, nan=0.0)
    
    st.info(f"📊 成功讀取並清理 DEM 檔案！網格尺寸：{z_values.shape}")

    # 4. 建立 Plotly 3D 地形圖
    fig = go.Figure(data=[go.Surface(z=z_values, colorscale='earth')])

    # 隱藏座標軸，讓畫面聚焦在地形本體，並調整立體感 (z=0.3)
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectratio=dict(x=1, y=1, z=0.3) 
        ),
        width=800,
        height=600,
        margin=dict(l=0, r=0, b=0, t=0) # 移除邊介白邊
    )

    # 5. 生成 360 度旋轉動畫並合成為 GIF
    output_gif = "dem_rotation.gif"

    # 在網頁上顯示載入中的動畫
    with st.spinner("🔄 正在繪製各角度 3D 地圖並合成為動態 GIF，請稍候..."):
        frames = []
        temp_files = []
        
        # 每 10 度擷取一張圖，共 36 張圖組成完美循環
        angles = np.arange(0, 360, 10)
        
        for i, angle in enumerate(angles):
            # 計算相機繞圈旋轉的 X, Y 座標
            rad = np.radians(angle)
            x_eye = 1.5 * np.cos(rad)
            y_eye = 1.5 * np.sin(rad)
            
            # 更新相機視角
            fig.update_layout(scene_camera=dict(eye=dict(x=x_eye, y=y_eye, z=0.9)))
            
            # 輸出暫存圖片 (需依賴 requirements.txt 中的 kaleido)
            temp_filename = f"temp_frame_{i}.png"
            fig.write_image(temp_filename, format="png")
            temp_files.append(temp_filename)
            
            # 讀取圖片存入記憶體
            frames.append(imageio.imread(temp_filename))

        # 打包成無限重複撥放的 GIF (loop=0 代表無限循環)
        # duration=100 代表每張圖停留 100 毫秒，數字越小轉越快
        imageio.mimsave(output_gif, frames, duration=3000, loop=0)

        # 刪除硬碟中的暫存 PNG 檔案，保持環境乾淨
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    st.success("🎉 動態不間斷旋轉 GIF 產出成功！")

    # 6. 呈現成果與下載按鈕
    st.image(output_gif, caption="3D 地形圖的旋轉展示", use_container_width=True)

    # 讀取剛剛做好的 GIF 提供使用者下載
    with open(output_gif, "rb") as file:
        st.download_button(
            label="💾 下載此動態 GIF 檔案",
            data=file,
            file_name="dem_3d_rotation.gif",
            mime="image/gif"
        )

except Exception as e:
    st.error(f"❌ 執行過程中發生錯誤：{e}")
    st.stop()