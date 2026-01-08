import streamlit as st

st.title("📍 Station Location Tracker")
st.write("This app will record GPS locations from WhatsApp links.")

name = st.text_input("Enter your name")
if name:
    st.success(f"Hello {name}! App is working.")
