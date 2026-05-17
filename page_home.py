import streamlit as st
from PIL import Image

# 這裡放所有您想在首頁顯示的內容
st.title("歡迎來到我的 3D GIS 專案！")
st.write("這是一個使用 Streamlit 建立的3D互動式地圖應用程式。")


# 直接將 MP4 影片的 URL 傳給 st.video()
#video_url = "https://i.imgur.com/1GoAB0C.mp4"

#st.write(f"正在播放影片： {video_url}")

#st.video(video_url)

# 將上傳的照片叫出並呈現
image = Image.open("41244.jpg")
st.image(image, caption="是作者我本人的照片喔😀", use_container_width=True)

# 直接將 照片的 URL 傳給 st.image()
#image_url = "https://i.imgur.com/uf1T4ND.png"
#st.image(image_url)