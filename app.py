import base64
import os
import streamlit as st

# --- EN-TÊTE AVEC LOGO LOCAL ---
col_logo, col_titre = st.columns([1, 8])

with col_logo:
  if os.path.exists("logo_smc.png"):
    with open("logo_smc.png", "rb") as f:
      data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{encoded}" width="65"'
        ' style="border-radius: 8px; margin-top: 5px;" />',
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        '<div style="background-color: #002D62; border: 2px solid #E30613;'
        ' border-radius: 10px; text-align: center; padding: 10px; width: 65px;'
        ' box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><span style="color: white;'
        ' font-weight: 900; font-size: 18px;">SMC</span></div>',
        unsafe_allow_html=True,
    )

with col_titre:
  st.markdown(
      "<h1 style='border-bottom: 4px solid #E30613; padding-bottom: 8px;"
      " margin-top: 5px;'>Concours de Pronos - SMC</h1>",
      unsafe_allow_html=True,
  )