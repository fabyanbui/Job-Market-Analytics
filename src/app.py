import streamlit as st
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO
# import base64
# import pandas as pd
# import google.generativeai as genai
from dashboard import tab_1
from recommendation import tab_2
from chatbot import tab_3
from feature import tab_4

st.set_page_config(layout="wide", page_title="UDPTDLTM Streamlit App")
st.title("Streamlit Deployment")

# Create horizontal tabs
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Recommendation", "Q&A", "Feature"])

# Tab 1: Dashboard
with tab1:
    tab_1()
    
# Tab 2: Chatbot
with tab2:
    tab_2()

# Tab 3: Recommendation
with tab3:
    tab_3()

with tab4:
    tab_4()

# Footer Section
st.markdown("---")
st.subheader("FIT@HCMUS - 21/24 - Intelligent Data Analytics Applications")
st.markdown("""
> - **21120045**: Bùi Hồng Đăng
> - **21120108**: Nguyễn Tiến Nhật  
> - **21120110**: Nguyễn Tấn Phát
> - **21120115**: Nguyễn Trọng Phúc
> - **21120169**: Thái Chí Vỹ
> - **21120201**: Bùi Đình Bảo
""")