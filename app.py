import streamlit as st

pg = st.navigation([
    st.Page('_pages/generate_upn_xml.py', title="Generate UPN XML"),
    st.Page('_pages/retreive_meter_readings.py', title="Meter readings"),
    st.Page('_pages/priloga_a.py', title="Priloga A"),
    st.Page('_pages/priloga_b.py', title="Priloga A test"),
    st.Page('_pages/json_dist.py', title="Json to distribution"),
])

pg.run()