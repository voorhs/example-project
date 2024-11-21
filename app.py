from io import BytesIO

import streamlit as st

from bear_marriage.data import read_points
from bear_marriage.find_pairs import connect_points
from bear_marriage.plotting_utils import plot_pairs

with st.sidebar:
     st.header("Data Sidebar")
     file: BytesIO = st.file_uploader(label="Upload your data", type="txt")

     if file is not None:
          st.success("Data uploaded successfully!")

st.header("Bear Marriage")

if file is not None:
     st.subheader("Vizualization")
     points = read_points(file)
     pairs = connect_points(points)
     st.write(plot_pairs(pairs))