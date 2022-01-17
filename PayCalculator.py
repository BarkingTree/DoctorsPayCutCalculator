import streamlit as st
from PIL import Image

col1, mid, col2 = st.columns([1,0.25,5])
with col1:
    st.image('https://cdn-images-1.medium.com/max/906/1*dVSDol9pouoO9IX_E_-35Q.png')
with col2:
    st.header('Medics For Pay Restoration')
    st.write('Calculate Your Pay Cut')
