# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Normalize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

# Logical field mapping
required_logical_fields = {
    "state_of_residence": None,
    "month": None,
    "month_code": None,
    "year_code": None,
    "sex_of_infant": None,
    "births": None
}

# Dynamically match fields
for logical_field in required_logical_fields.keys():
    matches = [col for col in df.columns if logical_field in col]
    if matches:
        required_logical_fields[logical_field] = matches[0]

missing_fields = [k for k, v in required_logical_fields.items() if v is None]

if missing_fields:
    st.error(f"Missing required logical fields: {missing_fields}")
    st.write("Available columns:")
    st.write(df.columns)
    st.stop()

# Rename columns to logical names
df = df.rename(columns={v: k for k, v in required_logical_fields.items()})

# Convert births to numeric
df["births"] = pd.to_numeric(df["births"], errors="coerce")
df = df.dropna(subset=["births"])

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

def multiselect_with_all(label, options):
    options = sorted(options)
    selected = st.sidebar.multiselect(
        label,
        options=["All"] + options,
        default=["All"]
    )
    return selected

month_selection = multiselect_with_all("Select Month", df["month"].dropna().unique())
gender_selection = multiselect_with_all("Select Gender", df["sex_of_infant"].dropna().unique())
state_selection = multiselect_with_all("Select State", df["state_of_residence"].dropna().unique())

# STEP 5 — Filtering Logic
filtered_df = df.copy()

if "All" not in month_selection:
    filtered_df = filtered_df[filtered_df["month"].isin(month_selection)]

if "All" not in gender_selection:
    filtered_df = filtered_df[filtered_df["sex_of_infant"].isin(gender_selection)]

if "All" not in state_selection:
    filtered_df = filtered_df[filtered_df["state_of_residence"].isin(state_selection)]

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# STEP 6 — Aggregation
aggregated_df = (
    filtered_df
    .groupby(["state_of_residence", "sex_of_infant"], as_index=False)["births"]
    .sum()
)

aggregated_df = aggregated_df.sort_values("state_of_residence")

# STEP 7 — Plot
fig = px.bar(
    aggregated_df,
    x="state_of_residence",
    y="births",
    color="sex_of_infant",
    title="Total Births by State and Gender",
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text="Gender",
    xaxis_title="State",
    yaxis_title="Total Births",
    margin=dict(l=40, r=40, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# STEP 8 — Show Filtered Table
display_df = filtered_df.reset_index(drop=True)
st.dataframe(display_df, use_container_width=True)
