import streamlit as st
import csv
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Survey", page_icon="📝")

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data.csv"

st.title("Student Study Habits Survey 📝")
st.write("Fill out the form below to add a response to the CSV file.")

with st.form("study_form"):
    name = st.text_input("Enter your name")
    hours = st.number_input("How many hours do you study per day?", min_value=0.0, max_value=24.0, step=0.5)
    place = st.selectbox("Where do you study the most?", ["Library", "Dorm", "Cafe", "Student Center", "Home", "Other"])
    submitted = st.form_submit_button("Submit")

if submitted:
    if name.strip():
        file_exists = CSV_PATH.exists()
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists or CSV_PATH.stat().st_size == 0:
                writer.writerow(["name", "study_hours", "study_place"])
            writer.writerow([name.strip(), hours, place])
        st.success("Your response has been saved!")
    else:
        st.warning("Please enter your name.")

st.divider()
st.subheader("Current CSV Data")
if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
    df = pd.read_csv(CSV_PATH)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data has been added yet.")
