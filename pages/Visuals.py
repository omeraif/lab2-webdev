import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Visualizations", page_icon="📈")

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data.csv"
JSON_PATH = BASE_DIR / "data.json"

st.title("Study Habits Visualizations 📈")
st.write("This page includes 3 different graphs: 1 static graph and 2 dynamic graphs using both CSV and JSON data.")

# DATA LOADING
csv_df = pd.DataFrame()
json_data = {}

try:
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
        csv_df = pd.read_csv(CSV_PATH)
        if "study_hours" in csv_df.columns:
            csv_df["study_hours"] = pd.to_numeric(csv_df["study_hours"], errors="coerce")
except Exception as e:
    st.error(f"Could not load CSV data: {e}")

try:
    if JSON_PATH.exists() and JSON_PATH.stat().st_size > 0:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)
except Exception as e:
    st.error(f"Could not load JSON data: {e}")

st.divider()
st.header("Graph 1: Average Study Hours by Place (Static Bar Chart)")
if not csv_df.empty and {"study_place", "study_hours"}.issubset(csv_df.columns):
    static_df = csv_df.groupby("study_place", as_index=True)["study_hours"].mean().sort_values(ascending=False)
    st.bar_chart(static_df)
    st.write("This static graph shows the average number of study hours for each study location using the CSV data.")
else:
    st.warning("CSV data is missing columns needed for the static graph.")

st.divider()
st.header("Graph 2: Filtered Student Study Hours (Dynamic CSV Graph)")

if "csv_selected_place" not in st.session_state:
    st.session_state.csv_selected_place = "All"
if "csv_min_hours" not in st.session_state:
    st.session_state.csv_min_hours = 0.0

if not csv_df.empty and {"name", "study_place", "study_hours"}.issubset(csv_df.columns):
    place_options = ["All"] + sorted(csv_df["study_place"].dropna().astype(str).unique().tolist())

    selected_place = st.selectbox(
        "Choose a study place", place_options, index=place_options.index(st.session_state.csv_selected_place) if st.session_state.csv_selected_place in place_options else 0
    )  #NEW
    min_hours = st.slider(
        "Choose the minimum study hours", 0.0, float(csv_df["study_hours"].max()), float(st.session_state.csv_min_hours), 0.5
    )  #NEW

    if st.button("Update CSV Graph"):  #NEW
        st.session_state.csv_selected_place = selected_place
        st.session_state.csv_min_hours = min_hours

    filtered_df = csv_df.copy()
    if st.session_state.csv_selected_place != "All":
        filtered_df = filtered_df[filtered_df["study_place"] == st.session_state.csv_selected_place]
    filtered_df = filtered_df[filtered_df["study_hours"] >= st.session_state.csv_min_hours]

    if not filtered_df.empty:
        graph_df = filtered_df.set_index("name")["study_hours"]
        st.bar_chart(graph_df)
        st.write("Use the place selector and minimum-hours slider to change which student responses appear.")
        st.metric("Average hours shown", round(filtered_df["study_hours"].mean(), 2))
        st.metric("Median hours shown", round(filtered_df["study_hours"].median(), 2))
    else:
        st.info("No CSV rows match the current filters.")
else:
    st.warning("CSV data is missing columns needed for the dynamic graph.")

st.divider()
st.header("Graph 3: Interactive JSON Data Explorer (Dynamic JSON Graph)")

if "json_dataset" not in st.session_state:
    st.session_state.json_dataset = list(json_data.keys())[0] if json_data else ""
if "json_chart_type" not in st.session_state:
    st.session_state.json_chart_type = "Bar Chart"

if json_data:
    dataset_names = list(json_data.keys())
    chosen_dataset = st.selectbox("Choose a JSON dataset", dataset_names, index=dataset_names.index(st.session_state.json_dataset) if st.session_state.json_dataset in dataset_names else 0)  #NEW
    chart_type = st.radio("Choose a chart style", ["Bar Chart", "Line Chart"])  #NEW

    if st.button("Update JSON Graph"):  #NEW
        st.session_state.json_dataset = chosen_dataset
        st.session_state.json_chart_type = chart_type

    current_dict = json_data.get(st.session_state.json_dataset, {})
    json_df = pd.DataFrame(
        {"Category": list(current_dict.keys()), "Value": list(current_dict.values())}
    ).set_index("Category")

    if not json_df.empty:
        if st.session_state.json_chart_type == "Bar Chart":
            st.bar_chart(json_df)
        else:
            st.line_chart(json_df)
        st.write("This graph uses the JSON file. Change the dataset and chart type to explore different summaries.")
        st.metric("Average value shown", round(json_df["Value"].mean(), 2))
        st.metric("Median value shown", round(json_df["Value"].median(), 2))
    else:
        st.info("The selected JSON dataset is empty.")
else:
    st.warning("JSON data could not be loaded.")
