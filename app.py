import streamlit as st

# 1. 使用 st.Page() 定義所有頁面
# 注意：st.Page() 會自動尋找 .py 檔案
pages = [
   st.Page("page_home.py", title="專案首頁", icon="🏠"),
   st.Page("page_3dmap-1.py", title="Pydeck 3D互動地圖瀏覽", icon="🌏"),
   st.Page("page_3dmap-2.py", title="Plotly 3D互動地圖瀏覽", icon="ℹ️")
   st.Page("page_3dmap-3.py", title="Plotly 3D互動地圖瀏覽", icon="♨️")
]

# 2. 使用 st.navigation() 建立導覽 (例如在側邊欄)
with st.sidebar:
    st.title("關於我：自我介紹")
    # st.navigation() 會回傳被選擇的頁面
    selected_page = st.navigation(pages)


# 3. 執行被選擇的頁面
selected_page.run()