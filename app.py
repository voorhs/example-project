from io import BytesIO
from time import perf_counter

import streamlit as st

from bear_marriage.data import read_points
from bear_marriage.find_pairs import connect_points
from bear_marriage.plotting_utils import plot_pairs_plotly, plot_distances

with st.sidebar:
    st.header("Data Sidebar")
    file: BytesIO = st.file_uploader(label="Upload your data", type="txt")

    if file is not None:
        st.success("Data uploaded successfully!")

    method = st.selectbox(
        label="Select method for finding pairs", options=["line", "hull", "both"]
    )
    build = st.button("Find connections")

st.header("Bear Marriage")

if file is not None and build:
    points = read_points(file)
    methods = []
    hull = method in ["both", "hull"]
    line = method in ["both", "line"]
    if hull:
        methods.append("hull")
    if line:
        methods.append("line")
    for meth in methods:
        st.subheader(f"Method: {meth}")
        with st.spinner("Finding connections"):
            begin = perf_counter()
            pairs = connect_points(points, method=meth)
            end = perf_counter()

        st.subheader("Pairs")
        st.info(f"Build in {end-begin:.2f} seconds")
        with st.spinner("Plotting"):
            st.plotly_chart(plot_pairs_plotly(pairs))

        st.subheader("Distances")
        chart, statistics = plot_distances(pairs)
        st.plotly_chart(chart)
        st.subheader("Statistics")
        st.write(statistics)
