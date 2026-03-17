import streamlit as st

# Configure the Streamlit app
st.set_page_config(layout="wide", page_title="MongoDB Dashboard Integration")
st.title("Streamlit Deployment")

# Define the URL of the MongoDB Charts dashboard
dashboard_url = "https://charts.mongodb.com/charts-endgame-udptdl-dpsfqqx/public/dashboards/1e47a8d3-fdbd-4ccd-a0a4-7e5a39b2d1c8"

# Embed the dashboard using an iframe
st.components.v1.html(
    f"""
    <iframe
        src="{dashboard_url}"
        width=1570
        height=1650
    </iframe>
    """,    
    scrolling=False,
    width=1570,
    height=1650,  # Adjust the height to fit your needs
)

# Footer Section
st.subheader("FIT@HCMUS - 21/24 - Intelligent Data Analytics Applications")
st.markdown("""
> - **21120045**: Bùi Hồng Đăng
> - **21120108**: Nguyễn Tiến Nhật  
> - **21120110**: Nguyễn Tấn Phát
> - **21120115**: Nguyễn Trọng Phúc
> - **21120169**: Thái Chí Vỹ
> - **21120201**: Bùi Đình Bảo
""")
