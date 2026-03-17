import streamlit as st
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO
# import base64
# import pandas as pd
# import google.generativeai as genai

def tab_1():
    st.header("Dashboard")
    # Define the URL of the MongoDB Charts dashboard
    dashboard_url = "https://charts.mongodb.com/charts-endgame-udptdl-dpsfqqx/public/dashboards/1e47a8d3-fdbd-4ccd-a0a4-7e5a39b2d1c8"

    # Embed the dashboard using an iframe
    width = 1550
    height = 1630
    st.components.v1.html(
        f"""
        <iframe
            src="{dashboard_url}"
            width={width}
            height={height}
        </iframe>
        """,    
        scrolling=False,
        width=width,
        height=height,  # Adjust the height to fit your needs
    )
